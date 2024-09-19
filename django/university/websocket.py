from channels.generic.websocket import WebsocketConsumer

class TestConsumer(WebsocketConsumer):
    def connect(self):
        print("Connected")
        
        self.accept()

    def disconnect(self, close_code):
        print("Disconnected")

    def receive(self, text_data):
        self.send(text_data=text_data)

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=message)