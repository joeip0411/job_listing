SELECT
    id
FROM
    {{ ref('fct__job_listing') }}
WHERE
    company_key NOT IN (
        SELECT
            company_key
        FROM
            {{ ref('dim__company') }}
    )