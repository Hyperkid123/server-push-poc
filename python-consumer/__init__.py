from kafka import KafkaConsumer
from json import loads
from json import dumps
import asyncio
import websockets
import socketio

# ws client
sio = socketio.Client()
sio.connect('http://localhost:5001')

consumer = KafkaConsumer(
    'test',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

for message in consumer:
    message = message.value
    print(message)
    sio.emit('my_message', dumps(message))

