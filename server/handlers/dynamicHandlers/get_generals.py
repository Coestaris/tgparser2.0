from datetime import datetime

from database.database import DB
from database.entities.message import Message
from server.handlers.dynamic_handler import DynamicHandler


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    messages = database.get_messages()
    id = database.get_id()

    total_sent = 0
    total_received = 0

    m = datetime.now()
    for message in messages:
        if message.accepts_filter(body) and not message.is_service():
            if message.is_output(id):
                total_sent += 1
                m = min(message.date, m)
            elif message.is_input(body):
                total_received += 1

    from_first_message = datetime.now().timestamp() - m.timestamp()
    days = from_first_message / 86400
    messages_in_day = total_sent / days

    return {
        'total_sent': total_sent,
        'total_received': total_received,
        'from_first_message': from_first_message,
        'messages_in_day': messages_in_day
    }
