import os

import boto3


def lambda_handler(event, context):
    """Sample pure Lambda function

    """

    client = boto3.client('ecs')
    ecs_service_desired_count = event['desired_count']

    try:
        response = client.update_service(
            cluster = os.getenv('ecs_cluster'),
            service = os.getenv('ecs_airflow_job_listing_service'),
            desiredCount=ecs_service_desired_count,
        )
    except Exception as e:
        print(e)
        raise e
    
    print(response)


    return True
