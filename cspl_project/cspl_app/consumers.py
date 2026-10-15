import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveMatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'match_{self.match_id}'

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

    # Scorer delivery broadcast receiver
    async def match_update(self, event):
        payload = event.get('data', {})
        await self.send(text_data=json.dumps(payload))