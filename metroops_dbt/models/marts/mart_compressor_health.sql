with daily_faults as (

    select
        compressor_id,
        cast(fault_start as date) as fault_date,

        count(*) as fault_count,

        sum(
            case
                when severity = 'Critical' then 1
                else 0
            end
        ) as critical_fault_count,

        sum(
            case
                when severity = 'High' then 1
                else 0
            end
        ) as high_fault_count

    from {{ ref('fct_faults') }}

    group by
        compressor_id,
        cast(fault_start as date)
)

select
    s.compressor_id,
    s.reading_date,

    c.asset_name,
    c.asset_type,
    c.criticality,
    c.manufacturer,

    c.facility_id,
    c.facility_name,
    c.city,
    c.country,

    s.reading_count,

    s.avg_tp2,
    s.avg_tp3,
    s.avg_h1,
    s.avg_dv_pressure,
    s.avg_reservoirs,

    s.avg_oil_temperature_c,
    s.max_oil_temperature_c,

    s.avg_motor_current_a,
    s.max_motor_current_a,

    s.avg_caudal_impulses,

    coalesce(f.fault_count, 0) as fault_count,
    coalesce(f.high_fault_count, 0) as high_fault_count,
    coalesce(f.critical_fault_count, 0) as critical_fault_count,

    case
        when coalesce(f.fault_count, 0) > 0 then true
        else false
    end as had_fault

from {{ ref('fct_sensor_daily') }} s

left join {{ ref('dim_compressor') }} c
    on s.compressor_id = c.compressor_id

left join daily_faults f
    on s.compressor_id = f.compressor_id
    and s.reading_date = f.fault_date