{{ config(
    materialized='table',
    file_format='iceberg'
) }}

WITH cte AS (
    SELECT
        md5(l.id) AS job_description_key,
        l.title,
        d.job_description,
        row_number() over (
            PARTITION by l.id
            ORDER BY
                l.extraction_time_utc DESC
        ) AS row_num
    FROM
        {{ ref('slvr__job_listing') }} l
        JOIN {{ ref('slvr__job_description') }} d ON l.id = d.id
),
final AS (
    SELECT
        job_description_key,
        title,
        job_description
    FROM
        cte
    WHERE
        row_num = 1
)
SELECT
    *
FROM
    final