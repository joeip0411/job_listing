{{ config(
    materialized='table',
    file_format='iceberg',
    enabled=false
) }}

with cte as (
    select
        md5(date_format(date_day, 'yyyy-MM-dd')) as extraction_date_key,
        date_day as extraction_date_day,
        prior_date_day as extraction_prior_date_day,
        next_date_day as extraction_next_date_day,
        prior_year_date_day as extraction_prior_year_date_day,
        prior_year_over_year_date_day as extraction_prior_year_over_year_date_day,
        day_of_week as extraction_day_of_week,
        day_of_week_iso as extraction_day_of_week_iso,
        day_of_week_name as extraction_day_of_week_name,
        day_of_week_name_short as extraction_day_of_week_name_short,
        day_of_month as extraction_day_of_month,
        day_of_year as extraction_day_of_year,
        week_start_date as extraction_week_start_date,
        week_end_date as extraction_week_end_date,
        prior_year_week_start_date as extraction_prior_year_week_start_date,
        prior_year_week_end_date as extraction_prior_year_week_end_date,
        week_of_year as extraction_week_of_year,
        iso_week_start_date as extraction_iso_week_start_date,
        iso_week_end_date as extraction_iso_week_end_date,
        prior_year_iso_week_start_date as extraction_prior_year_iso_week_start_date,
        prior_year_iso_week_end_date as extraction_prior_year_iso_week_end_date,
        iso_week_of_year as extraction_iso_week_of_year,
        prior_year_week_of_year as extraction_prior_year_week_of_year,
        prior_year_iso_week_of_year as extraction_prior_year_iso_week_of_year,
        month_of_year as extraction_month_of_year,
        month_name as extraction_month_name,
        month_name_short as extraction_month_name_short,
        month_start_date as extraction_month_start_date,
        month_end_date as extraction_month_end_date,
        prior_year_month_start_date as extraction_prior_year_month_start_date,
        prior_year_month_end_date as extraction_prior_year_month_end_date,
        quarter_of_year as extraction_quarter_of_year,
        quarter_start_date as extraction_quarter_start_date,
        quarter_end_date as extraction_quarter_end_date,
        year_number as extraction_year_number,
        year_start_date as extraction_year_start_date,
        year_end_date as extraction_year_end_date
    from {{ ref('dim__date')}}

)

select * from cte