class Participant:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        
    def to_json(self):
        return {
            'name': self.name,
        }