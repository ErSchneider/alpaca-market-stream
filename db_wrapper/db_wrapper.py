from confluent_kafka import Consumer
import config
import sqlite3
import json
from datetime import datetime

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
        , average_spread FLOAT
        , minimum_spread FLOAT
        , maximum_spread FLOAT
    )"""
    )
    return cur, con

def insert(cur, con, data):
    data = [
        datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S"),
        data["average_spread"],
        data["minimum_spread"],
        data["maximum_spread"],
    ]
    cur.execute("INSERT INTO Aggregated_spreads_in_v0 VALUES(?,?,?,?)", data)
    con.commit()


cur, con = set_up_db()

while True:
    input = c.poll()
    if input is None:
        continue
    if input.error():
        print(f"Error {input.error()}")
        continue

    data = json.loads(input.value().decode("utf-8"))

    insert(cur, con, data)