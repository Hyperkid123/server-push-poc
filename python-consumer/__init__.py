from kafka import KafkaConsumer
from json import loads
from json import dumps
import asyncio
import websockets

consumer = KafkaConsumer(
    'test',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

async def ws_service(websocket, path):
    for message in consumer:
        message = message.value
        await websocket.send(dumps(message))
        print(message)

start_server = websockets.serve(ws_service, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
