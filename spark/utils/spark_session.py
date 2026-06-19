from pyspark.sql import SparkSession

def get_spark_session(app_name: str, credentials_path: str) -> SparkSession:
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("fs.gs.auth.type","SERVICE_ACCOUNT_JSON_KEYFILE") \
        .config("fs.gs.auth.service.account.json.keyfile",credentials_path) \
        .config("fs.gs.impl","com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .getOrCreate()
    return spark
