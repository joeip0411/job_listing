{{ config(
    materialized='table',
    file_format='iceberg',
) }}

with cte as (
    select
        distinct
        md5(category) as category_key,
        category as category_description
    from {{ ref("slvr__job_listing") }}
)

select * from cte
