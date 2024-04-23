{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unique_key='id'
) }}

select
    id,
    full_description as job_description
from {{ source('job', 'stg__job_description') }}