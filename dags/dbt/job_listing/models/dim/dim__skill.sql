{{ config(
    materialized='table',
    file_format='iceberg'
) }}

with cte as (
    select
        distinct
        md5(skill) as skill_key,
        skill
    from {{ ref("slvr__job_skills") }}
)

select * from cte