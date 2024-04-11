import json

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook

ADZUNA_SEARCH_ENDPOINT = "https://api.adzuna.com/v1/api/jobs/au/search/{page_number}?app_id={app_id}&app_key={app_key}&what={search_content}&results_per_page=50"

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
    
@dag(dag_id='job_listing_processing',
     start_date=pendulum.datetime(2024,4,8, tz='UTC'),
     schedule_interval='0 2 * * *',
     catchup=False,
     owner_links={'admin':'https://airflow.apache.org'})
def job_listing_processing():
    """ELT pipeline for sourcing data engineer job listings from Adzuna API
    """

    @task()
    def get_job_listing(search_content:str) -> list:
        """Get data engineer job listing from Adzuna API

        Args:
            search_content (str): job title to search for

        Returns:
            list: all data engineer job listings
        """
        adzuna_hook = AdzunaHook(conn_id = 'adzuna_conn')
        job_listing = adzuna_hook.get_job_listings(job_title=search_content)

        with open('/opt/job_listing.json', 'w') as f:
            json.dump(job_listing, f)

        return job_listing
    
    get_job_listing(search_content='data%20engineer')

job_listing_processing()