# Deposit Summary
gold_df = (
    silver_df
    .groupBy("y")
    .agg(count("*").alias("total_customers"))
)

(
    gold_df.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.deposit_summary",
        properties=connection_properties
    )
)

# -----------------------------
# Job Summary
# -----------------------------
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

logger.info("Job Summary Loaded Successfully!")