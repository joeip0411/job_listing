import logging
import os
import time

import pendulum
import requests
from bs4 import BeautifulSoup
from cosmos import DbtTaskGroup
from include.job_listing.constants import (
    DBT_EXECUTION_CONFIG,
    DBT_PROFILE_CONFIG,
    DBT_PROJECT_CONFIG,
    DBT_RENDER_CONFIG,
    EMR_JOB_FLOW_OVERRIDES,
    GLUE_CATALOG,
    GLUE_DATABASE,
    SPARK_CONF,
)
from include.job_listing.hooks import AdzunaHook, ChatCompletionHook
from include.util import task_fail_slack_alert, task_success_slack_alert
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from airflow import settings
from airflow.decorators import dag, task
from airflow.models import Connection
from airflow.providers.amazon.aws.hooks.emr import EmrHook

local_tz = pendulum.timezone("Australia/Sydney")

default_args = {
    'owner': 'engineering',
    'start_date': pendulum.datetime(2024,4,8, tz=local_tz),
}

@dag(dag_id=os.path.basename(__file__).replace(".pyc", "").replace(".py", ""),
     schedule="0 2 * * *",
     catchup=False,
     tags=['ELT'],
     default_args=default_args,
     on_failure_callback=task_fail_slack_alert,
     on_success_callback=task_success_slack_alert,
     params={
         'spark_conf':SPARK_CONF,
         'catalog':GLUE_CATALOG,
         'database':GLUE_DATABASE,
     },
)
def job_listing_processing():
    """ELT pipeline for sourcing data engineer job listings from Adzuna API
    """

    # conf = SPARK_CONF
    # catalog = GLUE_CATALOG
    # database = GLUE_DATABASE

    @task()
    def get_job_listing(search_content:str, **context) -> str:
        """Get data engineer job listing from Adzuna API

        Args:
            search_content (str): job title to search for

        Returns:
            str: output table name
        """
        catalog = context['params']['catalog']
        database = context['params']['database']
        table_name = f'{catalog}.{database}.stg__job_listing'

        spark_conf=context['params']['spark_conf']
        spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()

        adzuna_hook = AdzunaHook(conn_id = 'adzuna_conn')
        job_listing = adzuna_hook.get_job_listings(job_title=search_content)

        schema = StructType([
            StructField(name="description", dataType=StringType(), nullable=True),
            StructField(name="id", dataType=StringType(), nullable=True),
            StructField(name="location", dataType=StringType(), nullable=True),
            StructField(name="redirect_url", dataType=StringType(), nullable=True),
            StructField(name="salary_is_predicted", dataType=StringType(), nullable=True),
            StructField(name="company", dataType=StringType(), nullable=True),
            StructField(name="__CLASS__", dataType=StringType(), nullable=True),
            StructField(name="adref", dataType=StringType(), nullable=True),
            StructField(name="category", dataType=StringType(), nullable=True),
            StructField(name="created", dataType=StringType(), nullable=True),
            StructField(name="title", dataType=StringType(), nullable=True),
            StructField(name="latitude", dataType=FloatType(), nullable=True),
            StructField(name="salary_min", dataType=IntegerType(), nullable=True),
            StructField(name="longitude", dataType=FloatType(), nullable=True),
            StructField(name="contract_time", dataType=StringType(), nullable=True),
            StructField(name="salary_max", dataType=IntegerType(), nullable=True),
            StructField(name="contract_type", dataType=StringType(), nullable=True),
        ])

        job_listing_df = spark.createDataFrame(job_listing, schema=schema)
        job_listing_df = job_listing_df.withColumn('extraction_time_utc', current_timestamp())

        job_listing_df.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name
    
    @task()
    def get_job_descriptions_from_listing(input_table:str, **context)-> str:
        """Get job description for each job

        Returns:
            str: output table name
        """
        spark_conf=context['params']['spark_conf']
        catalog=context['params']['catalog']
        database=context['params']['database']

        spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()

        sdf = spark.sql(f"""
                select
                    split(redirect_url, '\\\?')[0] as redirect_url
                from {input_table}
                where id not in (select id from {catalog}.{database}.brz__job_description);
            """)
        
        urls = [str(row.redirect_url) for row in sdf.collect()]

        job_descriptions = []

        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                job_desc = soup.find(class_="adp-body mx-4 mb-4 text-sm md:mx-0 md:text-base md:mb-0").text
            except AttributeError:
                job_desc = ''
            
            job = {'id':url.split('/')[-1], 
                   'full_description':job_desc}

            job_descriptions.append(job)
        
        schema = StructType([
            StructField(name="id", dataType=StringType(), nullable=True),
            StructField(name="full_description", dataType=StringType(), nullable=True),

        ])

        job_desc_df = spark.createDataFrame(job_descriptions, schema=schema)
        job_desc_df = job_desc_df.withColumn('extraction_time_utc', current_timestamp())

        table_name = f'{catalog}.{database}.stg__job_description'
        job_desc_df.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name

    @task
    def get_skills_from_job_description(input_table:str, **context) -> str:
        """Get technology/skills required for each job

        Returns:
            str: output table name
        """
        spark_conf=context['params']['spark_conf']
        spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()

        job_description = spark.sql(
            f"""
                select
                    id,
                    full_description
                from {input_table}
            """)

        desc = [((row.id, row.full_description)) for row in job_description.collect()]

        technologies = []
        chat_completion_hook = ChatCompletionHook(conn_id='openai_conn')

        for i in range(len(desc)):
            technology = chat_completion_hook.get_technologies_from_job_desc(job_desc=desc[i][1])
            technologies.append(technology)

        job_skills = [(desc[i][0], technologies[i]) for i in range(len(desc))]
        columns = ['id', 'skill']

        job_skills = spark.createDataFrame(job_skills, columns)
        job_skills = job_skills.withColumn('extraction_time_utc', current_timestamp())

        catalog = context['params']['catalog']
        database = context['params']['database']

        table_name = f'{catalog}.{database}.stg__job_skills'
        job_skills.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name
    
    @task(multiple_outputs=True)
    def start_emr_cluster():
        emr_hook = EmrHook(aws_conn_id='aws_custom')
        emr_client = emr_hook.get_conn()

        response = emr_client.run_job_flow(
            Name=EMR_JOB_FLOW_OVERRIDES['Name'],
            LogUri=EMR_JOB_FLOW_OVERRIDES['LogUri'],
            ReleaseLabel=EMR_JOB_FLOW_OVERRIDES['ReleaseLabel'],
            Instances=EMR_JOB_FLOW_OVERRIDES['Instances'],
            Steps=EMR_JOB_FLOW_OVERRIDES['Steps'],
            ServiceRole=EMR_JOB_FLOW_OVERRIDES['ServiceRole'],
            JobFlowRole=EMR_JOB_FLOW_OVERRIDES['JobFlowRole'],
            Applications=EMR_JOB_FLOW_OVERRIDES['Applications'],
            Configurations=EMR_JOB_FLOW_OVERRIDES['Configurations'],
        )
        logging.info(response)

        cluster_id = response['JobFlowId']
        
        while True:
            response = emr_client.describe_cluster(ClusterId=cluster_id)
            cluster_status = response['Cluster']['Status']['State']

            if cluster_status == 'STARTING' or cluster_status == 'RUNNING':
                time.sleep(60)
            elif cluster_status == 'WAITING':
                break
            else:
                raise RuntimeError
        
        master_public_dns = response['Cluster']['MasterPublicDnsName']

        return {"cluster_id":cluster_id, "master_public_dns":master_public_dns}
    
    @task
    def upsert_dbt_conn(master_public_dns:str):
        """update host of dbt conn to connect to EMR cluster

        Args:
            master_public_dns (str): primary node public DNS
        """

        conn = Connection(
            conn_id='dbt_conn',
            conn_type='generic',
            host=master_public_dns,
            login='hadoop',
            port=10001,
        )
        session = settings.Session()
        existing_conn = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()

        if str(existing_conn) == str(conn.conn_id):
            session.delete(existing_conn)
            session.commit()
            logging.info('Existing dbt connection deleted')

        session.add(conn)
        session.commit()
        logging.info('New dbt connection added')

        return conn

    dbt_task_group = DbtTaskGroup(
        group_id="job_listing_transformation",
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_PROFILE_CONFIG,
        execution_config=DBT_EXECUTION_CONFIG,
        render_config=DBT_RENDER_CONFIG,
        operator_args={
            "install_deps": True,
        },

    )

    @task
    def terminate_emr_cluster(cluster_id:str):
        emr_hook = EmrHook(aws_conn_id='aws_custom')
        emr_client = emr_hook.get_conn()

        response = emr_client.terminate_job_flows(
            JobFlowIds=[
                cluster_id,
            ],
        )
        return response


    job_listings = get_job_listing(search_content='data%20engineer')
    job_descriptions = get_job_descriptions_from_listing(job_listings)
    job_skills = get_skills_from_job_description(job_descriptions)
    emr_details = start_emr_cluster()

    job_listings >> job_descriptions >> job_skills >> dbt_task_group
    
    emr_details >> upsert_dbt_conn(master_public_dns=emr_details['master_public_dns']) >> dbt_task_group >> terminate_emr_cluster(cluster_id=emr_details['cluster_id'])
    
_ = job_listing_processing()