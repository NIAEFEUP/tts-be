import os
import socketio
from urllib.parse import parse_qs

from university.socket.sessionsserver import SessionsServer

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
    session_id = query_params.get('session_id', None)
    session_id = session_id[0] if session_id else None
    
    if session_id is None:
        await sessions_server.create_session(sid)
    
        session_id = sessions_server.get_client_session(sid)
        print(f"Session created: {session_id}")
    else:
        await sessions_server.enter_session(sid, session_id)
        print(f"Client {sid} joined session {session_id}")
    
    await sessions_server.emit('connected', { 'session_id' : session_id }, to=sid)


@sessions_server.event
async def disconnect(sid):
    await sessions_server.leave_session(sid)
    print('Client disconnected')

# TODO: Remove this
@sessions_server.event
async def ping(sid, data):
    await sessions_server.emit('ping', {
        'id': data[0]['id'],    
    }, session_id=data[0]['session_id'])
    