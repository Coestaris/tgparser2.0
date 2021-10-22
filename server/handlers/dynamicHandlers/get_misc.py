from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    return {
        'freq_contacts': database.get_freq_contacts(),
        'created_stickers': [x['url'] for x in database.get_created_stickers()],
        'installed_stickers': [x['url'] for x in database.get_installed_stickers()],
        'ips': [x['ip'] for x in database.get_ips()],
    }
