import uuid

class SessionsServer:
    def __init__(self, sio):
        self.sio = sio

    def valid_token(self, token):
        return True
        
    def event(self, event):
        return self.sio.event(event)