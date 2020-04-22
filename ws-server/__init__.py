import eventlet
import socketio
from json import loads

# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

# for standard WSGI applications
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    sio.enter_room(sid, environ["HTTP_X_RH_TENANT"]) 

@sio.event
def my_message(sid, data):
    print('message ', loads(data))
    message = loads(data)
    if 'tenant-scope' in message:
        sio.emit('my-message', data=data, room=message["tenant-scope"])
    else:
        sio.emit('my-message', data=data)
        

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)