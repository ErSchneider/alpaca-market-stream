from confluent_kafka import Consumer
import config
import sqlite3

c = Consumer({'bootstrap.servers': config.KAFKA_HOST,
             'group.id': 'python-consumer', 'auto.offset.reset': 'earliest'})

c.subscribe(['processed-data'])


def set_up_db():
    con = sqlite3.connect("reporting.db") 
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Quotes (x,y,z)")
    return cur

def insert(cur, data):
    cur.executemany("INSERT INTO Quotes VALUES(?,?,?)", data) # https://docs.python.org/3/library/sqlite3.html#:~:text=executemany(%22-,INSERT%20INTO%20movie%20VALUES,-(%3F%2C%20%3F%2C%20%3F)%22%2C%20data


cur = set_up_db()

while True:
    msg = c.poll()
    if msg is None:
        continue
    if msg.error():
        print('Error: {}'.format(msg.error()))
        continue

    data = msg.value().decode('utf-8')
    #insert(cur, data)
    #print("recieved processed data", data)        

