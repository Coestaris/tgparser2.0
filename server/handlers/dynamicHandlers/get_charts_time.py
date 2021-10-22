from datetime import datetime

from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler


def create_dict(len):
    d1 = {}
    d2 = {}
    for i in range(0, len):
        d1[i] = 0
        d2[i] = 0
    return {'input': d1, 'output': d2}


def trim(mass, max_len):
    first = max_len + 1
    last = -1
    for k, v in mass.items():
        if v != 0:
            first = min(first, k)
            last = max(last, k)

    mass_res = {}
    for i in range(first, last + 1):
        mass_res[i] = mass[i]

    return mass_res


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    print(body)

    messages = database.get_messages()
    id = database.get_id()

    min_year = 2010
    years = datetime.now().year - min_year + 1

    hour_messages = create_dict(24)
    day_of_week_messages = create_dict(7)
    month_messages = create_dict(12)
    year_messages = create_dict(years)

    for message in messages:
        if message.accepts_filter(body) and not message.is_service():
            if message.is_output(id):
                key = 'output'
            elif message.is_input(body):
                key = 'input'
            else:
                continue
            hour_messages[key][message.date.hour] += 1
            day_of_week_messages[key][message.date.weekday()] += 1
            month_messages[key][message.date.month - 1] += 1
            year_messages[key][message.date.year - min_year] += 1

    hour_messages['keys'] = [str(x) for x in hour_messages['output'].keys()]
    hour_messages['input'] = list(hour_messages['input'].values())
    hour_messages['output'] = list(hour_messages['output'].values())

    day_of_week_messages['keys'] = [str(x) for x in day_of_week_messages['output'].keys()]
    day_of_week_messages['input'] = list(day_of_week_messages['input'].values())
    day_of_week_messages['output'] = list(day_of_week_messages['output'].values())

    month_messages['keys'] = [str(x) for x in month_messages['output'].keys()]
    month_messages['input'] = list(month_messages['input'].values())
    month_messages['output'] = list(month_messages['output'].values())

    input = trim(year_messages['input'], years)
    year_messages['keys'] = [min_year + x for x in input.keys()]
    year_messages['input'] = list(input.values())
    year_messages['output'] = list(trim(year_messages['output'], years).values())

    return {
        'hour': hour_messages,
        'day_of_week': day_of_week_messages,
        'month': month_messages,
        'year': year_messages,
    }
