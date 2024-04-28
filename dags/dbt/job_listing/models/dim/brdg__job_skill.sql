{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unqiue_key=['job_key', 'skill_key']
) }}

with cte as (
    select
        md5(id) as job_key,
        md5(skill) as skill_key
    from {{ ref('slvr__job_skills')}}

)

select * from cte
