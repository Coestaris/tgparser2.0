from datetime import datetime

from database.database import DB
from database.entities.message import *
from server.handlers.dynamic_handler import DynamicHandler


def classifyMessages(msg):
    if isinstance(msg, PlainMessage):
        return 'plain'
    elif isinstance(msg, StickerMessage):
        return 'sticker'
    elif isinstance(msg, VideoVoiceMessage):
        return 'videoMessage'
    elif isinstance(msg, VideoMessage):
        return 'video'
    elif isinstance(msg, AudioMessage):
        return 'audio'
    elif isinstance(msg, VoiceMessage):
        return 'voice'
    elif isinstance(msg, ImageMessage):
        return 'image'
    elif isinstance(msg, LiveLocationMessage):
        return 'liveLocation'
    elif isinstance(msg, LocationMessage):
        return 'location'


def handle(dynamic_handler: DynamicHandler, body: dict, database: DB):
    messages = database.get_messages()
    id = database.get_id()

    input = {}
    output = {}

    calls = 0
    calls_duration = 0

    video_input_duration = 0
    video_output_duration = 0

    audio_input_duration = 0
    audio_output_duration = 0

    image_size = (0, 0)

    voice_input_duration = 0
    voice_output_duration = 0

    video_voice_input_duration = 0
    video_voice_output_duration = 0

    links_output = 0
    links_input = 0

    for message in messages:
        if message.accepts_filter(body):
            if message.is_service():
                if isinstance(message, PhoneCall) and message.duration != 0:
                    calls += 1
                    calls_duration += message.duration
            else:
                if isinstance(message, VideoVoiceMessage):
                    if message.is_output(id):
                        video_voice_output_duration += message.duration
                    elif message.is_input(body):
                        video_voice_input_duration += message.duration
                if isinstance(message, VideoMessage):
                    if message.is_output(id):
                        video_output_duration += message.duration
                    elif message.is_input(body):
                        video_input_duration += message.duration
                elif isinstance(message, AudioMessage):
                    if message.is_output(id):
                        audio_output_duration += message.duration
                    elif message.is_input(body):
                        audio_input_duration += message.duration
                elif isinstance(message, ImageMessage):
                    image_size = (image_size[0] + message.width,
                                  image_size[1] + message.height)
                elif isinstance(message, VoiceMessage):
                    if message.is_output(id):
                        voice_output_duration += message.duration
                    elif message.is_input(body):
                        voice_input_duration += message.duration

                if message.has_link():
                    if message.is_output(id):
                        links_output += 1
                    elif message.is_input(body):
                        links_input += 1

                type = classifyMessages(message)
                if message.is_output(id):
                    if type in output:
                        output[type] += 1
                    else:
                        output[type] = 1
                elif message.is_input(body):
                    if type in input:
                        input[type] += 1
                    else:
                        input[type] = 1

    keys = list(set(input.keys()).union(output.keys()))
    input_res = []
    output_res = []
    for key in keys:
        input_res.append(input[key] if key in input else 0)
        output_res.append(output[key] if key in output else 0)

    img_size_divider = ((0 if 'image' not in input else input['image']) +
                        (0 if 'image' not in output else output['image']))
    if img_size_divider == 0:
        img_size_divider = 1

    return {
        'keys': keys,
        'input': input_res,
        'output': output_res,
        'calls': calls,
        'calls_duration': calls_duration / (1 if calls == 0 else calls),
        'video_input_duration': video_input_duration / (1 if 'video' not in input else input['video']),
        'video_output_duration': video_output_duration / (1 if 'video' not in output else output['video']),
        'audio_input_duration': audio_input_duration / (1 if 'audio' not in input else input['audio']),
        'audio_output_duration': audio_output_duration / (1 if 'audio' not in output else output['audio']),
        'image_size': [
            image_size[0] / img_size_divider,
            image_size[1] / img_size_divider,
        ],
        'voice_input_duration': voice_input_duration / (1 if 'voice' not in input else input['voice']),
        'voice_output_duration': voice_output_duration / (1 if 'voice' not in output else output['voice']),
        'video_voice_input_duration': video_voice_input_duration / (1 if 'videoMessage' not in input else input['videoMessage']),
        'video_voice_output_duration': video_voice_output_duration / (1 if 'videoMessage' not in output else output['videoMessage']),
        'links_input': links_input,
        'links_output': links_output
    }
