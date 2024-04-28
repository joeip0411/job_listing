WITH brz_listing AS (
    SELECT
        id,
        extraction_time_utc,
        count(*) AS cnt
    FROM
        {{ ref('brz__job_listing') }}
    GROUP BY
        id,
        extraction_time_utc
),
slvr_listing AS (
    SELECT
        id,
        extraction_time_utc,
        count(*) AS cnt
    FROM
        {{ ref('slvr__job_listing') }}
    GROUP BY
        id,
        extraction_time_utc
) 

(
    SELECT
        id,
        extraction_time_utc,
        cnt
    FROM
        brz_listing
    EXCEPT
    SELECT
        id,
        extraction_time_utc,
        cnt
    FROM
        slvr_listing
)
UNION ALL 
(
    SELECT
        id,
        extraction_time_utc,
        cnt
    FROM
        slvr_listing
    EXCEPT
    SELECT
        id,
        extraction_time_utc,
        cnt
    FROM
        brz_listing
)