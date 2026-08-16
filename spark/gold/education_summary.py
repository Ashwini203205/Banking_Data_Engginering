education_df = (
    silver_df
    .groupBy("education")
    .agg(count("*").alias("total_customers"))
)

(
    education_df.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.education_summary",
        properties=connection_properties
    )
)