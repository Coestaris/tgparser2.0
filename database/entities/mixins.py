class MessageMixin:
    def __init__(self, object):
        self.object = object

    def parse(self, d):
        raise NotImplementedError()


class LocationMixin(MessageMixin):
    def __init__(self, object):
        super().__init__(object)
        self.object.longitude = 0
        self.object.latitude = 0

    def parse(self, d):
        self.object.longitude = float(d['longitude'])
        self.object.latitude = float(d['latitude'])


class ImageMixin(MessageMixin):
    def __init__(self, object):
        super().__init__(object)
        self.object.width = 0
        self.object.height = 0

    def parse(self, d):
        # if d['width'] is not None:
        self.object.width = int(d['width'])
        # if d['height'] is not None:
        self.object.height = int(d['height'])


class DurationMixin (MessageMixin):
    def __init__(self, object):
        super().__init__(object)
        self.object.duration = 0

    def parse(self, d):
        if d['duration_seconds'] is not None:
            self.object.duration = int(d['duration_seconds'])


class ResourceMixin (MessageMixin):
    def __init__(self, object):
        super().__init__(object)
        self.object.mime_type = ''

    def parse(self, d):
        self.object.mime_type = d['mime_type']
