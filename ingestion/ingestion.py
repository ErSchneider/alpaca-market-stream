import config
from confluent_kafka import Producer
import alpaca_trade_api as tradeapi

p = Producer({"bootstrap.servers": config.KAFKA_HOST})
base_url = "https://paper-api.alpaca.markets"


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

    p.produce("raw-data", str(q))

    p.flush() 


conn.subscribe_quotes(ingest, "TUI1")##AAPL
conn.run()