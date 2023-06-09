alpaca-market-stream is a docker based streaming solution to calculate, aggregate and save the spread of a given stock in real time. The application revieces quotes from alpaca, the spread is calculated as the difference between ask and bid price and aggregated to seconds. For each second different metrics are calculated. The microservice architecure looks as follows:

![microservices](examples/microservices.png "Architecture")

### How to run

- To use it you need to obtain access to [alpaca.markets](https://alpaca.markets/), see the [getting started documentation](https://alpaca.markets/docs/market-data/getting-started/).
- [download and install docker](https://www.docker.com/products/docker-desktop/)
- create `config.py` using the `example_config.py` as a template
- fill in your alpaca key and secret
- change `STOCK_CODE` if needed
- create and activate a virtual environment if needed
- install requirements via `pip install -r requirements.txt`
- start docker
- start the application via docker compose `docker-compose up --build`

All resulting data can be found in the sqlite database `reporting.db` in the `db_wrapper` container

### Examples

The following plots show a full day (2023-06-27 within the opening hours of the stock exchange) of processing AAPL quotes. Data is displayed as moving average with a window of 120 seconds. Velocity peaked at 361 quotes per second.

![quotes](examples/processed_quotes.png )
![spreads](examples/aggregated_spreads.png )