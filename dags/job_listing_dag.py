import json

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook
from bs4 import BeautifulSoup
from openai import OpenAI
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

ADZUNA_SEARCH_ENDPOINT = "https://api.adzuna.com/v1/api/jobs/au/search/{page_number}?app_id={app_id}&app_key={app_key}&what={search_content}&results_per_page=50"
BUCKET_NAME = 'joeip-data-engineering-job-listing'
class AdzunaHook(HttpHook):
    """Interacts with Adzuna job listing API
    application id and secret in "adzuna_conn"
    """

    def __init__(self, conn_id:str):
        """Adzuna API Wrapper Hook

        Args:
            conn_id (str): Airflow connection id to obtain application name and key
        """
        self.conn_id = conn_id
        self.connection = self.get_connection(self.conn_id)
        self.app_id = self.connection.extra_dejson.get('application_id')
        self.app_key = self.connection.extra_dejson.get('application_password')

    def get_job_listings(self, job_title:str) -> dict:
        """Get all job listing of a job title

        Args:
            job_title (str): job title to search

        Returns:
            dict: all job listings
        """
        all_result = []
        page_number = 1

        while True:
            endpoint = ADZUNA_SEARCH_ENDPOINT.format(page_number=page_number, 
                                                    app_id=self.app_id, 
                                                    app_key=self.app_key,
                                                    search_content=job_title)
            response = requests.get(endpoint)
            result = json.loads(response.text)['results']
            if len(result) > 0:
                all_result += result
                page_number += 1
            else:
                break

        return all_result

class ChatCompletionHook(HttpHook):
    """Interacts with OpenAI Chat Completion API
    api secret in "openai_conn"
    """
        
    def __init__(self, conn_id:str):
        """Open AI Chat Completion Hook

        Args:
            conn_id (str): Airflow connection id to obtain api secret
        """
        self.conn_id = conn_id
        self.connection = self.get_connection(self.conn_id)
        self.api_key = self.connection.password

    def get_technologies_from_job_desc(self, job_desc:str) -> str:
        """Extract technologies required from job description

        Args:
            job_desc (str): job description

        Returns:
            str: technologies delimited by " | "
        """
        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages = [
                {"role": "system", "content": "You are a helpful technology assistant who is aware of all cloud services and technology used for software development and data processing"},
                {"role": "user", "content": "Find all the cloud services and technology required for the job descripton provided"},
                {"role": "user", "content": "If the technology / cloud service identified is not the official name of the product, return the official name"},
                {"role": "user", "content": "Remove duplicates if there are any"},
                {"role": "user", "content": "Return an empty string if none identified"},
                {"role": "user", "content": "Return the result delimited by ' | '"},
                {"role": "user", "content": "Job description: \n" + job_desc},
            ],
            temperature=0.2,

        )
        content = response.choices[0].message.content
        return content

    
@dag(dag_id='job_listing_processing',
     start_date=pendulum.datetime(2024,4,8, tz='UTC'),
     schedule_interval='0 2 * * *',
     catchup=False,
     owner_links={'admin':'https://airflow.apache.org'})
def job_listing_processing():
    """ELT pipeline for sourcing data engineer job listings from Adzuna API
    """

    conf = (
        SparkConf()\
            .setAppName('app_name')\
            .set('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.5.0,org.apache.iceberg:iceberg-aws-bundle:1.5.0')\
            .set('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions')\
            .set('spark.sql.catalog.glue', 'org.apache.iceberg.spark.SparkCatalog')\
            .set('spark.sql.catalog.glue.catalog-impl', 'org.apache.iceberg.aws.glue.GlueCatalog')\
            .set('spark.sql.catalog.glue.warehouse', 's3://joeip-data-engineering-iceberg-test/')\
            .set('spark.sqk.catalog.glue.io-impl', 'org.apache.iceberg.aws.s3.S3FileIO')
    )

    catalog = 'glue'
    database = 'job'

    @task()
    def get_job_listing(search_content:str) -> str:
        """Get data engineer job listing from Adzuna API

        Args:
            search_content (str): job title to search for

        Returns:
            str: output table name
        """
        table_name = f'{catalog}.{database}.stg__job_listing'

        spark = SparkSession.builder.config(conf=conf).getOrCreate()

        adzuna_hook = AdzunaHook(conn_id = 'adzuna_conn')
        job_listing = adzuna_hook.get_job_listings(job_title=search_content)

        schema = StructType([
            StructField("description", StringType(), True),
            StructField("id", StringType(), True),
            StructField("location", StringType(), True),
            StructField("redirect_url", StringType(), True),
            StructField("salary_is_predicted", StringType(), True),
            StructField("company", StringType(), True),
            StructField("__CLASS__", StringType(), True),
            StructField("adref", StringType(), True),
            StructField("category", StringType(), True),
            StructField("created", StringType(), True),
            StructField("title", StringType(), True),
            StructField("latitude", FloatType(), True),
            StructField("salary_min", IntegerType(), True),
            StructField("longitude", FloatType(), True),
            StructField("contract_time", StringType(), True),
            StructField("salary_max", IntegerType(), True),
            StructField("contract_type", StringType(), True),
        ])

        job_listing_df = spark.createDataFrame(job_listing, schema=schema)
        job_listing_df = job_listing_df.withColumn('extraction_time_utc', current_timestamp())

        job_listing_df.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name
    
    @task()
    def get_job_descriptions(input_table:str)-> str:
        """Get job description for each job

        Returns:
            str: output table name
        """

        spark = SparkSession.builder.config(conf=conf).getOrCreate()

        sdf = spark.sql(f"""
                select
                    split(redirect_url, '\\\?')[0] as redirect_url
                from {input_table};
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
            StructField("id", StringType(), True),
            StructField("full_description", StringType(), True),

        ])

        job_desc_df = spark.createDataFrame(job_descriptions, schema=schema)
        job_desc_df = job_desc_df.withColumn('extraction_time_utc', current_timestamp())

        table_name = f'{catalog}.{database}.stg__job_description'
        job_desc_df.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name

    @task
    def get_technologies_from_job_description(input_table:str) -> str:
        """Get technology/skills required for each job

        Returns:
            str: output table name
        """
        spark = SparkSession.builder.config(conf=conf).getOrCreate()

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

        table_name = f'{catalog}.{database}.stg__job_skills'
        job_skills.write.format('iceberg')\
            .mode('overwrite')\
            .saveAsTable(table_name)

        return table_name

    job_listings = get_job_listing(search_content='data%20engineer')
    job_descriptions = get_job_descriptions(job_listings)
    get_technologies_from_job_description(job_descriptions)

job_listing_processing()