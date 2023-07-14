from confluent_kafka import Consumer
import config
import sqlite3
import json
from datetime import datetime
import logging

log = logging.getLogger()

log.info("Starting db_wrapper MS")

c = Consumer(
    {
        "bootstrap.servers": config.KAFKA_HOST,
        "group.id": "python-consumer",
        "auto.offset.reset": "earliest",
    }
)

c.subscribe(["processed-data"])


def set_up_db():
    con = sqlite3.connect("reporting.db")
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS Aggregated_spreads_in_v0 (
        datetime DATETIME
        , stock_code STRING
        , average_spread FLOAT
        , minimum_spread FLOAT
        , maximum_spread FLOAT
        , sample_size INT
    )"""
    )
    return cur, con

def insert(cur, con, data):
    data = [
        datetime.strptime(data["window"]["start"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        config.STOCK_CODE,
        data["avg_spread"],
        data["min_spread"],
        data["max_spread"],
        data["sample_size"]
    ]
    cur.execute("INSERT INTO Aggregated_spreads_in_v0 VALUES(?,?,?,?,?,?)", data)
    con.commit()



cur, con = set_up_db()


while True:
    message = c.poll(1.0)
    if message is None:
        continue
    if message.error():
        print(message.error())
        continue

    value = json.loads(message.value())

    insert(cur, con, value)
