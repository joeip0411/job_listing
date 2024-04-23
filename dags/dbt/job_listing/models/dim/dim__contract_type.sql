{{ config(
    materialized='table',
    file_format='iceberg',
) }}

with cte as (
    select
        distinct
        md5(concat(contract_type,contract_time)) as contract_type_key,
        contract_type,
        contract_time
    from {{ ref("slvr__job_listing") }}
)

select * from cte
