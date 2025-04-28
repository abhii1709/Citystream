import requests
import json
import threading
from confluent_kafka import Producer


locations = {
    "Mcloed Ganj":"citystream-mcleodganj",
    "Naddi":"citystream-naddi",
    "Kachehri Chowk":"citystream-kachehri-chowk",
    "Dharamkot":"citystream-dharamkot",
    "Sidhpur":"citystream-sidhpur",
    "Dari":"citystream-dari",
    "Dal Lake":"citystream-dal-lake",
    "Education Board":"citystream-education",
    "Bhagsu Nag":"citystream-bhagsunag",
    "Sakoh":"citystream-sakoh"
}
API_URL ="http://fastapi:8081/records"
PAGE_SIZE = 1000
NUM_THREADS =5


producer_config ={
    "bootstrap.servers":"kafka1:29092,kafka2:29093,kafka3:29094",
    "client.id" :"traffic_data_producer",
     "acks" :'all',
    "batch.size": 16384,
    "linger.ms":5,
    'queue.buffering.max.messages': 1000000
}
producer =Producer(producer_config)
def delivery_report(err,msg):
    if err is not None:
        print(f"Message delivery failed:{err}")
    else:
        print(f"msg delivered to{msg.topic()} [{msg.partition()}]")

def fetch_page(page_num):
    params ={"page":page_num,"size":PAGE_SIZE}
    response = requests.get(API_URL,params=params)
    if response.status_code == 200:
        return response.json()
    return[]

def process_and_publish(page_num):
    data = fetch_page(page_num)
    batch=[]

    for record in data:
        location = record.get("location")
        topic = locations.get(location)
        if topic:
            key =str(location).encode('utf-8')
            value = json.dumps(record).encode(('utf-8'))
            batch.append((topic,key,value))
    for topic,key,value in batch:
        producer.produce(topic,key=key,value=value,callback=delivery_report)

    producer.flush()
    print(f" Sent {len(batch)} records from Page {page_num}")

def start_producer():
    """ Run multiple threads to fetch and publish data """
    print(" Starting Kafka producer with multi-threading...")

    threads = []
    for page in range(1, NUM_THREADS + 1):
        thread = threading.Thread(target=process_and_publish, args=(page,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(" Data ingestion completed.")

# Run Producer
if __name__ == "__main__":
    start_producer()