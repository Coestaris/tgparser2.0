from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    return database.get_profile_pictures()
