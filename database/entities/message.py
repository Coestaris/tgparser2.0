from datetime import datetime
from typing import Optional, List, Dict

from database.entities.chat import Chat
from database.entities.mixins import *


class Message:
    def __init__(self, mixins: List[MessageMixin]):
        self.mixins: List[MessageMixin] = mixins

        self.id: int = 0
        self.chat_id: int = 0
        self.chat: Chat = None
        self.type: str = ""
        self.date: datetime = datetime.now()
        self.sender_name: str = ""
        self.from_id: str = ""

        self.forwarded_from: Optional[str] = None
        self.replied_to: Optional[Message] = None

        self.edited: Optional[datetime] = None
        self.via_bot: Optional[str] = None
        self.self_destruct: Optional[int] = None

        self.action: Optional[str] = None
        self.text: Optional[str] = None

    def is_output(self, id):
        return self.from_id == id

    def is_input(self, filters):
        if filters['chat']:
            if filters['selected_member'] == 'Все пользователи':
                return True
            else:
                return self.sender_name == filters['selected_member']

        return True

    def is_service(self):
        return self.type == 'service'

    def parse(self, d: dict, chats: List[Chat]):
        self.id = int(d['id'])

        self.chat_id = int(d['chat_id'])

        for chat in chats:
            if chat.id_key == self.chat_id:
                self.chat = chat
                break

        self.type = d['type']
        self.text = d['text']
        self.date = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S')
        self.sender_name = d['from_name']
        self.from_id = d['from_id']
        self.action = d['action']
        self.forwarded_from = d['forwarded_from']
        self.replied_to = d['reply_to_message_id']

        if d['edited'] is not None:
            self.edited = datetime.strptime(d['edited'], '%Y-%m-%dT%H:%M:%S')

        self.via_bot = d['via_bot']

        if d['self_destruct_period_seconds'] is not None:
            self.self_destruct = int(d['self_destruct_period_seconds'])

        for mixin in self.mixins:
            mixin.parse(d)

    def is_phone_call(self) -> bool:
        return self.action == 'phone_call'

    def has_link(self) -> bool:
        return self.text is not None and '<link#' in self.text

    def accepts_filter(self, filter: Dict[str, bool]) -> bool:
        if filter['chat']:
            return self.chat.name == filter['selected_chat']

        if filter['personals'] and self.chat.is_personal():
            return True
        if filter['public_chats'] and self.chat.is_public_group():
            return True
        if filter['private_chats'] and self.chat.is_private_group():
            return True
        if filter['channels'] and self.chat.is_public_channel() or self.chat.is_private_channel():
            return True
        return False


class PlainMessage(Message):
    def __init__(self):
        super().__init__([])


class PhoneCall(Message):
    def __init__(self):
        super().__init__([DurationMixin(self)])


class StickerMessage(Message):
    def __init__(self):
        super().__init__([ImageMixin(self)])
        self.sticker_emoji: str = ""

    def parse(self, d, chats: List[Chat]):
        super(StickerMessage, self).parse(d, chats)
        self.sticker_emoji = d['sticker_emoji']
        pass


class VideoMessage(Message):
    def __init__(self):
        super().__init__([ResourceMixin(self), ImageMixin(self), DurationMixin(self)])


class AudioMessage(Message):
    def __init__(self):
        super().__init__([ResourceMixin(self), DurationMixin(self)])
        self.performer: Optional[str] = ""
        self.title: Optional[str] = ""

    def parse(self, d, chats: List[Chat]):
        super(AudioMessage, self).parse(d, chats)
        self.performer = d['performer']
        self.title = d['title']
        pass


class VoiceMessage(Message):
    def __init__(self):
        super().__init__([ResourceMixin(self), DurationMixin(self)])


class VideoVoiceMessage(VideoMessage):
    pass


class ImageMessage(Message):
    def __init__(self):
        super().__init__([ImageMixin(self)])


class LocationMessage(Message):
    def __init__(self):
        super().__init__([LocationMixin(self)])


class LiveLocationMessage(Message):
    def __init__(self):
        super().__init__([LocationMixin(self), DurationMixin(self)])


def choose_message_type(d: dict, chats: List[Chat]) -> Message:
    if d['media_type'] == 'sticker':
        message = StickerMessage()
    elif d['media_type'] == 'animation' or d['media_type'] == 'video_file':
        message = VideoMessage()
    elif d['media_type'] == 'audio_file':
        message = AudioMessage()
    elif d['media_type'] == 'video_message':
        message = VideoVoiceMessage()
    elif d['media_type'] == 'voice_message':
        message = VoiceMessage()
    elif d['media_type'] is None:
        if d['width'] is not None:
            message = ImageMessage()
        elif d['live_location_period_seconds'] is not None:
            message = LiveLocationMessage()
        elif d['longitude'] is not None:
            message = LocationMessage()
        elif d['action'] is not None and d['action'] == 'phone_call':
            message = PhoneCall()
        else:
            message = PlainMessage()
    else:
        raise NameError(d['media_type'])
    message.parse(d, chats)
    return message

