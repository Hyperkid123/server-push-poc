from kafka import KafkaProducer
import flask
from flask import request, send_from_directory
import json

# create kafka producer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
  return send_from_directory('./', 'index.html')

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