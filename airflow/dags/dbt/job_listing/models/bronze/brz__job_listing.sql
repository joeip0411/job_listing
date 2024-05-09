{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    partition_by=['day(extraction_time_utc)'],
    unique_key=['id','extraction_time_utc']
) }}

select
    *
from {{ source('job', 'stg__job_listing') }}

{% if is_incremental() %}
where date(extraction_time_utc) > (select date(max(extraction_time_utc)) from {{ this }})
{% endif %}