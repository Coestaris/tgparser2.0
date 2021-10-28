from collections import defaultdict
from itertools import count
from typing import List
import re
from database.database import DB
from database.entities.message import StickerMessage
from server.handlers.dynamic_handler import DynamicHandler
from emoji import emoji_lis


reSplitter = re.compile(r'''\s|[.,!@#$%^&*()<>?\"'[\]\-+=:{}`~_;]''')
reLink = re.compile(r'''<link#\d+>''')
reMat = re.compile(r'''(бля(ть)?)|(су(ч)?к[аи])|(пизд)|(eб[лаoe])|(eбну)|(ху[йeё])|(говн)|(уеб)''')


def dict_inc(dict, txt):
    if txt in dict:
        dict[txt] += 1
    else:
        dict[txt] = 1


def sort_dict(d, max=None):
    count = list(d.items())
    size = sum(x[1] for x in count)
    count.sort(key=lambda x: x[1], reverse=True)

    return {
        'total': size,
        'dict': dict(count[:max] if max is not None else count)
    }


def count_emojis(words):
    count = {}
    for word in words:
        emojis = emoji_lis(word)
        if len(emojis) != 0:
            for emoji in emojis:
                dict_inc(count, emoji['emoji'])
    return count


def count_words(words):
    count = {}
    for word in words:
        dict_inc(count, word)
    return count


def filter_dict(d, fn):
    new_dict = {}
    for k,v in d.items():
        if fn(k):
            new_dict[k] = v

    return new_dict


def split(inp: str) -> List[str]:
    return [x.strip().lower() for x in reSplitter.split(reLink.sub('', inp)) if x.strip() != '']


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    chats = database.get_chats()
    id = database.get_id()
    messages = database.get_messages()

    input_count = 0
    output_count = 0
    input_words = []
    output_words = []

    stickers_input = {}
    stickers_output = {}

    edited_input = 0
    edited_output = 0

    self_destruct_input = 0
    self_destruct_output = 0

    via_bot_input = 0
    via_bot_output = 0

    replies_input = 0
    replies_output = 0

    forwarded_input = 0
    forwarded_output = 0

    for message in messages:
        if message.accepts_filter(body) and not message.is_service():
            if message.is_output(id):
                if message.text is not None:
                    output_count += 1
                    output_words += split(message.text)

                if isinstance(message, StickerMessage):
                    dict_inc(stickers_output, message.sticker_emoji)

                if message.edited is not None:
                    edited_output += 1

                if message.self_destruct is not None:
                    self_destruct_output += 1

                if message.via_bot is not None:
                    via_bot_output += 1

                if message.replied_to is not None:
                    replies_output += 1

                if message.forwarded_from is not None:
                    forwarded_output += 1

            elif message.is_input(body):
                if message.text is not None:
                    input_count += 1
                    input_words += split(message.text)

                if isinstance(message, StickerMessage):
                    dict_inc(stickers_input, message.sticker_emoji)

                if message.edited is not None:
                    edited_input += 1

                if message.self_destruct is not None:
                    self_destruct_input += 1

                if message.via_bot is not None:
                    via_bot_input += 1

                if message.replied_to is not None:
                    replies_input += 1

                if message.forwarded_from is not None:
                    forwarded_input += 1

    counted_words_input = count_words(input_words)
    counted_words_output = count_words(output_words)

    return {
        'input_words': sort_dict(counted_words_input, 200),
        'output_words': sort_dict(counted_words_output, 200),
        'input_mats': sort_dict(filter_dict(counted_words_input, reMat.match), 50),
        'output_mats': sort_dict(filter_dict(counted_words_output, reMat.match), 50),
        'hello_input': len([x for x in input_words if x == 'привет']),
        'hello_output': len([x for x in output_words if x == 'привет']),
        'edited_input': edited_input,
        'edited_output': edited_output,
        'self_destruct_input': self_destruct_input,
        'self_destruct_output': self_destruct_output,
        'via_bot_input': via_bot_input,
        'via_bot_output': via_bot_output,
        'replies_input': replies_input,
        'replies_output': replies_output,
        'forwarded_input': forwarded_input,
        'forwarded_output': forwarded_output,
        'input_stickers': sort_dict(stickers_input, 10),
        'output_stickers': sort_dict(stickers_output, 10),
        'input_emoji': sort_dict(count_emojis(input_words), 30),
        'output_emoji': sort_dict(count_emojis(output_words), 30),
        'words_in_input': len(input_words) / input_count if input_count != 0 else 0,
        'words_in_output': len(output_words) / output_count if output_count != 0 else 0
    }
