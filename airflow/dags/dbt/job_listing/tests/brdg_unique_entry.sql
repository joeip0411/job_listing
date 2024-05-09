SELECT
    job_key,
    skill_key
FROM
    {{ ref('brdg__job_skill') }}
GROUP BY
    job_key,
    skill_key
HAVING
    count(*) > 1