select
    compressor_id,
    reading_date,
    count(*) as row_count

from {{ ref('fct_sensor_daily') }}

group by
    compressor_id,
    reading_date

having count(*) > 1