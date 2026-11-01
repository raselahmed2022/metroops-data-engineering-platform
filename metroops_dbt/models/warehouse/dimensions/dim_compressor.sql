select
    c.compressor_id,
    c.asset_name,
    c.asset_type,
    c.asset_status,
    c.commissioned_date,
    c.planned_replacement_date,
    c.max_pressure_bar,
    c.max_oil_temp_c,
    c.max_motor_current_a,
    c.criticality,
    c.manufacturer,

    c.facility_id,
    f.facility_name,
    f.city,
    f.country,
    f.facility_type

from {{ ref('stg_compressors') }} c

left join {{ ref('dim_facility') }} f
    on c.facility_id = f.facility_id