{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unique_key=['id']
) }}

select
    *
from {{ source('job', 'stg__job_description') }}

{% if is_incremental() %}
where date(extraction_time_utc) >= (select date(max(extraction_time_utc)) from {{ this }})
{% endif %}