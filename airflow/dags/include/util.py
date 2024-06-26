import uuid

from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
from airflow.utils.state import State

ICON_URL = 'https://raw.githubusercontent.com/apache/airflow/main/airflow/www/static/pin_100.png'

def task_fail_slack_alert(context):
    """Slack notification on task failure
    """
    tis_dagrun = context['ti'].get_dagrun().get_task_instances()
    failed_tasks = [f"<{ti.log_url}|{ti.task_id}>" for ti in tis_dagrun if ti.sttate == State.FAILED]
    
    dag=context.get('task_instance').dag_id
    exec_date=context.get('execution_date')

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":red_circle: Dag Failed.",
            },
        },
        {
            "type": "section",
            "block_id": f"section{uuid.uuid4()}",
            "text": {
                "type": "mrkdwn",
                "text": f"*Dag*: {dag} \n *Execution Time*: {exec_date}",
            },
            "accessory": {
                "type": "image",
                "image_url": ICON_URL,
                "alt_text": "Airflow",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Failed Tasks: {', '.join(failed_tasks)}",
            },
        },
    ]
    failed_alert = SlackWebhookHook(
        http_conn_id='slack_conn',
        channel="#airflow-notifications",    
        blocks=blocks,
        username='airflow',
    )
    failed_alert.execute()
    return 


def task_success_slack_alert(context):
    """Slack notification on DAG run success
    """
    dag=context.get('task_instance').dag_id
    exec_date=context.get('execution_date')

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":large_green_circle: Dag Succeed.",
            },
        },
        {
            "type": "section",
            "block_id": f"section{uuid.uuid4()}",
            "text": {
                "type": "mrkdwn",
                "text": f"*Dag*: {dag} \n *Execution Time*: {exec_date}",
            },
            "accessory": {
                "type": "image",
                "image_url": ICON_URL,
                "alt_text": "Airflow",
            },
        },
    ]
    success_alert = SlackWebhookHook(
        http_conn_id='slack_conn',
        channel="#airflow-notifications",    
        blocks=blocks,
        username='airflow',
    )
    success_alert.execute()
    return 