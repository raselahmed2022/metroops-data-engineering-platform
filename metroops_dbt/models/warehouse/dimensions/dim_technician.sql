select
    t.technician_id,
    t.technician_name,
    t.specialization,
    t.skill_level,
    t.hourly_cost_eur,

    t.home_facility_id,
    f.facility_name as home_facility_name,
    f.city as home_facility_city,
    f.country as home_facility_country

from {{ ref('stg_technicians') }} t

left join {{ ref('dim_facility') }} f
    on t.home_facility_id = f.facility_id