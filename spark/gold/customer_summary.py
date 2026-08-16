from pyspark.sql.functions import count, avg, sum, when

customer_summary = (
    silver_df
    .agg(
        count("*").alias("total_customers"),

        sum(
            when(silver_df.y == "yes", 1).otherwise(0)
        ).alias("subscribed_customers"),

        avg("age").alias("average_age"),

        avg("balance").alias("average_balance"),

        sum("balance").alias("total_balance")
    )
)

(
    customer_summary.write
    .mode("overwrite")
    .jdbc(
        url=JDBC_URL,
        table="gold.customer_summary",
        properties=connection_properties
    )
)