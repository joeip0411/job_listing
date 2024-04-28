{{ config(
    materialized='table',
    file_format='iceberg'
) }}

{{ dbt_date.get_date_dimension("2020-01-01", "2034-12-31") }}