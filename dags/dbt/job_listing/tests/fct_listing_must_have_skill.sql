SELECT
    count(*) AS cnt
FROM
    {{ref('fct__job_listing')}}
WHERE
    job_key NOT IN (
        SELECT
            DISTINCT job_key
        FROM
            {{ref('brdg__job_skill')}}
    )
HAVING
    count(*) > 0

UNION ALL

SELECT
    count(*) AS cnt
FROM
    {{ref('brdg__job_skill')}}
WHERE
    skill_key NOT IN (
        SELECT
            skill_key
        FROM
            {{ref('dim__skill')}}
    )
HAVING
    count(*) > 0