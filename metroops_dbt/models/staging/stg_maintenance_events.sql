select
    trim(maintenance_id) as maintenance_id,
    trim(work_order_id) as work_order_id,
    trim(compressor_id) as compressor_id,
    trim(technician_id) as technician_id,

    try_cast(maintenance_date as timestamp) as maintenance_date,

    trim(maintenance_type) as maintenance_type,

    labor_hours,
    downtime_minutes,
    maintenance_cost_eur,

    trim(resolution) as resolution,

    _source_file,
    _ingested_at

from {{ source('bronze', 'maintenance_events') }}