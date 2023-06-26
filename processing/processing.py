from confluent_kafka import Consumer, Producer
import time
import config
import json
from datetime import datetime  
import logging

log = logging.getLogger()

log.info("Waiting for kafka to start")
time.sleep(20)

c = Consumer({'bootstrap.servers': config.KAFKA_HOST,
             'group.id': 'python-consumer', 'auto.offset.reset': 'earliest'})
p = Producer({'bootstrap.servers': config.KAFKA_HOST})

c.subscribe(['raw-data'])


current_batch_second = None
current_batch = []

def process(input_data):
    global current_batch
    global current_batch_second

    spread = input_data['ask_price'] - input_data['bid_price']
    current_second = datetime.fromtimestamp(input_data['timestamp'] // 1000000000) # floor to second, input data in UTC

    if current_second == current_batch_second:
        current_batch.append(spread)
        return
    
    else:
        #prevent division by zero attempt
        if (len(current_batch) == 0): 
            ret = None
        else:
            ret =  {'datetime': current_second
                    ,'average_spread': sum(current_batch) / (len(current_batch))
                    ,'minimum_spread': min(current_batch)
                    , 'maximum_spread': max(current_batch)}

        #reset batch
        current_batch = []
        current_batch_second = current_second
        return json.dumps(ret, default=str)


i = 0
while True:
    if i % 10 == 0:
        p.flush()
    input = c.poll()
    if input is None:
        continue
    if input.error():
        log.error(input.error())
        continue

    input_data = json.loads(input.value().decode('utf-8').replace("Quote(", "").replace(")", "").replace("'", '"'))
    output_data = process(input_data)
        
    if output_data:
        p.produce('processed-data', output_data.encode('utf-8'))
    i+=1