{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unique_key='id'
) }}

select
    *
from {{ source('job', 'stg__job_skills') }}