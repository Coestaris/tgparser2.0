from server.handlers.request_handler import RequestHandler


class StaticHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/html'

    def find(self, route_data):
        try:
            template_file = open('server/public/{}'.format(route_data['file']))
            self.contents = template_file
            self.set_status(200)
            return True
        except FileNotFoundError:
            self.set_status(404)
            return False
