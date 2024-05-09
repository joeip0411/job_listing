SELECT
    id
FROM
    {{ ref('fct__job_listing') }}
WHERE
    contract_type_key NOT IN (
        SELECT
            contract_type_key
        FROM
            {{ ref('dim__contract_type') }}
    )