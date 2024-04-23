{{ config(
    materialized='incremental',
    incremental_strategy='append',
    file_format='iceberg',
    partition_by=['day(extraction_time_utc)']
) }}

with cte as (
    select
        id,
        title,
        regexp_extract(category, 'label=([\\\w|\\\s]+)',1) as category,
    regexp_extract(company, 'display_name=(.+),',1) as company,
    split(regexp_extract(location, 'area=\\\[(.+)\]', 1),',') as area,
    to_timestamp(created) as ad_creation_time_utc,
    salary_is_predicted,
    contract_type,
    contract_time,
    salary_min,
    salary_max,
    description,
    extraction_time_utc
from {{ ref('brz__job_listing')}}

{% if is_incremental() %}
where extraction_time_utc >= (select max(extraction_time_utc) from {{ this }})
{% endif %}
),

final as (
    select 
        id,
        title,
        category,
        company,
        ifnull(area[0], 'N/A') as country,
        ifnull(area[1], 'N/A') as state,
        ifnull(area[2], 'N/A') as region,
        ifnull(area[3], 'N/A') as city,
        ad_creation_time_utc,
        salary_is_predicted,
        ifnull(contract_type, 'N/A') as contract_type,
        ifnull(contract_time, 'N/A') as contract_time,
        salary_min,
        salary_max,
        description,
        extraction_time_utc 
    from cte
)

select * from final
