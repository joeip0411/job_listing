{{ config(
    materialized='table',
    file_format='iceberg'
) }}

with cte as (
    select
        distinct
        md5(concat(country, state, region, city)) as location_key,
        country,
        state,
        region,
        city
    from {{ ref("slvr__job_listing") }}
)

select * from cte
