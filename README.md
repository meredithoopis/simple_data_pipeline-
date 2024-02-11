# A data pipeline for reading news 

## About 
The data is crawled in real-time at [VNEXPRESS](https://e.vnexpress.net/)
Once the service starts, the data crawled from the website will be streamed to a Kafka topic, then stored in a MongoDB database, and then streamed back again to Kafka for API usage: See the number of articles each day 

## Requirement: 
WSL/ Device running on Linux\
A Confluent account: Create a cluster -> a new environment -> a topic and a key for access. [Reference](https://developer.confluent.io/get-started/python/)\
A MongoDB account: Create a cluster -> A database to connect. [Reference](https://www.mongodb.com/languages/python)
A Ngrok account: Making your API accessible everywhere: Create an account and endpoint 

## How-to 
Create a virtual environment(python==3.9)
Run "pip install -r requirements.txt"
### For running services individually 
Uncomment three functions in the test_kafka file and run the file 
Open another terminal, run the api.py to see the API 
For making the API available everywhere, after installing and configuring Ngrok: Open a terminal and run ngrok http 8000 and go to the website to see the publicly available API 
### Running Airflow for all: 
Install and set up Airflow: [Airflow](https://www.restack.io/docs/airflow-knowledge-apache-ubuntu-install-server-22-04-20-04-18-04) (Make sure to put the dags folder in the Airflow config file) 
Open a terminal and run: "airflow scheduler" 
Open another terminal and run: "airflow webserver" to see the UI 


