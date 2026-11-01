select
    reading_id,
    trim(compressor_id) as compressor_id,
    try_cast("timestamp" as timestamp) as reading_timestamp,

    TP2 as tp2,
    TP3 as tp3,
    H1 as h1,
    DV_pressure as dv_pressure,
    Reservoirs as reservoirs,
    Oil_temperature as oil_temperature,
    Motor_current as motor_current,
    Caudal_impulses as caudal_impulses,

    _source_file,
    _ingested_at

from {{ source('bronze', 'sensor_readings') }}