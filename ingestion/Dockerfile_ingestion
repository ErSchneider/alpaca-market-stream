FROM python:3.8.8
RUN pip install confluent_kafka websocket-client 
RUN pip install alpaca_trade_api
RUN apt-get update && apt-get install -y iputils-ping nmap 
ADD ingestion/ingestion.py /
ADD config.py /
CMD [ "python", "./ingestion.py" ]