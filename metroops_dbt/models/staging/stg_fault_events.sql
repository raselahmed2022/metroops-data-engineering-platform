select
    trim(fault_id) as fault_id,
    trim(compressor_id) as compressor_id,

    try_cast(fault_start as timestamp) as fault_start,
    try_cast(fault_end as timestamp) as fault_end,

    trim(fault_type) as fault_type,
    trim(severity) as severity,

    oil_temperature_c,
    motor_current_a,
    tp3_pressure_bar,

    trim(detected_by) as detected_by,
    trim(fault_status) as fault_status,

    _source_file,
    _ingested_at

from {{ source('bronze', 'fault_events') }}