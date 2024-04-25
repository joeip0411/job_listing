import json

import requests
from airflow.providers.http.hooks.http import HttpHook
from openai import OpenAI


class AdzunaHook(HttpHook):
    """Interacts with Adzuna job listing API
    application id and secret in "adzuna_conn"
    """
    ADZUNA_SEARCH_ENDPOINT = "https://api.adzuna.com/v1/api/jobs/au/search/{page_number}?app_id={app_id}&app_key={app_key}&what={search_content}&results_per_page=50"

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
            endpoint = self.ADZUNA_SEARCH_ENDPOINT.format(page_number=page_number, 
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
                {"role": "user", "content": "Remove duplicates if there are any"},
                {"role": "user", "content": "Return an empty string if none identified"},
                {"role": "user", "content": "Return the result delimited by ' | '"},
                {"role": "user", "content": "Job description: \n" + job_desc},
            ],
            temperature=0.2,

        )
        content = response.choices[0].message.content
        return content