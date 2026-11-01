select
    trim(technician_id) as technician_id,
    trim(technician_name) as technician_name,
    trim(specialization) as specialization,
    trim(skill_level) as skill_level,
    trim(home_facility_id) as home_facility_id,

    hourly_cost_eur,

    _source_file,
    _ingested_at

from {{ source('bronze', 'technicians') }}