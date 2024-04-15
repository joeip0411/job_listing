import io
import json
import os
import tempfile
from datetime import datetime

import pandas as pd
import pendulum
import requests
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.http.hooks.http import HttpHook
from bs4 import BeautifulSoup
from openai import OpenAI

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
                {"role": "user", "content": "Return 'N/A' if none identified"},
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
    s3_hook = S3Hook(aws_conn_id='aws_custom')

    @task()
    def get_job_listing(search_content:str) -> str:
        """Get data engineer job listing from Adzuna API

        Args:
            search_content (str): job title to search for

        Returns:
            str: key of the blob in s3
        """
        adzuna_hook = AdzunaHook(conn_id = 'adzuna_conn')
        job_listing = adzuna_hook.get_job_listings(job_title=search_content)

        job_listing_df = pd.DataFrame(job_listing).astype('string')

        file_name = 'job_listings.parquet'
        key = datetime.utcnow().strftime('raw/%Y/%m/%d/')+ file_name
        _load_obj_to_s3(file_name = file_name, key = key, obj=job_listing_df)

        return key
    
    @task()
    def get_job_descriptions(key:str)-> str:
        """Get job description for each job

        Returns:
            str: key of the blob in s3
        """
        jobs = pd.read_parquet(_get_obj_from_s3(key=key)) 
        
        urls = jobs['redirect_url'].str.split('?').str[0]

        job_descriptions = []

        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                job_desc = soup.find(class_="adp-body mx-4 mb-4 text-sm md:mx-0 md:text-base md:mb-0").text
            except AttributeError:
                job_desc = ''
            
            job = {'id':url.split('/')[-1], 
                   'desc':job_desc}

            job_descriptions.append(job)
        
        job_descriptions_df = pd.DataFrame(job_descriptions).astype('string')

        file_name = 'job_descriptions.parquet'
        output_key = datetime.utcnow().strftime('raw/%Y/%m/%d/')+ file_name
        _load_obj_to_s3(file_name = file_name, key = output_key, obj=job_descriptions_df)

        return output_key

    def _load_obj_to_s3(file_name:str, key:str, obj:object) -> str:

        file_path = os.path.join(tempfile.gettempdir(), file_name)
        obj.to_parquet(path=file_path)

        key = datetime.utcnow().strftime('raw/%Y/%m/%d/')+ file_name

        if s3_hook.check_for_key(key=key, bucket_name=BUCKET_NAME):
            s3_hook.delete_objects(bucket=BUCKET_NAME, keys=key)
        s3_hook.load_file(filename=file_path, key=key, bucket_name=BUCKET_NAME)

    def _get_obj_from_s3(key:str):
        s3_obj = s3_hook.get_key(key=key,bucket_name=BUCKET_NAME)
        obj = io.BytesIO(s3_obj.get()['Body'].read())
        return obj
    
    @task
    def get_technologies_from_job_description(key:str):
        job_desc = pd.read_parquet(_get_obj_from_s3(key=key)) 

        technologies = []
        chat_completion_hook = ChatCompletionHook(conn_id='openai_conn')

        for i in range(len(job_desc)):
            technology = chat_completion_hook.get_technologies_from_job_desc(job_desc=job_desc.iloc[i,1])
            technologies.append(technology)

        job_desc['technology'] = technologies

        file_name = 'job_descriptions_with_skill.parquet'
        output_key = datetime.utcnow().strftime('raw/%Y/%m/%d/')+ file_name
        _load_obj_to_s3(file_name=file_name, key=output_key, obj=job_desc)

        return output_key


    job_listings = get_job_listing(search_content='data%20engineer')
    job_descriptions = get_job_descriptions(job_listings)
    get_technologies_from_job_description(job_descriptions)


job_listing_processing()