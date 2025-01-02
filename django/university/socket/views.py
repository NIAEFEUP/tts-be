import os
import socketio
from urllib.parse import parse_qs

from university.socket.sessionsserver import SessionsServer

async_mode = None

basedir = os.path.dirname(os.path.realpath(__file__))

sessions_server = SessionsServer(
    socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins="*",
    )
)

@sessions_server.event
async def connect(sid, environ, auth):
    if auth is None or 'token' not in auth:
        raise ConnectionRefusedError('Authentication failed: No token provided')
    if not sessions_server.valid_token(auth['token']):
        raise ConnectionRefusedError('Authentication failed: Invalid token')
    
    print('Client connected')
    
    query_params = parse_qs(environ.get("QUERY_STRING", ""))
    room_id = query_params.get('room_id', None)
    room_id = room_id[0] if room_id else None
    
    if room_id is None:
        await sessions_server.create_room(sid)
    
        room_id = sessions_server.get_client_room(sid)
        print(f"Room created: {room_id}")
    else:
        await sessions_server.enter_room(sid, room_id)
        print(f"Client {sid} joined room {room_id}")
    
    await sessions_server.emit('connected', { 'room_id' : room_id }, to=sid)


@sessions_server.event
async def disconnect(sid):
    await sessions_server.leave_room(sid)
    print('Client disconnected')

# TODO: Remove this
@sessions_server.event
async def ping(sid, data):
    await sessions_server.emit('ping', {
        'id': data[0]['id'],    
    }, room=data[0]['room_id'])
    