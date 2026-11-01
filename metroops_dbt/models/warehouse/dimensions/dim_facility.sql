select
    facility_id,
    facility_name,
    city,
    country,
    facility_type,
    operating_hours,
    opened_date

from {{ ref('stg_facilities') }}