from typing import Coroutine
from random import randbytes
import socketio

class SessionsServer:
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.rooms = {}

    def valid_token(self, token: str) -> bool:
        return True
        
    def event(self, event):
        return self.sio.event(event)
    
    def emit(self, event, data, **kwargs):
        return self.sio.emit(event, data, **kwargs)
    
    def generate_room_id(self):
        while True:
            room_id = randbytes(4).hex().upper()
            if room_id not in self.rooms:
                return room_id
    
    def create_room(self, sid) -> Coroutine:        
        if self.get_client_room(sid):
            raise ConnectionError('Client is already in a room')
        
        room_id = self.generate_room_id()
        self.rooms.setdefault(room_id, [])
        self.rooms[room_id].append(sid)
        
        return self.sio.enter_room(sid, room_id)
    
    def enter_room(self, sid, room_id) -> Coroutine:
        if self.get_client_room(sid):
            raise ConnectionError('Client is already in a room')
        
        if room_id not in self.rooms:
            print(self.rooms)
            raise ConnectionError('Room is empty')
        
        return self.sio.enter_room(sid, room_id)
    
    def leave_room(self, sid) -> Coroutine:
        room_id = self.get_client_room(sid)
        return self.sio.leave_room(sid, room_id)
    
    def get_client_room(self, sid):
        client_room = self.sio.rooms(sid)
        return client_room[1] if len(client_room) >= 2 else None