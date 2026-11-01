select
    trim(facility_id) as facility_id,
    trim(facility_name) as facility_name,
    trim(city) as city,
    trim(country) as country,
    trim(facility_type) as facility_type,

    trim(operating_hours) as operating_hours,

    try_cast(opened_date as date) as opened_date,

    _source_file,
    _ingested_at

from {{ source('bronze', 'facilities') }}