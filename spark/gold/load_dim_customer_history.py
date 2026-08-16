from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

from config import *
from db_connection import connection_properties
from logger import logger

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SCD Type 2")
    .config("spark.jars", JAR_PATH)
    .getOrCreate()
)

logger.info("Reading Silver Table...")

silver_df = spark.read.jdbc(
    url=JDBC_URL,
    table="silver.customer_clean",
    properties=connection_properties
)

history_df = (
    silver_df
    .select(
        "customer_id",
        "age",
        "job",
        "marital",
        "education",
        "balance"
    )
    .withColumn("start_date", current_timestamp())
    .withColumn("end_date", lit(None).cast("timestamp"))
    .withColumn("is_current", lit(True))
)

logger.info("Writing History Table...")

history_df.write.mode("overwrite").jdbc(
    url=JDBC_URL,
    table="gold.dim_customer_history",
    properties=connection_properties
)

logger.info("History Table Loaded Successfully!")

spark.stop()