{{ config(
    materialized='table',
    file_format='iceberg',
) }}

with cte as (
    select
        distinct
        md5(company) as company_key,
        company
    from {{ ref("slvr__job_listing") }}
)

select * from cte
