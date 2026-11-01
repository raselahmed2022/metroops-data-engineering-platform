select
    trim(work_order_id) as work_order_id,
    trim(compressor_id) as compressor_id,
    trim(fault_id) as fault_id,
    trim(technician_id) as technician_id,

    trim(maintenance_type) as maintenance_type,
    trim(priority) as priority,

    try_cast(opened_at as timestamp) as opened_at,
    try_cast(closed_at as timestamp) as closed_at,

    trim(status) as status,

    labor_hours,
    external_cost_eur,

    trim(resolution) as resolution,

    _source_file,
    _ingested_at

from {{ source('bronze', 'work_orders') }}