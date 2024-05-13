import os
from datetime import timedelta

import awswrangler as wr
import pendulum
from include.util import task_fail_slack_alert, task_success_slack_alert

from airflow.decorators import dag, task

DAG_OWNER_NAME='operations'
GLUE_DATABASE=os.getenv('GLUE_DATABASE')

local_tz = pendulum.timezone("Australia/Sydney")

default_args = {
    'owner': DAG_OWNER_NAME,
    'start_date': pendulum.datetime(2024,4,8, tz=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@dag(dag_id=os.path.basename(__file__).replace(".pyc", "").replace(".py", ""),
        schedule="0 2 * * *",
        catchup=False,
        tags=['iceberg', 's3', 'maintenance'],
        on_success_callback=task_success_slack_alert,
        on_failure_callback=task_fail_slack_alert,
        default_args=default_args,
)
def iceberg_vacuum():
    """Expiring Iceberg table snapshots
    """

    @task()
    def expire_iceberg_snapshots():
        """Expring Iceberg table snapshots
        """

        query = f"""
            SELECT 
                t.table_name
            FROM information_schema.tables t
            where t.table_schema = '{GLUE_DATABASE}'
                and t.table_type = 'BASE TABLE'
        """
        tables = wr.athena.read_sql_query(
            sql=query,
            database=GLUE_DATABASE,
        )

        for t in tables['table_name']:
            wr.athena.start_query_execution(
                sql=f"vacuum {t}",
                database=GLUE_DATABASE,
                wait=True,
            )

    _ = expire_iceberg_snapshots()

_ = iceberg_vacuum()