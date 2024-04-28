SELECT
    count(*)
FROM
    {{ ref('brz__job_listing') }}
WHERE
    id NOT IN (
        SELECT
            id
        FROM
            {{ ref('brz__job_description') }}
    )
HAVING
    count(*) > 0