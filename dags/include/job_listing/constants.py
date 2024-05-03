from pathlib import Path

from cosmos import ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import TestBehavior
from cosmos.profiles import SparkThriftProfileMapping
from pyspark import SparkConf

SPARK_CONF=(
    SparkConf()\
        .setAppName("spark_app")\
        .set("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.5.0,org.apache.iceberg:iceberg-aws-bundle:1.5.0")\
        .set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
        .set("spark.sql.catalog.glue", "org.apache.iceberg.spark.SparkCatalog")\
        .set("spark.sql.catalog.glue.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")\
        .set("spark.sql.catalog.glue.warehouse", "s3://joeip-data-engineering-iceberg-test/")\
        .set("spark.sqk.catalog.glue.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
)
GLUE_CATALOG="glue"
GLUE_DATABASE="job"

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
                    "spark.sql.defaultCatalog=glue",
                    "--conf",
                    "spark.sql.catalog.glue=org.apache.iceberg.spark.SparkCatalog",
                    "--conf",
                    "spark.sql.catalog.glue.warehouse=s3://joeip-data-engineering-iceberg-test/",
                    "--conf",
                    "spark.sql.catalog.glue.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog",
                    "--conf",
                    "spark.sql.catalog.glue.io-impl=org.apache.iceberg.aws.s3.S3FileIO",
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
                "spark.sql.defaultCatalog": "glue",
                "spark.sqk.catalog.glue.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
                "spark.sql.catalog.glue": "org.apache.iceberg.spark.SparkCatalog",
                "spark.sql.catalog.glue.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
                "spark.sql.catalog.glue.warehouse": "s3://joeip-data-engineering-iceberg-test/",
                "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            },
        },
    ],
}

DBT_PROJECT_NAME = "job_listing"
DBT_ROOT_PATH = Path(__file__).parent.parent.parent / "dbt"
DBT_PROJECT_CONFIG = ProjectConfig(dbt_project_path= DBT_ROOT_PATH / DBT_PROJECT_NAME)
DBT_PROFILE_CONFIG = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=SparkThriftProfileMapping(
        conn_id="dbt_conn",
        profile_args={"user": "hadoop",
                        "schema": "job",
                        "threads": 4},
    ),
)
DBT_EXECUTION_CONFIG=ExecutionConfig(
        dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
    )

DBT_RENDER_CONFIG=RenderConfig(
    test_behavior=TestBehavior.AFTER_ALL,
    select=[DBT_PROJECT_NAME],
)