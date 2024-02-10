from fastapi import FastAPI, Query 
from confluent_kafka import Consumer, TopicPartition
import uvicorn
from test_kafka import conf_cons,topic
import json 
#Run ngrok.exe -> ngrok http 80 to start the service and get the public URL -> Windows
#Wsl: ngrok http 8000



app = FastAPI()
@app.get("/")
def get_root(): 
    return {"message": "This is a simple interface for streaming news"}

@app.get("/consume")
def consume_data(limit: int = Query(default=10, description="How many articles do you want to take?")): 
    consumer = Consumer(conf_cons)
    consumer.assign([TopicPartition(topic, 0)])
    messages = []
    while len(messages) < limit: 
        message = consumer.poll()
        if message is None: 
            continue 
        if message.error(): 
            print(f"Consumer error: {message.error()}")
            continue
        value = message.value().decode('utf-8')
        messages.append(value)
        #print(f"Consumed message: {value}")
    consumer.close()
    formatted_messages = []
    for m in messages: 
        formatted_messages.append(", ".join([f"{key}: {value}" for key, value in json.loads(m).items()]))
    return {"message": formatted_messages}

if __name__== "__main__": 
    #uvicorn.run(app, host="0.0.0.0", port=80)
    uvicorn.run(app)
    

    
