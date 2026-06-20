from pyspark.sql.functions import avg,max,count
from utils.spark_session import get_spark_session
import os

GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def staging_to_prod():
    spark = get_spark_session("staging_to_prod",GOOGLE_APPLICATION_CREDENTIALS)
    departures_delay = spark.read.parquet(
    f"gs://{GCP_BUCKET_NAME}/staging/departures/"
    )
    return departures_delay.groupBy("station_name","train_type") \
            .agg( 
                avg("delay_minutes"),
                max("delay_minutes"),
                count("*")
            )

if __name__== "__main__":
    df = staging_to_prod()
    df.write.mode("overwrite").parquet(f"gs://{GCP_BUCKET_NAME}/prod/departures/")