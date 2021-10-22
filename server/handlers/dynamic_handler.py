import importlib
import logging
import traceback
from inspect import getmembers, isfunction

from server.handlers.request_handler import RequestHandler
import pkgutil
import server.handlers.dynamicHandlers


class DynamicHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/html'

    def find(self, route_data):
        class_name = route_data['route']['file']

        names = [name for _, name, _ in pkgutil.iter_modules(server.handlers.dynamicHandlers.__path__)]
        if class_name in names:
            handler_module = importlib.import_module("server.handlers.dynamicHandlers." + class_name)
            functions = getmembers(handler_module, isfunction)
            for name, fn in functions:
                if name == 'handle':
                    try:
                       self.contents = fn(self, route_data['body'], route_data['database'])
                    except Exception as e:
                        print(traceback.format_exc())
                        logging.error('Dynamic handler failed with next error: %s', str(e))
                        self.set_status(500)
                        return False
            self.set_status(200)
            return True
        else:
            self.set_status(404)
            return False

    def get_contents(self):
        return self.contents

