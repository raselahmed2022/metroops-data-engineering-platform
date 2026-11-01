select
    compressor_id,

    cast(reading_timestamp as date) as reading_date,

    count(*) as reading_count,

    avg(tp2) as avg_tp2,
    avg(tp3) as avg_tp3,
    avg(h1) as avg_h1,
    avg(dv_pressure) as avg_dv_pressure,
    avg(reservoirs) as avg_reservoirs,

    avg(oil_temperature) as avg_oil_temperature_c,
    max(oil_temperature) as max_oil_temperature_c,

    avg(motor_current) as avg_motor_current_a,
    max(motor_current) as max_motor_current_a,

    avg(caudal_impulses) as avg_caudal_impulses

from {{ ref('stg_sensor_readings') }}

where reading_timestamp is not null

group by
    compressor_id,
    cast(reading_timestamp as date)