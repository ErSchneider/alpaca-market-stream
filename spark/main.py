from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
import config
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

packages = [
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2",
    "org.apache.kafka:kafka-clients:3.2.1",
]

spark = (
    SparkSession.builder.master("local")
    .appName(config.APPNAME)
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

influxdb_client = InfluxDBClient(
    url=config.INFLUXDB_HOST,
    token=config.INFLUXDB_TOKEN,
    org=config.INFLUXDB_ORG,
    username=config.INFLUXDB_USERNAME,
    password=config.INFLUXDB_PASSWORD   
)

query = (
    aggregated_df.writeStream
    .outputMode("complete")
    .foreachBatch(lambda df, batch_id: write_to_influxdb(df, batch_id))
    .start()
)

def write_to_influxdb(df, batch_id):
    pandas_df = df.toPandas()

    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    for _, row in pandas_df.iterrows():
        point = Point('testmeasurement') \
            .time(row['window']['start'], WritePrecision.NS) \
            .field("min_spread", row['min_spread']) \
            .field("max_spread", row['max_spread']) \
            .field("avg_spread", row['avg_spread']) \
            .field("sample_size", row['sample_size'])
        write_api.write(bucket=config.INFLUXDB_BUCKET, record=point)


query.awaitTermination()