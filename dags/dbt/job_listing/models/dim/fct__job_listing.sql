{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unqiue_key=['job_key', 'extraction_date_key']
) }}

with cte as (
    select
        md5(id) as job_key,
        id,
        md5(category) as category_key,
        md5(company) as company_key,
        md5(concat(country, state, region, city)) as location_key,
        md5(concat(contract_type,contract_time)) as contract_type_key,
        md5(id) as job_description_key,
        d.ad_creation_date_key,
        date(l.ad_creation_time_utc) as ad_creation_date,
        e.extraction_date_key,
        e.extraction_date_day,
        salary_min,
        salary_max
    from {{ ref('slvr__job_listing')}} l 
    join {{ ref('dim__ad_creation_date')}} d 
    on date(l.ad_creation_time_utc) = d.ad_creation_date_day
    join {{ ref('dim__extraction_date')}} e 
    on date(l.extraction_time_utc) = e.extraction_date_day

    {% if is_incremental() %}
    where date(l.extraction_time_utc) > (select max(extraction_date_day) from {{ this }})
    {% endif %}
)

select * from cte