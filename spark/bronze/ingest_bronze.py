from pyspark.sql import SparkSession

print("=" * 60)
print("BANKING ANALYTICS - BRONZE LAYER")
print("=" * 60)

# Create Spark Session
spark = SparkSession.builder \
    .appName("Banking Bronze Layer") \
    .master("local[*]") \
    .getOrCreate()

print("\n✓ Spark Session Created Successfully")

# Read CSV
df = spark.read.csv(
    "data/source/bank-full.csv",
    header=True,
    inferSchema=True,
    sep=";"
)

print("\n✓ Dataset Loaded Successfully")

print("\nFirst 5 Records")
df.show(5, truncate=False)

print("\nDataset Schema")
df.printSchema()

print("\nTotal Records :", df.count())
print("Total Columns :", len(df.columns))

print("\nColumn Names")
print(df.columns)

spark.stop()

print("\n✓ Spark Session Closed")