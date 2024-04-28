{{ config(
    materialized='incremental',
    incremental_strategy='append',
    file_format='iceberg'
) }}

with cte as (
	SELECT 
		id,
		EXPLODE(
			SPLIT(
				REGEXP_REPLACE(
					REGEXP_EXTRACT(skill, '(([\\\w| |[^\\\w\\\s]]+ \\\|){2,} [\\\w| |[^\\\w\\\s]]+)', 1), 
					'Result: ', 
					''),
				' \\\| '
			)
		) as skill
	
	FROM {{ ref("brz__job_skills")}}
	
	{% if is_incremental() %}
	where id not in (select id from {{ this }})
	{% endif %}

),

final as (
	select
		id,
		lower(skill) as skill
	from cte
)

select * from final