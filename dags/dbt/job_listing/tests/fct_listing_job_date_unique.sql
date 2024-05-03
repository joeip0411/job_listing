SELECT
    job_key,
    extraction_date_day,
    count(*) AS cnt
FROM
    {{ ref('fct__job_listing') }}
GROUP BY
    job_key,
    extraction_date_day
HAVING
    count(*) > 1