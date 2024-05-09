SELECT
    id,
    date(extraction_time_utc) AS extraction_date,
    count(*) AS cnt
FROM
    {{ ref('brz__job_listing') }}
GROUP BY
    id,
    date(extraction_time_utc)
HAVING
    count(*) > 1