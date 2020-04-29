import flask
import cgi
import json
import threading
import logging
from queue import Queue
from collections import defaultdict
from kafka import KafkaConsumer
from flask_cors import CORS, cross_origin

app = flask.Flask(__name__)
app.config["DEBUG"] = True
logging.getLogger('flask_cors').level = logging.DEBUG
CORS(app, resources={r"*": {"origins": "*"}})

class EventsConsumer(object):
    def __init__(self, event_publisher):
        self.event_publisher = event_publisher
        self.consumer = KafkaConsumer(
            'test',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    
    def listen(self):
        logging.info('starting the listen thread')
        for message in self.consumer:
            message = message.value
            self.event_publisher.emit_broadcast(message, message['external_tenant'])

    def start(self):
        '''
        create new thread to avoid blocking the flask server
        '''
        self.message_listenner = threading.Thread(target=self.listen, args=())
        self.message_listenner.start()
        
    

class EventPublisher(object):
    END_STREAM = {}
    def __init__(self):
        '''
        new event publisher for users
        initialize with empty list
        '''
        self.users_by_channel = defaultdict(list)
    
    def get_channel_users(self, channel='broadcast'):
        '''
        get list if users for specific channel
        '''
        return self.users_by_channel[channel]

    def emit_single_user(self, data, queue):
        """
        Emits event only to a single user
        """
        event_id = data["event"]
        str_data = json.dumps(data)
        queue.put('event: ' + event_id)
        queue.put('\n')
        queue.put('data: ' + str_data)
        queue.put('\n\n')

    def emit_broadcast(self, data, channel='broadcast'):
        '''
        global emitor for every connected user to a channel
        '''
        if callable(data):
            for queue, properties in self.get_channel_users(channel):
                value = data(properties)
                if value:
                    self.emit_single_user(value, queue)
        else:
            for queue, _ in self.get_channel_users(channel):
                self.emit_single_user(data, queue)

    def join_channel(self, channel, properties=None, initial_data=[]):
        '''
        every user will be joined to the broadcast channel and custom one
        custom channel represents tenant 
        '''
        queue = Queue()
        properties = properties or {}
        subscriber = (queue, properties)

        '''
        we can emit some initial events right after user subscribes to the event stream
        '''
        for data in initial_data:
            self.emit_single_user(data, queue)
        
        '''
        add user to channles
        '''
        self.users_by_channel['broadcast'].append(subscriber)
        self.users_by_channel[channel].append(subscriber)

        return self.generate_emittor(queue)
    
    def generate_emittor(self,queue):
        '''
        generates events until the END_STREAM is called
        '''
        while True:
            data = queue.get()
            if data is EventPublisher.END_STREAM:
                return
            yield data

    def close(self):
        '''
        closes all connections
        '''
        for channel in self.users_by_channel.values():
            for queue, _ in channel:
                queue.put(EventPublisher.END_STREAM)
            channel.clear()


if __name__ == '__main__':
    event_publisher = EventPublisher()
    consumer = EventsConsumer(event_publisher)
    consumer.start()

    @app.route('/', methods=['GET'])
    def home():
        return flask.send_from_directory('./', 'index.html')
    
    @app.route('/subscribe', methods=['GET'])
    @cross_origin(origin='*')
    def subscribe():
        username =  flask.request.args.get('username')
        channel =  flask.request.args.get('channel')
        return flask.Response(event_publisher.join_channel(properties=username, channel=channel),
                                content_type='text/event-stream')


    app.run(host="localhost", port=5002, debug=True)