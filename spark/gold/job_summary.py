from pyspark.sql.functions import count

job_df = (
    silver_df
    .groupBy("job")
    .agg(count("*").alias("total_customers"))
)

(
    job_df.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.job_summary",
        properties=connection_properties
    )
)