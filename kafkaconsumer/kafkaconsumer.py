import json
import boto3
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import time
from confluent_kafka import Consumer
from io import BytesIO
import threading
import os
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FOLDER = "traffic_data/"
REGION_NAME = os.getenv("AWS_REGION")

# Kafka Configuration
KAFKA_BROKER = "kafka1:29092,kafka2:29093,kafka3:29094"
TOPIC_LIST = [
    "citystream-mcleodganj",
    "citystream-naddi",
    "citystream-kachehri-chowk",
    "citystream-dharamkot",
    "citystream-sidhpur",
    "citystream-dari",
    "citystream-dal-lake",
    "citystream-education",
    "citystream-bhagsunag",
    "citystream-sakoh"

]
GROUP_ID = "citystream-s3-group"
BATCH_SIZE = 50  # Messages per batch
UPLOAD_INTERVAL = 30  # Upload every 30 seconds

# Initialize S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)


def convert_to_parquet(data):
    """
    Convert JSON data to Parquet format using Pandas and PyArrow.
    """
    df = pd.DataFrame(data)

    # Define Parquet schema
    schema = pa.schema([
        ("timestamp", pa.string()),
        ("location", pa.string()),
        ("vehicle_count", pa.string()),
        ("avg_speed_kmph", pa.string()),
        ("congestion_level", pa.string()),
        ("weather", pa.string()),
        ("accidents_reported", pa.string())
    ])

    # Convert DataFrame to Parquet
    table = pa.Table.from_pandas(df, schema=schema)

    output = BytesIO()
    pq.write_table(table, output, compression="snappy")
    return output.getvalue()


def upload_to_s3(data, topic):
    """
    Upload Kafka messages to S3 in Parquet format.
    """
    try:
        timestamp = int(time.time())
        file_key = f"{S3_FOLDER}{topic}_{timestamp}.parquet"

        parquet_data = convert_to_parquet(data)

        s3_client.put_object(Bucket="citystream-kafkaconsumer-data", Key=file_key, Body=parquet_data)
        print(f" Data uploaded to S3: s3://{BUCKET_NAME}/{file_key}")
    except Exception as e:
        print(f" S3 Upload Failed: {e}")


def consume_messages(topic):
    """
    Read messages from Kafka topics and upload to S3 in batches.
    """
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe([topic])

    messages = []
    last_upload_time = time.time()

    try:
        print(f" Listening for Kafka messages on {topic}...")
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f" Kafka Error: {msg.error()}")
                continue

            value = json.loads(msg.value().decode("utf-8"))
            messages.append(value)

            # Upload data in batches or at set time intervals
            if len(messages) >= BATCH_SIZE or (time.time() - last_upload_time) >= UPLOAD_INTERVAL:
                upload_to_s3(messages, topic)
                messages = []  # Clear batch after upload
                last_upload_time = time.time()

    except KeyboardInterrupt:
        print(f"\n Stopping Kafka Consumer for {topic}...")
    finally:
        consumer.close()


# Start Consuming Messages with Multithreading
threads = []
for topic in TOPIC_LIST:
    thread = threading.Thread(target=consume_messages, args=(topic,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()