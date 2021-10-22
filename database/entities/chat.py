from typing import List


class Chat:
    def __init__(self):
        self.id_key: int = 0
        self.messages_count: int = 0
        self.name: str = ''
        self.members: List[str] = []
        self.type: str = ''
        self.id: str = ''

    def is_saved(self):
        return self.type == 'saved_messages'

    def is_personal(self):
        return self.type == 'personal_chat'

    def is_private_group(self):
        return self.type == 'private_group' or self.type == 'private_supergroup'

    def is_public_group(self):
        return self.type == 'public_group' or self.type == 'public_supergroup'

    def is_private_channel(self):
        return self.type == 'private_channel'

    def is_public_channel(self):
        return self.type == 'public_channel'

    def parse(self, d):
        self.id_key = d['id_key']
        self.id = d['id']
        self.messages_count = d['messages_count']
        self.name = d['name']
        self.type = d['type']
        return self
