select
    count(*)
from {{ ref('brz__job_listing') }}
where id not in (select id from {{ ref('brz__job_skills')}})
having count(*) > 0