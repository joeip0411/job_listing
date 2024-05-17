import os
from pathlib import Path

from cosmos import ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import TestBehavior
from cosmos.profiles import SparkThriftProfileMapping
from pyspark import SparkConf

GLUE_CATALOG = os.getenv('GLUE_CATALOG')
GLUE_DATABASE = os.getenv('GLUE_DATABASE')
GLUE_DATABASE_STORAGE_LOCATION = os.getenv('GLUE_DATABASE_STORAGE_LOCATION')
STAGE = os.getenv('STAGE')

SPARK_CONF=(
    SparkConf()\
        .setAppName("spark_app")\
        .set("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.5.0,org.apache.iceberg:iceberg-aws-bundle:1.5.0")\
        .set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
        .set(f"spark.sql.catalog.{GLUE_CATALOG}", "org.apache.iceberg.spark.SparkCatalog")\
        .set(f"spark.sql.catalog.{GLUE_CATALOG}.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")\
        .set(f"spark.sql.catalog.{GLUE_CATALOG}.warehouse", GLUE_DATABASE_STORAGE_LOCATION)\
        .set(f"spark.sqk.catalog.{GLUE_CATALOG}.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
)

EMR_JOB_FLOW_OVERRIDES = {
    "Name": "dbt_spark_cluster",
    "LogUri":"s3n://aws-logs-654654412098-ap-southeast-2/elasticmapreduce/",
    "ReleaseLabel": "emr-6.15.0",
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "primary",
                "InstanceRole": "MASTER",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 1,
                "Market": "SPOT",
            },
        ],

        "EmrManagedMasterSecurityGroup": "sg-0cb660a18340f7dd3",
        "EmrManagedSlaveSecurityGroup": "sg-022b94e344b317380",

        "KeepJobFlowAliveWhenNoSteps": True,
        "Ec2SubnetId": "subnet-00db28f8b82b2d34f",
    },
    "Steps": [
        {
            "Name": "Start Thrift Server",
            "ActionOnFailure":"CONTINUE",
            "HadoopJarStep":{
                "Jar":"command-runner.jar",
                "Args":[
                    "sudo", 
                    "/usr/lib/spark/sbin/start-thriftserver.sh",
                    "--conf",
                    "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                    "--conf",
                    f"spark.sql.defaultCatalog={GLUE_CATALOG}",
                    "--conf",
                    f"spark.sql.catalog.{GLUE_CATALOG}=org.apache.iceberg.spark.SparkCatalog",
                    "--conf",
                    f"spark.sql.catalog.{GLUE_CATALOG}.warehouse={GLUE_DATABASE_STORAGE_LOCATION}",
                    "--conf",
                    f"spark.sql.catalog.{GLUE_CATALOG}.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog",
                    "--conf",
                    f"spark.sql.catalog.{GLUE_CATALOG}.io-impl=org.apache.iceberg.aws.s3.S3FileIO",
                ],
            },
        },
],
    "ServiceRole": "EMR-service-role",
    "JobFlowRole": "EMR-EC2-instance-profile",
    "Applications": [
        {"Name": "Hadoop"},
        {"Name": "Hive"},
        {"Name": "JupyterEnterpriseGateway"},
        {"Name": "Livy"},
        {"Name": "Spark"},
    ],
    "Configurations": [
        {
            "Classification": "iceberg-defaults",
            "Properties": {
                "iceberg.enabled": "true",
            },
        },
        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.sql.defaultCatalog": GLUE_CATALOG,
                f"spark.sqk.catalog.{GLUE_CATALOG}.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
                f"spark.sql.catalog.{GLUE_CATALOG}": "org.apache.iceberg.spark.SparkCatalog",
                f"spark.sql.catalog.{GLUE_CATALOG}.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
                f"spark.sql.catalog.{GLUE_CATALOG}.warehouse": GLUE_DATABASE_STORAGE_LOCATION,
                "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            },
        },
    ],
}

DBT_PROJECT_NAME = "job_listing"
DBT_ROOT_PATH = Path(__file__).parent.parent.parent / "dbt"
DBT_PROJECT_CONFIG = ProjectConfig(
    dbt_project_path= DBT_ROOT_PATH / DBT_PROJECT_NAME,
    env_vars={
        "GLUE_DATABASE":GLUE_DATABASE,
        })
DBT_PROFILE_CONFIG = ProfileConfig(
    profile_name="default",
    target_name=os.getenv('STAGE'),
    profile_mapping=SparkThriftProfileMapping(
        conn_id="dbt_conn",
        profile_args={
            "user": "hadoop",
            "schema": GLUE_DATABASE,
            "threads": 4,
            },
    ),
)
DBT_EXECUTION_CONFIG=ExecutionConfig(
        dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
    )

DBT_RENDER_CONFIG=RenderConfig(
    test_behavior=TestBehavior.AFTER_ALL,
    select=[DBT_PROJECT_NAME],
)