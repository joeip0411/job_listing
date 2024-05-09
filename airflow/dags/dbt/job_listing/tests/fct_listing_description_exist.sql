SELECT
    id
FROM
    {{ ref('fct__job_listing') }}
WHERE
    job_description_key NOT IN (
        SELECT
            job_description_key
        FROM
            {{ ref('dim__job_description')}}
    )