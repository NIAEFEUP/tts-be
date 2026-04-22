import uuid

class Participant:
    def __init__(self, sid, name, selected_slots, nmec=None):
        self.sid = sid
        self.client_id = str(uuid.uuid4())
        self.name = name
        self.selected_slots = selected_slots or []
        self.nmec = nmec

    def to_json(self):
        return {
            'client_id': self.client_id,
            'name': self.name,
            'selected_slots': self.selected_slots,
        }

    @staticmethod
    def from_json(sid, data):
        if 'name' not in data:
            raise ValueError('name is required')
        return Participant(sid, data['name'], data.get('selected_slots', []), data.get('nmec'))

    def update_from_json(self, data):
        if 'name' in data:
            self.name = data['name']
        if 'selected_slots' in data:
            self.selected_slots = data['selected_slots']