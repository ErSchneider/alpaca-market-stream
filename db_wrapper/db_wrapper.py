from confluent_kafka import Consumer
import config
import sqlite3
import json
from datetime import datetime
import logging

log = logging.getLogger()

log.info("Waiting for kafka to start")

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
        datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S"),
        data['stock_code'],
        data["average_spread"],
        data["minimum_spread"],
        data["maximum_spread"],
        data["sample_size"]
    ]
    cur.execute("INSERT INTO Aggregated_spreads_in_v0 VALUES(?,?,?,?,?,?)", data)
    con.commit()


cur, con = set_up_db()

while True:
    input = c.poll()
    data = json.loads(input.value().decode("utf-8"))

    if input.error():
        log.error(input.error())
        continue
    if not data:
        log.warning("No data")
        continue

    insert(cur, con, data)
