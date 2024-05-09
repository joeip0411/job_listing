WITH slvr AS (
    SELECT
        id,
        date(extraction_time_utc) AS extraction_date_day,
        count(*) AS cnt
    FROM
        {{ ref('slvr__job_listing') }}
    GROUP BY
        id,
        date(extraction_time_utc)
),
fct AS (
    SELECT
        f.id,
        d.extraction_date_day,
        count(*) AS cnt
    FROM
        {{ ref('fct__job_listing') }} f
        JOIN {{ ref('dim__extraction_date')}} d 
        ON f.extraction_date_key = d.extraction_date_key
    GROUP BY
        f.id,
        d.extraction_date_day
) 

(
    SELECT
        id,
        extraction_date_day,
        cnt
    FROM
        slvr
    EXCEPT
    SELECT
        id,
        extraction_date_day,
        cnt
    FROM
        fct
)
UNION ALL 
(
    SELECT
        id,
        extraction_date_day,
        cnt
    FROM
        fct
    EXCEPT
    SELECT
        id,
        extraction_date_day,
        cnt
    FROM
        slvr
)