from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    messages = database.get_messages()
    id = database.get_id()

    input_messages = {}
    output_messages = {}

    for message in messages:
        if message.accepts_filter(body) and not message.is_service():
            key = message.date.isocalendar()[1] + message.date.year * 100
            if message.is_output(id):
                if key not in input_messages:
                    input_messages[key] = 1
                else:
                    input_messages[key] += 1
            elif message.is_input(body):
                if key not in output_messages:
                    output_messages[key] = 1
                else:
                    output_messages[key] += 1

    keys = list(set(input_messages.keys()).union(output_messages.keys()))
    keys.sort()
    input_messages_res = []
    output_messages_res = []

    for key in keys:
        if key in input_messages:
            input_messages_res.append(input_messages[key])
        else:
            input_messages_res.append(0)
        if key in output_messages:
            output_messages_res.append(output_messages[key])
        else:
            output_messages_res.append(0)

    return {
        'keys': keys,
        'input': input_messages_res,
        'output': output_messages_res
    }