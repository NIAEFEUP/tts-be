from university.socket.participant import Participant
from datetime import datetime
from datetime import timedelta

class Session:
    def __init__(self, session_id: str, duration: timedelta = timedelta(days=30)):
        self.session_id = session_id
        self.participants = {}
        self.expire_datetime = datetime.now() + duration
        
    def add_client(self, participant: Participant):
        self.participants[participant.sid] = participant
        
    def remove_client(self, sid):
        del self.participants[sid]
        
    def update_client(self, participant: Participant):
        self.participants[participant.sid] = participant
        
    def no_participants(self):
        return self.participants == []
    
    def expired(self):
        return datetime.now() > self.expire_datetime
    
    def to_json(self):
        return {
            'expire_datetime': self.expire_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'participants': list(map(Participant.to_json, self.participants.values()))
        }
    