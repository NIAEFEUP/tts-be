class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.clients = []
        
    def add_client(self, client):
        self.clients.append(client)
        
    def remove_client(self, client):
        self.clients.remove(client)
        
    def is_empty(self):
        return self.clients == []
    
    def to_json(self):
        return {
            'session_id': self.session_id,
            'clients': self.clients,
        }
    