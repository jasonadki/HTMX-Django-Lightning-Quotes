# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QuoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_identifier = self.scope['session'].get('user_token', 'anonymous')
        
        self.room_group_name = f'quotes_{self.user_identifier}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def quote_update(self, event):
        await self.send(text_data=json.dumps({
            'quote_id': event['quote_id'],
            'status': event['status'],
            'type': "quote.update",
        }))

