import os
import socketio

from university.socket.sessionsserver import SessionsServer

async_mode = None

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
)

session_server = SessionsServer(sio)
        
@session_server.event
async def connect(sid, environ, auth):
    if session_server.valid_token(auth['token']):
        print('Client connected')
        await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)
    else:
        raise ConnectionRefusedError('Authentication failed: Invalid token')


@session_server.event
def disconnect(sid):
    print('Client disconnected')
    
@session_server.event
async def test(sid, environ):
    await sio.emit('response', 'ya')