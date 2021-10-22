import base64
import logging
from os.path import isfile
from typing import Dict, List, Optional

from database.entities.chat import Chat
from database.entities.message import choose_message_type, Message
from database.models import Model


class DB:
    def __init__(self, model: Model):
        self.model: Model = model
        self._cache: Dict = {}
        self.limit_messages: Optional[int] = None

    def create_table(self, name, specs):
        self.model.execute('DROP TABLE IF EXISTS {0}', name)
        self.model.execute('CREATE TABLE {0} ({1});', name, specs)
        self.model.commit()
        logging.info("'%s' database created", name)

    def create_databases(self):
        logging.info("Creating tables")
        self.create_table('personals', '''
            user_id NUMERIC NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255),
            phone_number VARCHAR(255) NOT NULL,
            username VARCHAR(255),
            bio VARCHAR
            ''')
        self.create_table('profile_pictures', '''
            date TIMESTAMP NOT NULL,
            photo VARCHAR NOT NULL,
            data VARCHAR NOT NULL
            ''')
        self.create_table('contacts', '''
            first_name VARCHAR NOT NULL,
            last_name VARCHAR,
            phone_number VARCHAR NOT NULL,
            date TIMESTAMP NOT NULL
            ''')
        self.create_table('frequent_contacts', '''
            id VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            rating VARCHAR NOT NULL
            ''')
        self.create_table('created_stickers', '''
            url VARCHAR NOT NULL
            ''')
        self.create_table('installed_stickers', '''
            url VARCHAR NOT NULL
            ''')
        self.create_table('ips', '''
            ip VARCHAR NOT NULL
            ''')
        self.create_table('drafts', '''
            chat VARCHAR NOT NULL,
            chat_name VARCHAR NOT NULL,
            html VARCHAR NOT NULL
            ''')
        self.create_table('chats', '''
            id_key NUMERIC NOT NULL,
            id NUMERIC NOT NULL,
            messages_count NUMERIC NOT NULL,
            name VARCHAR,
            type VARCHAR NOT NULL
            ''')

        self.create_table('links', '''
            id_key NUMERIC NOT NULL,
            chat_id NUMERIC NOT NULL,
            message_id NUMERIC NOT NULL,
            url VARCHAR NOT NULL
            ''')

        self.create_table('messages', '''
            id NUMERIC NOT NULL,
            chat_id NUMERIC NOT NULL,
            type VARCHAR NOT NULL,
            date TIMESTAMP NOT NULL,
            from_name VARCHAR,
            from_id VARCHAR,
            text VARCHAR,
            forwarded_from VARCHAR,
            reply_to_message_id VARCHAR,
            saved_from VARCHAR,
            edited VARCHAR,
            media_type VARCHAR,
            mime_type VARCHAR,
            performer VARCHAR,
            sticker_emoji VARCHAR,
            via_bot VARCHAR,
            title VARCHAR,
            live_location_period_seconds NUMERIC,
            width VARCHAR,
            height VARCHAR,
            duration_seconds NUMERIC,
            self_destruct_period_seconds NUMERIC,
            discard_reason VARCHAR,
            action VARCHAR,
            latitude VARCHAR,
            longitude VARCHAR''')

    def _fill_row(self, name, args):
        keys = ",".join(list(args.keys()))
        values = ",".join(
            "'{0}'".format(str(x).replace("\'", "\'\'")) if x != '' else "null" for x in list(args.values()))
        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(name, keys, values)
        self.model.execute(query)

    def _fill_personals(self, data):
        data = data['personal_information']
        self._fill_row('personals', data)
        self.model.commit()

    def _fill_profile_pictures(self, data, base_dir):
        data = data['profile_pictures']
        for item in data:
            file = base_dir + "/" + item['photo']
            if not isfile(file):
                logging.error('Unable to open profile picture %s', file)
                item['data'] = ''
            else:
                with open(file, "rb") as f:
                    item['data'] = base64.b64encode(f.read()).decode("utf-8")

            self._fill_row('profile_pictures', item)
        self.model.commit()

    def _fill_contacts(self, data):
        data = data['contacts']
        for item in data['list']:
            self._fill_row('contacts', item)
        self.model.commit()

    def _fill_frequent_contacts(self, data):
        data = data['frequent_contacts']
        for item in data['list']:
            self._fill_row('frequent_contacts', item)
        self.model.commit()

    def _fill_created_stickers(self, data):
        data = data['other_data']
        for item in data['created_stickers']:
            self._fill_row('created_stickers', item)
        self.model.commit()

    def _fill_installed_stickers(self, data):
        data = data['other_data']
        for item in data['installed_stickers']:
            self._fill_row('installed_stickers', item)
        self.model.commit()

    def _fill_ips(self, data):
        data = data['other_data']
        for item in data['ips']:
            self._fill_row('ips', item)
        self.model.commit()

    def _fill_drafts(self, data):
        data = data['other_data']
        for item in data['drafts']:
            self._fill_row('drafts', item)
        self.model.commit()

    def _fill_chats(self, data):
        data = data['chats']

        for index, item in enumerate(data['list']):
            item['id_key'] = index
            item['messages_count'] = len(item['messages'])
            item = {i: item[i] for i in item if i != 'messages'}
            self._fill_row('chats', item)
        self.model.commit()

    def _rm_keys(self, dict, keys):
        for key in keys:
            if key in dict:
                del dict[key]
        return dict

    def _fill_messages(self, data):
        data = data['chats']

        total = 0
        for item in data['list']:
            total += len(item['messages'])

        processed = 0
        max_stages = 40
        stages = []

        for i in range(0, max_stages):
            stages.append((total / max_stages * i, False))
        link_counter = 0

        for chat_id, item in enumerate(data['list']):
            item = item['messages']
            for message in item:
                message['chat_id'] = chat_id
                message = self._rm_keys(message, ['photo', 'thumbnail', 'file', 'game_title',
                                                  'game_description', 'game_link', 'actor', 'actor_id',
                                                  'game_message_id', 'score', 'contact_information',
                                                  'contact_vcard', 'poll', 'message_id', 'inviter',
                                                  'members', 'place_name', 'address', 'emoticon',
                                                  'author'])
                text = ""

                if isinstance(message['text'], list):
                    for entity in message['text']:
                        if isinstance(entity, dict):
                            if entity['type'] == 'link':
                                text += "<link#{0}>".format(link_counter)
                                e = {'chat_id': chat_id,
                                     'message_id': message['id'],
                                     'id_key': link_counter,
                                     'url': entity['text']}
                                link_counter += 1
                                self._fill_row('links', e)
                            else:
                                text += entity['text']
                        else:
                            text += entity
                else:
                    text = message['text']

                message['text'] = text

                if 'from' in message:
                    message['from_name'] = message.pop('from')

                if 'duration' in message:
                    message['duration_seconds'] = message.pop('duration')

                if 'location_information' in message:
                    loc = message.pop('location_information')
                    message['latitude'] = loc['latitude']
                    message['longitude'] = loc['longitude']

                self._fill_row('messages', message)
                if processed % 200 == 0:
                    for index, stage in enumerate(stages):
                        if stage[0] < processed and not stage[1]:
                            logging.info("Filled {0:.2f}% ({1} of {2})".format(processed / total * 100,
                                                                               processed,
                                                                               total))
                            stages[index] = (0, True)
                processed += 1
        self.model.commit()

    def fill_databases(self, data: Dict, base_dir: str):
        logging.info("Filling tables")

        logging.info("Filling 'personals' information")
        self._fill_personals(data)

        logging.info("Filling 'profile_pictures' information")
        self._fill_profile_pictures(data, base_dir)

        logging.info("Filling 'contacts' information")
        self._fill_contacts(data)

        logging.info("Filling 'frequent_contacts' information")
        self._fill_frequent_contacts(data)

        logging.info("Filling 'created_stickers' information")
        self._fill_created_stickers(data)

        logging.info("Filling 'installed_stickers' information")
        self._fill_installed_stickers(data)

        logging.info("Filling 'ips' information")
        self._fill_ips(data)

        logging.info("Filling 'drafts' information")
        self._fill_drafts(data)

        logging.info("Filling 'chats' information")
        self._fill_chats(data)

        logging.info("Filling 'messages' information")
        self._fill_messages(data)

    def get_personals(self):
        self.model.execute('SELECT * FROM personals')
        return self.model.fetchone(True)

    def get_profile_pictures(self):
        self.model.execute('SELECT * FROM profile_pictures ORDER BY date DESC')
        return self.model.fetchall(True)

    def _do_cache(self, name: str, fn):
        if name not in self._cache:
            self._cache[name] = fn()
        return self._cache[name]

    def get_id(self) -> str:
        return self._do_cache(
            'id',
            lambda: 'user' + str(self.get_personals()['user_id']))

    def _get_chats_aux(self):
        self.model.execute('SELECT * FROM chats')
        return [Chat().parse(x) for x in self.model.fetchall(True)]

    def get_chats(self) -> List[Chat]:
        return self._do_cache(
            'chats',
            self._get_chats_aux)

    def _get_messages_aux(self):
        logging.info('Caching chats')
        chats = self.get_chats()

        logging.info('Caching messages')
        if self.limit_messages is not None:
            self.model.execute('SELECT * FROM messages LIMIT {0}'.format(self.limit_messages))
        else:
            self.model.execute('SELECT * FROM messages')
        messages = [choose_message_type(x, chats) for x in self.model.fetchall(True)]

        logging.info('Caching members')
        for chat in chats:
            members = set()
            for message in messages:
                if message.chat == chat:
                    members.add(message.sender_name)

            if None in members:
                members.remove(None)

            chat.members = list(members)

        return messages

    def get_messages(self) -> List[Message]:
        return self._do_cache(
            'messages',
            self._get_messages_aux)

    def get_freq_contacts(self) -> List[Dict]:
        self.model.execute('SELECT * FROM frequent_contacts')
        return self.model.fetchall(True)

    def get_created_stickers(self) -> List[Dict]:
        self.model.execute('SELECT * FROM created_stickers')
        return self.model.fetchall(True)

    def get_installed_stickers(self) -> List[Dict]:
        self.model.execute('SELECT * FROM installed_stickers')
        return self.model.fetchall(True)

    def get_ips(self) -> List[Dict]:
        self.model.execute('SELECT * FROM ips')
        return self.model.fetchall(True)
