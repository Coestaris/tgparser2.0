from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    chats = database.get_chats()
    messages = database.get_messages()
    result = []
    for chat in chats:
        result.append({
            'messages_count': chat.messages_count,
            'members': chat.members,
            'name': chat.name,
            'type': chat.type,
            'id': chat.id
        })
    result.sort(key=lambda x: x['messages_count'], reverse=True)
    return result
