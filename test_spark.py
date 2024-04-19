import time

import boto3
import pyspark
from pyspark.sql import SparkSession

# pyspark==3.4.1
# "glue" below can be anything
conf = (
    pyspark.SparkConf()\
    .setAppName('app_name')\
    .set('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.5.0,org.apache.iceberg:iceberg-aws-bundle:1.5.0')\
    .set('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions')\
    .set('spark.sql.catalog.glue', 'org.apache.iceberg.spark.SparkCatalog')\
    .set('spark.sql.catalog.glue.catalog-impl', 'org.apache.iceberg.aws.glue.GlueCatalog')\
    .set('spark.sql.catalog.glue.warehouse', 's3://joeip-data-engineering-iceberg-test/')\
    .set('spark.sqk.catalog.glue.io-impl', 'org.apache.iceberg.aws.s3.S3FileIO')
)

spark = SparkSession.builder.config(conf=conf).getOrCreate()

spark.sql(
    """create database glue.test
    """,
)

spark.sql(
    """
    create table if not exists glue.test.sales
    (id string, name string, product string, price string, date string) using iceberg
    """,
)

data = [("John", 30), ("Alice", 25), ("Bob", 35)]
df = spark.createDataFrame(data)

df.write.format('iceberg')\
    .mode('overwrite')\
    .saveAsTable('glue.test.person')

spark.sql("select * from glue.test.person").show()

##############################
#EMR

session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name='ap-southeast-2',
)

emr_client = session.client('emr')


response = emr_client.run_job_flow(
    Name = 'my_boto_cluster',
    LogUri = 's3n://aws-logs-654654412098-ap-southeast-2/elasticmapreduce/',
    ReleaseLabel = 'emr-6.15.0',
    Instances = {
        'InstanceGroups': [
            {
                'Name': 'primary',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
                'Market': 'SPOT',
            },
            {
                'Name': 'core',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
                'Market': 'SPOT',
            }
        ],

        "EmrManagedMasterSecurityGroup": 'sg-0cb660a18340f7dd3',
        "EmrManagedSlaveSecurityGroup": 'sg-022b94e344b317380',

        "KeepJobFlowAliveWhenNoSteps": True,
        'Ec2SubnetId': 'subnet-00db28f8b82b2d34f',
    },
    Steps=[
        {
            'Name': 'Start Thrift Server',
            'ActionOnFailure':'CONTINUE',
            'HadoopJarStep':{
                'Jar':'command-runner.jar',
                'Args':[
                    'sudo', 
                    '/usr/lib/spark/sbin/start-thriftserver.sh',
                    '--conf',
                    'spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions',
                    '--conf',
                    'spark.sql.defaultCatalog=glue',
                    '--conf',
                    'spark.sql.catalog.glue=org.apache.iceberg.spark.SparkCatalog',
                    '--conf',
                    'spark.sql.catalog.glue.warehouse=s3://joeip-data-engineering-iceberg-test/',
                    '--conf',
                    'spark.sql.catalog.glue.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog',
                    '--conf',
                    'spark.sql.catalog.glue.io-impl=org.apache.iceberg.aws.s3.S3FileIO',
                ],
            },
        },
    ],
    ServiceRole='EMR-service-role',
    JobFlowRole='EMR-EC2-instance-profile',
    Applications=[
        {'Name': 'Hadoop'},
        {'Name': 'Hive'},
        {'Name': 'JupyterEnterpriseGateway'},
        {'Name': 'Livy'},
        {'Name': 'Spark'},
    ],
    Configurations= [
        {
            "Classification": "iceberg-defaults",
            "Properties": {
                "iceberg.enabled": "true",
            },
        },
        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.sqk.catalog.glue.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
                "spark.sql.catalog.glue": "org.apache.iceberg.spark.SparkCatalog",
                "spark.sql.catalog.glue.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
                "spark.sql.catalog.glue.warehouse": "s3://joeip-data-engineering-iceberg-test/",
                "spark.sql.defaultCatalog": "glue",
                "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            },
        },
    ],
)

cluster_id = response['JobFlowId']

cluster_details = emr_client.describe_cluster(ClusterId=cluster_id)
cluster_status = response['Cluster']['Status']['State']

while True:
    response = emr_client.describe_cluster(ClusterId=cluster_id)
    cluster_status = response['Cluster']['Status']['State']

    if cluster_status == 'STARTING':
        time.sleep(60)
    elif cluster_status == 'WAITING':
        break
    elif cluster_status == 'TERMINATED':
        raise RuntimeError
    
cluster_details = emr_client.describe_cluster(ClusterId = cluster_id)
host_name = cluster_details['Cluster']['MasterPublicDnsName']