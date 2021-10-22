import logging
import os
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Tuple

import orjson

from database.database import DB
from server.handlers.dynamic_handler import DynamicHandler
from server.routes import routes
from server.handlers.bad_request_handler import BadRequestHandler
from server.handlers.file_handler import FileHandler
from server.handlers.static_handler import StaticHandler


def make_server(database):
    class Server(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super(Server, self).__init__(*args, **kwargs)

        def do_HEAD(self):
            return

        def do_response(self, type):
            split_path = os.path.splitext(self.path)
            requested_path = split_path[0]
            request_extension = split_path[1]

            found_handler = False
            handler = None

            for file, route in routes.items():
                if file == requested_path:
                    if type not in route['methods']:
                        handler = BadRequestHandler()
                        logging.error('Invalid method: %s allowed, but got "%s"', route['methods'], type)
                    else:
                        if route['type'] == 'static':
                            handler = StaticHandler()
                            handler.find(routes[self.path])
                        else:
                            content_len = int(self.headers.get('Content-Length'))
                            post_body = self.rfile.read(content_len)

                            handler = DynamicHandler()
                            handler.find(
                                {
                                    'database': database,
                                    'body': orjson.loads(post_body),
                                    'route': routes[self.path]
                                })
                        found_handler = True

            if not found_handler:
                handler = FileHandler()
                handler.find(self.path)

            self.respond({
                'handler': handler
            })
            pass

        def do_GET(self):
            self.do_response('get')
            pass

        def do_POST(self):
            self.do_response('post')
            pass

        def handle_http(self, handler):
            status_code = handler.get_status()

            self.send_response(status_code)

            if status_code == 200:
                content = handler.get_contents()
                self.send_header('Content-type', handler.get_content_type())
            else:
                if status_code == 404:
                    logging.error('Not found 404')
                    content = "404 Not Found"
                else:
                    logging.error('Internal error')
                    content = "500 Internal error"

            self.end_headers()

            if isinstance(content, bytes):
                return content
            elif isinstance(content, dict) or isinstance(content, list):
                return orjson.dumps(content)
            else:
                return bytes(content, 'UTF-8')

        def respond(self, opts):
            response = self.handle_http(opts['handler'])
            self.wfile.write(response)
    return Server


def run_server(db: DB, host_name: str, port_number: int) -> None:
    server_class = make_server(db)
    httpd = HTTPServer((host_name, port_number), server_class)

    logging.info('Staring sever %s:%s', host_name, port_number)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Server Stopped %s:%s', host_name, port_number)