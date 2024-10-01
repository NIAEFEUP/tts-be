import os
import socketio

async_mode = None

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
)
        
@sio.event
async def connect(sid, environ):
    print('Client connected')
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')
    
@sio.event
async def test(sid, environ):
    await sio.emit('response', 'ya')