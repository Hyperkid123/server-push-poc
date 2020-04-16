from kafka import KafkaProducer
import flask
from flask import request
import json

# create kafka producer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
  return "<h1>Test server for kafka producer</h1>"

@app.route('/send-message', methods=["POST"])
def send_message():
  data = json.loads(request.data)
  print(data)
  producer.send('test', request.data)
  return request.data


app.run()

#print(producer)
#for _ in range(100):
#  

#producer.flush()