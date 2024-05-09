{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unique_key='id'
) }}

select
    id,
    full_description as job_description
from {{ ref('brz__job_description')}}