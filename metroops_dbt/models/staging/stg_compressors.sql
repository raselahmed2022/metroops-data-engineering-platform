select
    trim(compressor_id) as compressor_id,
    trim(facility_id) as facility_id,
    trim(asset_name) as asset_name,
    trim(asset_type) as asset_type,
    trim(asset_status) as asset_status,

    try_cast(commissioned_date as date) as commissioned_date,
    try_cast(planned_replacement_date as date) as planned_replacement_date,

    max_pressure_bar,
    max_oil_temp_c,
    max_motor_current_a,

    trim(criticality) as criticality,
    trim(manufacturer) as manufacturer,

    _source_file,
    _ingested_at

from {{ source('bronze', 'compressors') }}