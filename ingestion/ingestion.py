import config
from confluent_kafka import Producer
import alpaca_trade_api as tradeapi
import logging
import json

log = logging.getLogger()

log.info("Starting ingestion MS")

p = Producer({"bootstrap.servers": config.KAFKA_HOST})
base_url = config.BASE_URL


api = tradeapi.REST(
    config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, base_url, api_version="v2"
)


conn = tradeapi.stream.Stream(
    key_id=config.ALPACA_API_KEY,
    secret_key=config.ALPACA_SECRET_KEY,
    base_url=base_url,
    data_feed="iex",
)

async def ingest(q):
    p.produce(topic="raw-data",
              value= json.dumps(q.__dict__['_raw']))

    p.flush() 


conn.subscribe_quotes(ingest, config.STOCK_CODE)
log.info(f"Subscribed to quote {config.STOCK_CODE}")

conn.run()
