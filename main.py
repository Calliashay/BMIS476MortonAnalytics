import os
import polars as pl
import numpy as np
from adbc_driver_postgresql import dbapi



## load vessel finder feed data
username = os.getenv("DB_APP_USER")
password = os.getenv("DB_APP_PW")
server_uri = os.getenv("DB_SERVER_URI")
server_port = os.getenv("DB_SERVER_PORT")
db_name = os.getenv("DB_NAME")

uri = f"postgresql://{username}:{password}@{server_uri}:{server_port}/{db_name}"

## helper function
def change_of(value):
    final = np.diff(value).mean()
    return(final)

## data processing
start_data = pl.read_database_uri(
    """
    WITH latest_voyage as (
        SELECT mmsi
        ,MAX(voyage_count) AS max_voyage_count

        FROM ais_integration

        GROUP BY mmsi
    )
        SELECT ai.* 
        
        FROM ais_integration ai
        LEFT JOIN latest_voyage lv ON lv.mmsi = ai.mmsi

        WHERE 1=1
        AND (ai.voyage_count >= lv.max_voyage_count OR ai.voyage_count IS NULL)
        
        """
    ,uri = uri
    ,engine = 'adbc'
)

start_data = start_data.filter(pl.col('source') != "inferred_data")
window_chunks = start_data.partition_by('mmsi')
windowed_data_complete = pl.DataFrame([])
for chunk in window_chunks:
  windowed_data = (
  chunk
    .sort(pl.col(['timestamp']))
    .with_columns(
      pl.col('speed')
        .rolling(index_column="timestamp", period = "3h")
        .map_elements(change_of, return_dtype=float)
        .alias('speed_delta_3h'),
      pl.col('distance_to_anchorage')
        .rolling(index_column="timestamp", period = "3h")
        .map_elements(change_of, return_dtype=float)
        .alias('anchorage_delta_3h'),
      pl.col('distance_to_terminal')
        .rolling(index_column="timestamp", period = "3h")
        .map_elements(change_of, return_dtype=float)
        .alias('terminal_delta_3h'),
      pl.col('draught')
        .rolling(index_column="timestamp", period = "3h")
        .map_elements(change_of, return_dtype=float)
        .alias('draught_delta_3h')
        ).fill_nan(None)
    )

  windowed_data_1i = (
    windowed_data
      .sort(pl.col(['ais_int_id']))
      .with_columns(
        pl.col('speed')
          .rolling(index_column="ais_int_id", period = "2i")
          .map_elements(change_of, return_dtype=float)
          .alias('speed_delta_1i'),
        pl.col('distance_to_anchorage')
          .rolling(index_column="ais_int_id", period = "2i")
          .map_elements(change_of, return_dtype=float)
          .alias('anchorage_delta_1i'),
        pl.col('distance_to_terminal')
          .rolling(index_column="ais_int_id", period = "2i")
          .map_elements(change_of, return_dtype=float)
          .alias('terminal_delta_1i'),
        pl.col('draught')
          .rolling(index_column="ais_int_id", period = "2i")
          .map_elements(change_of, return_dtype=float)
          .alias('draught_delta_1i')
      ).fill_nan(None)
    )

  windowed_data_coalesced =(
    windowed_data_1i.with_columns(
        pl.coalesce(pl.col(['speed_delta_3h', 'speed_delta_1i'])).alias('speed_delta'),
        pl.coalesce('anchorage_delta_3h', 'anchorage_delta_1i').alias('anchorage_delta'),
        pl.coalesce('terminal_delta_3h', 'terminal_delta_1i').alias('terminal_delta'),
        pl.coalesce('draught_delta_3h', 'draught_delta_1i').alias('draught_delta')
    )
  )

  labeled_window_data = windowed_data_coalesced.with_columns(
      pl.when(pl.col("speed_delta") < 0).then(pl.lit("decreasing"))
        .when(pl.col("speed_delta") > 0).then(pl.lit("increasing"))
        .otherwise(pl.lit('stable'))
        .alias("speed_status"),
      pl.when(pl.col('anchorage_delta') <0).then(pl.lit("decreasing"))
        .when(pl.col("anchorage_delta") > 0).then(pl.lit("increasing"))
        .otherwise(pl.lit('stable'))
        .alias("anchorage_status"),
      pl.when(pl.col('terminal_delta') <0).then(pl.lit("decreasing"))
        .when(pl.col("terminal_delta") > 0).then(pl.lit("increasing"))
        .otherwise(pl.lit('stable'))
        .alias("terminal_status"),
      pl.when(pl.col('draught_delta') <0).then(pl.lit("decreasing"))
        .when(pl.col("draught_delta") > 0).then(pl.lit("increasing"))
        .otherwise(pl.lit('stable'))
        .alias("draught_status")
  )

  windowed_data_complete = pl.concat([windowed_data_complete, labeled_window_data])

terminal_data = pl.read_database_uri(
    """
    SELECT terminal_id, terminal_type FROM terminals
    """
    ,uri = uri
    ,engine = 'adbc'
)

windowed_joined = windowed_data_complete.join(terminal_data, on = 'terminal_id', how = "left")


## event labels

event_labeled_data = windowed_joined.with_columns(
      pl.when(
        pl.col('navigational_status') == 5
        ,pl.col('terminal_type') == 'Supplier'
        ,pl.col('in_terminal') == 1
        )
      .then(pl.lit('berth_loading'))
      .when(
        pl.col('navigational_status') == 5
        ,pl.col('terminal_type') == 'Customer'
        ,pl.col('in_terminal') == 1
        )
      .then(pl.lit('berth_discharging'))
      .when(
        pl.col('navigational_status') == 1
        ,pl.col('in_anchorage') == 1
        )
      .then(pl.lit('anchorage_idling'))
      .when(
        pl.col('distance_to_anchorage') <= 5000
        ,pl.col('speed')  <= 2
        ,pl.col('anchorage_status') == "increasing"
      )
      .then(pl.lit("anchorage_departure"))
      .when(
        pl.col('distance_to_anchorage') <= 5000
        ,pl.col('speed')  <= 2
        ,pl.col('anchorage_status') == "decreasing"
      )
      .then(pl.lit("anchorage_arrival"))
      .when(
        pl.col('distance_to_terminal') <= 5000
        ,pl.col('speed')  <= 2
        ,pl.col('terminal_status') == "increasing"
      )
      .then(pl.lit("berth_departure"))
      .when(
        pl.col('distance_to_terminal') <= 5000
        ,pl.col('speed')  <= 2
        ,pl.col('terminal_status') == "decreasing"
      )
      .then(pl.lit("berth_arrival"))
      .when(
        pl.col('speed') <= 2
        ,pl.col('navigational_status') == 0
        ,pl.col('on_river') == 0
      )
      .then(pl.lit("drifting"))
      .when(
        pl.col('navigational_status') == 5
        ,pl.col("in_terminal") == 0
        ,pl.col('speed') <= .1
      )
      .then(pl.lit("berth_unknown"))
      .when(
        pl.col('navigational_status') == 0
        ,pl.col('speed') > 2
        )
      .then(pl.lit('sailing'))
      .alias('event_description')
)

## add voyage counter
pl_voyage_count_chunks = event_labeled_data.partition_by("mmsi")
pl_voyage_counter_added = pl.DataFrame([])

for chunk in pl_voyage_count_chunks:

  pl_with_terminal_type = chunk.sort(pl.col('timestamp'), descending = False).with_columns(pl.col('in_terminal').shift(1).fill_null(pl.col('in_terminal')).alias('prev_in_terminal')
                                                                                          ,pl.col('in_terminal').shift(2).fill_null(pl.col('in_terminal')).alias('prev_in_terminal2')
                                                                                          ,pl.col('in_terminal').shift(3).fill_null(pl.col('in_terminal')).alias('prev_in_terminal3')
                                                                                          ,pl.col('in_terminal').shift(-1).fill_null(pl.col('in_terminal')).alias('future_in_terminal1')
                                                                                          ,pl.col('in_terminal').shift(-2).fill_null(pl.col('in_terminal')).alias('future_in_terminal2')
                                                                                          ,pl.col('in_terminal').shift(-3).fill_null(pl.col('in_terminal')).alias('future_in_terminal3')
                                                                                          ,pl.col('event_description').shift(1).alias('prev_event_description'))
  pl_avg = pl_with_terminal_type.with_columns( 
    ((pl.col("in_terminal") + pl.col('prev_in_terminal')+ pl.col('prev_in_terminal2')+ pl.col('prev_in_terminal3')+ pl.col('future_in_terminal1')+ pl.col('future_in_terminal2')+ pl.col('future_in_terminal3'))/7).alias('avg_terminal')
  )                                                                                        
  pl_voyage_count =   pl_avg.sort(pl.col('timestamp'), descending= False).with_columns(
    voyage_count = (
        ((pl.col('avg_terminal') >= .5) & (pl.col('prev_in_terminal') == 0 )).cast(pl.Int32)  # Convert boolean to integer (1 for True, 0 for False)
        .cum_sum()
        .over("mmsi")
    )
    )
  pl_voyage_counter_added = pl.concat([pl_voyage_counter_added,pl_voyage_count])

## add voyage leg status
pl_voyage_leg_status_chunks = pl_voyage_counter_added.partition_by("mmsi","voyage_count")
pl_voyage_leg_status_added = pl.DataFrame([])
chunk = pl_voyage_leg_status_chunks[1]
for chunk in pl_voyage_leg_status_chunks:
  #pl_with_prev = chunk.sort('timestamp', descending=False).with_columns(pl.col('voyage_leg_type').shift(1).alias('prev_voyage_leg_type'))

  item = chunk.filter( (pl.col('in_terminal') == 1) | (pl.col("prev_in_terminal")== 1) )
  if item.height == 0:
    pl_voyage_leg_status = chunk.with_columns(
      voyage_leg_type =  pl.lit('unknown')
      )
    pl_voyage_leg_status_added = pl.concat([pl_voyage_leg_status_added,pl_voyage_leg_status])
  else:

    dist_terminal_id =item.n_unique(subset = ['terminal_id'])

    if dist_terminal_id >1 :
      #if count of distinct terminal id == 1, then guess for supplier (set laden), unknown for customer else do below

      max_date = item.select(pl.max('timestamp')).to_series()

      leg_status = item.filter(pl.col('timestamp') >= max_date)
      leg_status_label = leg_status.select(assign = pl.when(
          ( (pl.col('in_terminal') == 1) | (pl.col("prev_in_terminal")== 1) )
          ,pl.col('terminal_type') == "Supplier"
        )
        .then(
          pl.lit('ballast')
        )
        .when(
          ( (pl.col('in_terminal') == 1) | (pl.col("prev_in_terminal")== 1) )
          ,pl.col('terminal_type') == "Customer"
        )
        .then(
          pl.lit('laden')
        ))

      pl_voyage_leg_status = chunk.with_columns(
        voyage_leg_type =  pl.lit(leg_status_label['assign'].first())
      )
      pl_voyage_leg_status_added = pl.concat([pl_voyage_leg_status_added,pl_voyage_leg_status])

    elif dist_terminal_id <= 1:

      max_date = item.select(pl.max('timestamp')).to_series()

      leg_status = item.filter(pl.col('timestamp') >= max_date)

      leg_status_label = leg_status.select(assign = pl.when(
          ( (pl.col('in_terminal') == 1) | (pl.col("prev_in_terminal")== 1) )
          ,pl.col('terminal_type') == "Supplier"
        )
        .then(
          pl.lit('ballast')
        )
        .when(
          ( (pl.col('in_terminal') == 1) | (pl.col("prev_in_terminal")== 1) )
          ,pl.col('terminal_type') == "Customer"
        )
        .then(
          pl.lit('laden')
        ))

      pl_voyage_leg_status = chunk.with_columns(
        voyage_leg_type =  pl.lit(leg_status_label['assign'].first())
      )

      pl_voyage_leg_status_added = pl.concat([pl_voyage_leg_status_added,pl_voyage_leg_status])
 

pl_final = pl_voyage_leg_status_added.select(['ais_int_id',
 'mmsi',
 'timestamp',
 'ts_date',
 'latitude',
 'longitude',
 'course',
 'speed',
 'heading',
 'navigational_status',
 'imo',
 'vessel_name',
 'call_sign',
 'vessel_type',
 'draught',
 'estimated_destination',
 'geographic_zone',
 'ts_year',
 'ts_month',
 'ts_day',
 'ts_hour',
 'ts_minute',
 'prev_latitude',
 'prev_longitude',
 'prev_timestamp',
 'calculated_bearing',
 'calculated_distance',
 'on_river',
 'terminal_id',
 'in_terminal',
 'distance_to_terminal',
 'in_anchorage',
 'distance_to_anchorage',
 'event_description',
 'voyage_count',
 'voyage_leg_count',
 'voyage_leg_type',
 'eca',
 'source'])

## write to the temp table to update integration with new columns
pl_final_2 = pl_final.with_columns(
  pl.col('voyage_count').cast(pl.Float64)
  ,pl.col('voyage_leg_count').cast(pl.Float64)
).unique(subset = 'ais_int_id', keep = 'first').sort('timestamp')

conn = dbapi.connect(uri)
cursor = conn.cursor()
cursor.execute(
    """
    TRUNCATE TABLE ais_integration_temp;
    """
    )
conn.commit()
cursor.close()
conn.close()


pl_final_2.write_database(
           table_name ='ais_integration_temp',
           connection = uri,
           engine = 'adbc',
           if_table_exists = 'append'
        )