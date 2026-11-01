select
    w.work_order_id,
    m.maintenance_id,
    w.fault_id,

    w.compressor_id,
    c.facility_id,
    w.technician_id,

    w.maintenance_type,
    w.priority,
    w.status,

    w.opened_at,
    w.closed_at,
    m.maintenance_date,

    date_diff('minute', w.opened_at, w.closed_at) / 60.0
        as work_order_duration_hours,

    m.labor_hours,
    m.downtime_minutes,
    m.downtime_minutes / 60.0 as downtime_hours,

    m.maintenance_cost_eur,
    w.external_cost_eur,

    m.labor_hours * t.hourly_cost_eur
        as technician_labor_cost_eur,

    m.maintenance_cost_eur + w.external_cost_eur
        as total_maintenance_cost_eur,

    w.resolution,

    c.asset_name,
    c.criticality,
    c.facility_name,

    t.technician_name,
    t.specialization,
    t.skill_level

from {{ ref('stg_work_orders') }} w

left join {{ ref('stg_maintenance_events') }} m
    on w.work_order_id = m.work_order_id

left join {{ ref('dim_compressor') }} c
    on w.compressor_id = c.compressor_id

left join {{ ref('dim_technician') }} t
    on w.technician_id = t.technician_id