import os

from server.handlers.request_handler import RequestHandler


class FileHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.filetypes = {
            ".js": "text/javascript",
            ".css": "text/css",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".ico": "image/ico",
            ".png": "image/png",
            "notfound": "text/plain"
        }

    def find(self, file_path):
        split_path = os.path.splitext(file_path)
        extension = split_path[1]

        try:
            if extension in (".jpg", ".jpeg", ".png", ".ico"):
                self.contents = open("server/public{}".format(file_path), 'rb')
            else:
                self.contents = open("server/public{}".format(file_path), 'r')

            self.set_content_type(extension)
            self.set_status(200)
            return True
        except FileNotFoundError:
            self.set_content_type('notfound')
            self.set_status(404)
            return False

    def set_content_type(self, ext):
        self.content_type = self.filetypes[ext]
