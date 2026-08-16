from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

from config import *
from db_connection import connection_properties
from logger import logger

# Create Spark Session
spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SCD Type 1")
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

# Select required columns
dim_customer = (
    silver_df.select(
        "customer_id",
        "age",
        "job",
        "marital",
        "education",
        "balance"
    )
    .withColumn("updated_at", current_timestamp())
)

logger.info("Writing Dimension Table...")

(
    dim_customer.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.dim_customer",
        properties=connection_properties
    )
)

logger.info("Dimension Table Loaded Successfully!")

spark.stop()
