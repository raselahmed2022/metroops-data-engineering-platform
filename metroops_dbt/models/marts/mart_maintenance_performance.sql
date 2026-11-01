select
    work_order_id,
    maintenance_id,
    fault_id,

    compressor_id,
    facility_id,
    technician_id,

    maintenance_type,
    priority,
    status,

    opened_at,
    closed_at,
    maintenance_date,

    work_order_duration_hours,
    labor_hours,
    downtime_minutes,
    downtime_hours,

    maintenance_cost_eur,
    external_cost_eur,
    technician_labor_cost_eur,
    total_maintenance_cost_eur,

    asset_name,
    criticality,
    facility_name,

    technician_name,
    specialization,
    skill_level,

    resolution

from {{ ref('fct_maintenance') }}