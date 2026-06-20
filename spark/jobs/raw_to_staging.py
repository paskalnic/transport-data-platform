from utils.spark_session import get_spark_session
import os
from pyspark.sql.functions import explode,col,to_timestamp

GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
def raw_to_staging():
    spark = get_spark_session("raw_to_staging",GOOGLE_APPLICATION_CREDENTIALS)
    departures_df = spark.read.option("multiline", "true").json(
    f"gs://{GCP_BUCKET_NAME}/raw/departures/*.json"
)
    return departures_df.select(explode("departures").alias("departures"))

def extract_col(dataframe):

    df = dataframe.select(
        col("departures.stop_point.name").alias("station_name"),
        col("departures.display_informations.commercial_mode").alias("train_type"),
        col("departures.display_informations.direction").alias("direction"),
        to_timestamp(col("departures.stop_date_time.departure_date_time"),"yyyyMMdd'T'HHmmss").alias("departure_time"),
        to_timestamp(col("departures.stop_date_time.base_departure_date_time"),"yyyyMMdd'T'HHmmss").alias("base_departure_time")

    )
    return df.withColumn("delay_minutes",(col("departure_time")-col("base_departure_time"))/60)
   

if __name__=="__main__":
    df = raw_to_staging()
    clean_df = extract_col(df)
    clean_df.write.mode("overwrite").parquet(f"gs://{GCP_BUCKET_NAME}/staging/departures/")
    