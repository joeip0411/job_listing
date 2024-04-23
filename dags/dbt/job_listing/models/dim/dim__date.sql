{{ config(
    materialized='table',
    file_format='iceberg',
    enable=false
) }}

{{ dbt_date.get_date_dimension("2020-01-01", "2034-12-31") }}