SELECT
    id
FROM
    {{ ref('fct__job_listing') }}
WHERE
    location_key NOT IN (
        SELECT
            location_key
        FROM
            {{ ref('dim__location') }}
    )