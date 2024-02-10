from airflow import DAG 
from airflow.operators.python import PythonOperator 
from datetime import datetime, timedelta 
#from pytz import timezone 
import os 
import sys 
from pathlib import Path 
from dotenv import load_dotenv 
from confluent_kafka import Producer, Consumer, TopicPartition 
import socket 
import json 
from pymongo import MongoClient 
from pymongo.server_api import ServerApi
sys.path.append("/home/meredith/apps/stream")
from crawl import Crawler
#from test_kafka import producing, stream_to_mongo, mongo_to_kafka
#Start on ubuntu: airflow scheduler -> airflow webserver 
default_args = {
    'owner': 'airflow', 
    'email': 'nthhanh.work.02@gmail.com', 
    'email_on_failure': True, 
    'depends_on_past': False, 
    #'start_date': datetime.today() - timedelta(days=1), 
    #'retries': 1, 
    #'retry_delay': timedelta(minutes=5), 
    #'timezone': 'Asia/Ho_Chi_Minh'
    }

load_dotenv()
conf_prod = {
    'bootstrap.servers': os.getenv("kafka_server"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv("kafka_key"),
    'sasl.password': os.getenv("kafka_secret"),
    "client.id": socket.gethostname(),
    'enable.idempotence': True  # Not insert duplicate messages 
}

conf_cons = {
    'bootstrap.servers': os.getenv("kafka_server"),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv("kafka_key"),
    'sasl.password': os.getenv("kafka_secret"),
    'group.id': 'news-consumer', 
    'auto.offset.reset': 'earliest'
}
producer = Producer(conf_prod)
consumer = Consumer(conf_cons)
topic = "news"
#Connect to mongo + A small function to create a db and a collection: 
uri = "mongodb+srv://ng_dang_nhap:dang_nhap_ng@hanh.2qtl3cu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

#Send message to kafka topic 
def producing(): 
    #Started crawling: 
    crawl = Crawler() 
    crawl.main()
    articles = crawl.articles 
    for article in articles: 
        url, title, content, created_at = article 
        d = {
            "url": url, 
            "title": title, 
            "content": content, 
            "created_at": created_at
        }
        producer.produce(topic, json.dumps(d).encode('utf-8'), callback=acked)

    producer.flush()
    print("Number of messages produced: ", len(articles))
    #producer.close()
    return True


# Stream data from Kafka to mongodb 
def stream_to_mongo(): 
    db = client["news"]
    collection = db["vnexpress"]
    consumer.assign([TopicPartition(topic, 0)]) 
    try: 
        while True: 
            message = consumer.poll()
            if message is None: 
                print("No message received")
            if message.error(): 
                print("Error: {}".format(message.error())) 
            val = message.value().decode('utf-8')
            msg = json.loads(val) 
            print("Received message: {}".format(val)) 
            collection.insert_one(msg)
            print("Inserted to mongo")    

    except Exception as e: 
        print(e)
    finally:
        consumer.close()
    print("Number of collections: ", collection.count_documents({}))
    return True

#Stream data from mongo to kafka for fastapi  -> this is kinda stupid wont try 
def mongo_to_kafka(num_documents=10): 
    try: 
        db = client["news"]
        collection = db["vnexpress"]
        documents = collection.find().limit(num_documents)
        for document in documents: 
            producer.produce(topic, json.dumps(document).encode('utf-8'), callback=acked)
        producer.flush()
        print("Stream to Kafka ok")
        print("Putting {} documents to Kafka".format(num_documents))

    except Exception as e:
        print(e)
    return True


dag = DAG(
    "Daily_runs", 
    default_args = default_args, 
    description = "Crawling news each day", 
    start_date= datetime.today() - timedelta(days=1), 
    schedule= timedelta(days=1), 
    catchup=False, 
    #timezone = 'Asia/Ho_Chi_Minh'
)


produce_task = PythonOperator(
    task_id = "Crawling_to_Kafka", 
    python_callable = producing, 
    dag = dag
)

stream_task = PythonOperator(
    task_id = "Stream_to_mongo_task", 
    python_callable= stream_to_mongo, 
    dag = dag 
)
mongo_kafka_task = PythonOperator(
    task_id = "Mongo_to_kafka_task", 
    python_callable= mongo_to_kafka,
    dag= dag
)

produce_task >> stream_task >> mongo_kafka_task

