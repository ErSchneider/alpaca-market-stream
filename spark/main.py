import pyspark
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
import config

packages = [
    f"org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2",
    "org.apache.kafka:kafka-clients:3.2.1",
]

spark = (
    SparkSession.builder.master("local")
    .appName("kafka-example")
    .config("spark.jars.packages", ",".join(packages))
    .getOrCreate()
)

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", config.KAFKA_HOST)
    .option("subscribe", "raw-data")
    .load()
)

schema = (
    StructType()
    .add("symbol", StringType())
    .add("bid_exchange", StringType())
    .add("bid_price", DoubleType())
    .add("bid_size", IntegerType())
    .add("ask_exchange", StringType())
    .add("ask_price", DoubleType())
    .add("ask_size", IntegerType())
    .add("conditions", ArrayType(StringType()))
    .add("tape", StringType())
    .add("timestamp", LongType())
)

df = df.withColumnRenamed("value", "raw_value")

df = df.withColumn("raw_value", df["raw_value"].cast(StringType()))

deserialized_df = df.withColumn("deserialized_value", from_json(df.raw_value, schema))

extracted_df = deserialized_df.select("deserialized_value.*")

extracted_df = extracted_df.withColumn(
    "timestamp", (extracted_df["timestamp"] / 1000000000).cast(TimestampType())
)

extracted_df = extracted_df.withColumn("spread", col("ask_price") - col("bid_price"))

extracted_df = extracted_df.select("timestamp", "spread")

aggregated_df = (
    extracted_df.withWatermark("timestamp", "1 second")
    .groupBy(window(col("timestamp"), "1 second"))
    .agg(
        expr("min(spread) as min_spread"),
        expr("max(spread) as max_spread"),
        expr("avg(spread) as avg_spread"),
        count("*").alias("sample_size")
    )
)


# to console
# query = aggregated_df \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .option("truncate", False) \
#     .start()


kafka_producer_properties = {
    "kafka.bootstrap.servers": config.KAFKA_HOST,
    "value.serializer": "org.apache.kafka.common.serialization.StringSerializer",
}

aggregated_df.selectExpr(
    "CAST(window AS STRING) AS key",
    "to_json(struct(*)) AS value"
).writeStream.format("kafka").option(
    "kafka.bootstrap.servers", config.KAFKA_HOST
).option("topic", "processed-data").option(
    "checkpointLocation", "/tmp/checkpoint"
).start().awaitTermination()