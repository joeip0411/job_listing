{{ config(
    materialized='incremental',
    incremental_strategy='append',
    file_format='iceberg',
    partition_by=['day(extraction_time_utc)']
) }}

select
    *
from {{ source('job', 'stg__job_listing') }}

{% if is_incremental() %}
where extraction_time_utc >= (select max(extraction_time_utc) from {{ this }})
{% endif %}