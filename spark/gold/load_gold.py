from pyspark.sql import SparkSession
from pyspark.sql.functions import count

from config import *
from db_connection import connection_properties
from logger import logger

# Create Spark Session
spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("Gold Layer")
    .config("spark.jars", JAR_PATH)
    .getOrCreate()
)

logger.info("Reading Silver Table...")

silver_df = (
    spark.read.jdbc(
        url=JDBC_URL,
        table="silver.customer_clean",
        properties=connection_properties
    )
)

logger.info(f"Silver Records: {silver_df.count()}")

# Business Summary
gold_df = (
    silver_df
    .groupBy("y")
    .agg(count("*").alias("total_customers"))
)

logger.info("Writing Gold Table...")

(
    gold_df.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.deposit_summary",
        properties=connection_properties
    )
)

logger.info("Gold Layer Loaded Successfully!")

spark.stop()