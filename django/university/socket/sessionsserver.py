from typing import Coroutine
from random import randbytes
import socketio
from socketio.exceptions import ConnectionRefusedError

class SessionsServer:
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.sessions = {}

    def valid_token(self, token: str) -> bool:
        return True
        
    def event(self, event):
        return self.sio.event(event)
    
    def emit(self, event, data, to=None, session_id=None):
        return self.sio.emit(event, data, to=to, room=session_id)
    
    def generate_session_id(self):
        while True:
            session_id = randbytes(4).hex().upper()
            if session_id not in self.sessions:
                return session_id
    
    def create_session(self, sid) -> Coroutine:        
        if self.get_client_session(sid):
            raise ConnectionRefusedError('Client is already in a session')
        
        session_id = self.generate_session_id()
        self.sessions.setdefault(session_id, [])
        self.sessions[session_id].append(sid)
        
        return self.sio.enter_room(sid, session_id)
    
    def enter_session(self, sid, session_id) -> Coroutine:
        if self.get_client_session(sid):
            raise ConnectionRefusedError('Client is already in a session')
        
        if session_id not in self.sessions:
            print(self.sessions)
            raise ConnectionRefusedError('Session is empty')
        
        return self.sio.enter_room(sid, session_id)
    
    def leave_session(self, sid) -> Coroutine:
        session_id = self.get_client_session(sid)
        return self.sio.leave_room(sid, session_id)
    
    def get_client_session(self, sid):
        client_session = self.sio.rooms(sid)
        return client_session[1] if len(client_session) >= 2 else None