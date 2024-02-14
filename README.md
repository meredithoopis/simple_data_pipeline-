A data pipeline for reading news 
===============================

The data is crawled in real-time at [VNEXPRESS](https://e.vnexpress.net/)\
Once the service starts, the data crawled from the website will be streamed to a Kafka topic, then stored in a MongoDB database, and then streamed back again to Kafka for API usage: See the number of articles each day. 

### Requirements 
- WSL/ Device running on Linux
- A Confluent account: Create a cluster -> a new environment -> a topic and a key for access. [Reference](https://developer.confluent.io/get-started/python/)
- A MongoDB account: Create a cluster -> A database to connect. [Reference](https://www.mongodb.com/languages/python)
- A Ngrok account: Making your API accessible everywhere: Create an account and endpoint
- Take the necessary credentials and put them into the .env file 

### How-to 
Clone this repository, create a virtual environment(python 3.9), and run:  
```bash
pip install -r requirements.txt
```

### For running services individually 
1. Running Kafka: Uncomment Uncomment three functions in the following file and run: 
```bash
python test_kafka.py
```
2. Open another terminal, to see the API run:
```bash
python api.py
```
3. To make the API available everywhere, after installing and configuring Ngrok, open a terminal and run: 
```bash
ngrok http 8000
```
and go to the website to see the publicly available API 

### Running Airflow for all: 
Install and set up Airflow: [Airflow](https://www.restack.io/docs/airflow-knowledge-apache-ubuntu-install-server-22-04-20-04-18-04) (Make sure to put the dags folder in the Airflow config file)\ 

Open a terminal and run: 
```bash 
airflow scheduler
```
Open another terminal and run: 
```bash 
airflow webserver
```
to see the UI 


