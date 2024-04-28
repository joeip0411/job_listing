{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    file_format='iceberg',
    unqiue_key=['job_description_key']
) }}

with cte as (
    select
        md5(l.id) as job_description_key,
        l.title,
        d.job_description
    from {{ ref('slvr__job_listing')}} l join {{ ref('slvr__job_description')}} d on l.id = d.id

)

select * from cte