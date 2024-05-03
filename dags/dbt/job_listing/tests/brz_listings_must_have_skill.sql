SELECT
    count(*)
FROM
    {{ ref('brz__job_listing') }}
WHERE
    id NOT IN (
        SELECT
            id
        FROM
            {{ ref('brz__job_skills') }}
    )
HAVING
    count(*) > 0