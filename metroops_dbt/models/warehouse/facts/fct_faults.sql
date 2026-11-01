select
    f.fault_id,
    f.compressor_id,
    c.facility_id,

    f.fault_start,
    f.fault_end,
    date_diff('minute', f.fault_start, f.fault_end) as fault_duration_minutes,

    f.fault_type,
    f.severity,
    f.fault_status,
    f.detected_by,

    f.oil_temperature_c,
    f.motor_current_a,
    f.tp3_pressure_bar,

    c.asset_name,
    c.asset_type,
    c.criticality,
    c.manufacturer,

    c.facility_name,
    c.city,
    c.country

from {{ ref('stg_fault_events') }} f

left join {{ ref('dim_compressor') }} c
    on f.compressor_id = c.compressor_id