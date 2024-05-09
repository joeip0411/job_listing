SELECT
    id
FROM
    {{ ref('fct__job_listing') }}
WHERE
    category_key NOT IN (
        SELECT
            category_key
        FROM
            {{ ref('dim__category') }}
    )