marital_df = (
    silver_df
    .groupBy("marital")
    .agg(count("*").alias("total_customers"))
)

(
    marital_df.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.marital_summary",
        properties=connection_properties
    )
)