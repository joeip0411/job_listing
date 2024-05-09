{{ config(
    materialized='table',
    file_format='iceberg'
) }}

with cte as (
    select
        distinct
        md5(id) as job_key,
        md5(skill) as skill_key
    from {{ ref('slvr__job_skills')}}

)

select * from cte
