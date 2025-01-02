from university.socket.participant import Participant

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.participants = {}
        
    def add_client(self, participant: Participant):
        self.participants[participant.sid] = participant
        
    def remove_client(self, sid):
        del self.participants[sid]
        
    def no_participants(self):
        return self.participants == []
    
    def to_json(self):
        return {
            'participants': list(map(Participant.to_json, self.participants.values()))
        }
    