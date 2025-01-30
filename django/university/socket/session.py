from university.socket.participant import Participant
from datetime import datetime, timedelta, timezone
import time

class Session:
    def __init__(self, session_id: str, duration: timedelta = timedelta(days=30)):
        self.session_id = session_id
        self.participants = {}
        self.picked_courses = []
        self.multiple_options = [{"id":0,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0031-fe0f-20e3.png","name":"Horário 1","course_options":[],"chosen":False,"selected":False},{"id":1,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0032-fe0f-20e3.png","name":"Horário 2","course_options":[],"chosen":False,"selected":False},{"id":2,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0033-fe0f-20e3.png","name":"Horário 3","course_options":[],"chosen":False,"selected":False},{"id":3,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0034-fe0f-20e3.png","name":"Horário 4","course_options":[],"chosen":False,"selected":False},{"id":4,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0035-fe0f-20e3.png","name":"Horário 5","course_options":[],"chosen":False,"selected":False},{"id":5,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0036-fe0f-20e3.png","name":"Horário 6","course_options":[],"chosen":False,"selected":False},{"id":6,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0037-fe0f-20e3.png","name":"Horário 7","course_options":[],"chosen":False,"selected":False},{"id":7,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0038-fe0f-20e3.png","name":"Horário 8","course_options":[],"chosen":False,"selected":False},{"id":8,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/0039-fe0f-20e3.png","name":"Horário 9","course_options":[],"chosen":False,"selected":False},{"id":9,"icon":"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f51f.png","name":"Horário 10","course_options":[],"chosen":False,"selected":False}]
        self.expiration_datetime = datetime.now(timezone.utc) + duration
        
    def add_client(self, participant: Participant):
        self.participants[participant.sid] = participant
        
    def remove_client(self, sid):
        del self.participants[sid]
        
    def update_client(self, participant: Participant):
        self.participants[participant.sid] = participant
        
    def no_participants(self):
        return self.participants == []
    
    def expired(self):
        return datetime.now() > self.expiration_datetime
    
    def to_json(self):
        return {
            'expiration_time': int(time.mktime(self.expiration_datetime.timetuple())) * 1000.0,
            'picked_courses': self.picked_courses,
            'multiple_options': self.multiple_options,
            'participants': list(map(Participant.to_json, self.participants.values()))
        }
    