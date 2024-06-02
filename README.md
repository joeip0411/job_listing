<a name="readme-top"></a>

<br />
<div align="center">

  <h1 align="center">Job Listing Data Curation</h1>

  <p align="center">
    <br />
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


Traditional job searching platforms often lack advanced filtering options, such as filtering jobs by date posted or searching jobs by specific skills. Moreover, crucial information is typically embedded within the job description as free text, making it challenging to conduct meaningful analytics.

The motivation behind this project stems from the need to empower job seekers with comprehensive and actionable insights into the job market. By overcoming the shortcomings of existing job searching platforms, we enable candidates to make more informed decisions about their career paths. This includes understanding current market conditions, gaining insights into salary ranges for specific roles, and identifying in-demand technologies to enhance their skill sets.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

* [![airflow-badge]][airflow-url]
* [![iceberg-badge]][iceberg-url]
* [![spark-badge]][spark-url]
* [![dbt-badge]][dbt-url]
* [![docker-badge]][docker-url]
* [![github-action-badge]][github-action-url]
* [![powerbi-badge]][powerbi-url]
* [![terraform-badge]][terraform-url]


### Architecture Diagram
![plot](./ArchitectureDiagram.png)
### Data Model
![plot](./DataModel.png)
### Power BI Report
![plot](./PowerBIReport.png)
![plot](./PowerBIReport_Details.png)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites


- **Docker**
Install Docker Desktop: https://docs.docker.com/desktop/install/ubuntu/

- **Terraform**
Install Terraform : https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

- **AWS CLI**
Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

- **Adzuna API**
Create an account and obtain a free API key from Adzuna: https://developer.adzuna.com/

- **Open AI API**
Create an account and generate an API key from Open AI: https://platform.openai.com/

- **Slack Webhook URL**
Create an account and incoming webhook: https://api.slack.com/messaging/webhooks

### Local Installation

1. Create an .env file at the root directory of the project
```yaml
# .env
AIRFLOW_BASE_URL=http://localhost:8080
AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
AWS_DEFAULT_REGION=<your_aws_region>
AWS_REGION=<your_aws_region>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
ENABLE_REMOTE_LOGGING=false
FERNET_KEY=<your_airflow_metastore_fernet_key>
POSTGRES_DB=airflow
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=airflow
POSTGRES_PORT=5432
POSTGRES_USER=airflow
GLUE_CATALOG=<your_aws_glue_catalog>
GLUE_DATABASE=deafult
GLUE_DATABASE_STORAGE_LOCATION=<your_aws_s3_bucket>
STAGE=dev        
```

2. Start Docker container
```bash
docker compose up --build -d
```

3. Create admin user in Airflow
```bash
docker exec -it <airflow_webserver_container_id> /bin/bash

airflow users create -u admin -f <first_name> -l <last_name> -r Admin -e <email>
```

3. Configure connections in Airflow
```vash
airflow connections add 'adzuna_conn' \
    --conn-json '{
        "conn_type": "http",
        "extra": {
            "application_id": "<your_application_id>",
            "application_password": "<your_application_password>"
        }
    }'

airflow connections add 'aws_custom'  \
    --conn-json '{
        "conn_type": "aws",
        "login":"<your_aws_access_key_id>",
        "password":"<your_aws_secret_access_key>",
        "extra": {
            "region_name": "<your_aws_region>"
        }
    }'

airflow connections add 'openai_conn'  \
    --conn-json '{
        "conn_type": "http",
        "password":"<your_open_ai_api_key>"
    }'

airflow connections add 'slack_conn' \
    --conn-json '{
        "conn_type": "slack",
        "password":"<your_slack_webhook_url>"
    }'

```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Deployment
### Cloud infrastructure set up
1. Configure variables in `terraform.tfvars` in Terraform project
2. Deploy resources to AWS
```bash
cd infra/terraform
terraform init
terraform apply
```
### CI/CD pipeline set up
1. Configure the necessary environment and variables listed in [.github/workflows/CICD.yml](.github/workflows/CICD.yml) in Github Actions.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

The Power BI report provides an easy way to interact with the data. More complex analysis can be conducted through AWS Athena. Some useful queries are provided below
```sql
-- Popularity of skills for jobs with salary > 50th percentile
WITH cte AS (
    SELECT
        job_key,
        job_description_key,
        company_key,
        salary_max,
        row_number() over (
            PARTITION by job_key
            ORDER BY
                extraction_date_day DESC
        ) AS row_num
    FROM
        fct__job_listing f
    WHERE
        salary_max > 0
),
salary_pct AS (
    SELECT
        c.job_key,
        jd.title,
        dc.company,
        c.salary_max,
        percent_rank() over (
            ORDER BY
                c.salary_max ASC
        ) AS pct_rank
    FROM
        cte c
        JOIN dim__job_description jd ON c.job_description_key = jd.job_description_key
        JOIN dim__company dc ON dc.company_key = c.company_key
    WHERE
        row_num = 1
        AND lower(title) LIKE '%data%engineer'
)
SELECT
    ds.skill,
    count(s.job_key) AS job_required_count
FROM
    salary_pct s
    JOIN brdg__job_skill b ON b.job_key = s.job_key
    JOIN dim__skill ds ON ds.skill_key = b.skill_key
WHERE
    s.pct_rank > 0.5
GROUP BY
    ds.skill
ORDER BY
    count(s.job_key) DESC
```
```sql
-- Re-advertised jobs
WITH cte AS (
    SELECT
        f.job_key,
        d.title,
        f.extraction_date_day,
        CASE
            WHEN date_diff(
                'day',
                lag(f.extraction_date_day) over (
                    PARTITION by f.job_key
                    ORDER BY
                        f.extraction_date_day ASC
                ),
                f.extraction_date_day
            ) = 1 THEN 0
            ELSE 1
        END AS segment_start
    FROM
        fct__job_listing f
        JOIN dim__job_description d ON f.job_description_key = d.job_description_key
        AND lower (d.title) LIKE '%data%engineer'

),
segment AS (
    SELECT
        job_key,
        title,
        extraction_date_day,
        sum(segment_start) over (
            PARTITION by job_key
            ORDER BY
                extraction_date_day ASC
        ) AS segment_no
    FROM
        cte
),
segment_summary AS (
    SELECT
        job_key,
        title,
        segment_no,
        min(extraction_date_day) AS start_ad_date,
        max(extraction_date_day) AS end_ad_date
    FROM
        segment
    GROUP BY
        job_key,
        title,
        segment_no
)
SELECT
    job_key,
    title,
    listagg(
        concat(
            'start: ',
            cast(start_ad_date AS varchar),
            ', end: ',
            cast(end_ad_date AS varchar)
        ),
        '\n'
    ) within group (
        ORDER BY
            end_ad_date DESC
    ) AS details
FROM
    segment_summary
GROUP BY
    job_key,
    title
HAVING
    count(*) > 1
    AND max(end_ad_date) = (
        SELECT
            max(extraction_date_day)
        FROM
            fct__job_listing
    )
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[github-action-badge]:https://img.shields.io/badge/-github%20actions-1c2541?logo=githubactions&logoColor=2088FF&style=for-the-badge
[github-action-url]:https://github.com/features/actions
[spark-badge]: https://img.shields.io/badge/-apache%20spark-1c2541?logo=apachespark&logoColor=E25A1C&style=for-the-badge
[spark-url]: https://spark.apache.org/
[Airflow-badge]: https://img.shields.io/badge/-Apache%20Airflow-1c2541?logo=apacheairflow&logoColor=017CEE&style=for-the-badge
[airflow-url]: https://airflow.apache.org/
[dbt-badge]: https://img.shields.io/badge/-dbt-1c2541?logo=dbt&logoColor=FF694B&style=for-the-badge
[dbt-url]: https://www.getdbt.com/
[terraform-badge]: https://img.shields.io/badge/-terraform-1c2541?logo=terraform&logoColor=844FBA&style=for-the-badge
[terraform-url]: https://www.terraform.io/
[powerbi-badge]: https://img.shields.io/badge/-power%20bi-1c2541?logo=powerbi&logoColor=F2C811&style=for-the-badge
[powerbi-url]: https://www.microsoft.com/en-us/power-platform/products/power-bi
[docker-badge]: https://img.shields.io/badge/-docker-1c2541?logo=docker&logoColor=2496ED&style=for-the-badge
[docker-url]: https://www.docker.com/
[iceberg-badge]: https://img.shields.io/badge/-apache%20iceberg-1c2541?style=for-the-badge
[iceberg-url]: https://iceberg.apache.org/
