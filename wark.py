import os
import json
import uuid
import time
import shlex

import weechat
import requests
from ciscosparkapi import CiscoSparkAPI
from ws4py.client.threadedclient import WebSocketClient


SCRIPT_NAME = "spark"
FULL_NAME = "plugins.var.python.{}".format(SCRIPT_NAME)
SPARK_SOCKET_URL = 'https://wdm-a.wbx2.com/wdm/api/v1/devices'


api = None
listener = None
rooms = None


# Cisco Spark has a websocket interface to listen for message events
# It isn't documented, I found it here:
# https://github.com/marchfederico/ciscospark-websocket-events
class EventListener(WebSocketClient):
    def __init__(self):
        spec = {
            "deviceName": "weechat",
            "deviceType": "DESKTOP",
            "localizedModel": "python2",
            "model": "python2",
            "name": "weechat",
            "systemName": "weechat",
            "systemVersion": "0.1"
        }

        self.bearer = 'Bearer ' + os.getenv("SPARK_ACCESS_TOKEN")
        self.headers = {'Authorization': self.bearer}

        resp = requests.post(SPARK_SOCKET_URL, headers=self.headers, json=spec,
                             timeout=10.0)
        if resp.status_code != 200:
            print("Failed to register device {}: {}".format(name, resp.json()))
        info = resp.json()

        self.dev_url = info['url']
        super(EventListener, self).__init__(
            info['webSocketUrl'], protocols=['http-only', 'chat'])

    def opened(self):
        # authentication handshake
        self.send(json.dumps({
            'id': str(uuid.uuid4()),
            'type': 'authorization',
            'data': { 'token': self.bearer }
        }))

    def closed(self, code, reason=None):
        resp = requests.delete(self.dev_url, headers=self.headers,
                               timeout=10.0)
        if resp.status_code != 200:
            print("Failed to unregister websocket device from Spark")

    def received_message(self, m):
        try:
            j = json.loads(str(m))
        except:
            print("Failed to parse message {}".format(m))
            return

        timestamp = j['timestamp']
        data = j['data']
        name = data.get('actor', {}).get('displayName')
        ev = data['eventType']

        if ev == 'status.start_typing':
            print('{} started typing'.format(name))
        elif ev == 'status.stop_typing':
            print('{} stopped typing'.format(name))
        elif ev == 'conversation.activity':
            act = data['activity']
            verb = act['verb']
            if verb == 'post':
                msg = api.messages.get(act['id'])
                print('{} says {}'.format(name, msg))
        else:
            print('Unknown event {}'.format(ev))


class CommandException(Exception):
    pass


def buffer_input_cb(data, buf, input_data):
    weechat.prnt(buf, input_data)
    return weechat.WEECHAT_RC_OK


def buffer_close_cb(data, buf):
    return weechat.WEECHAT_RC_OK


def room_list(buf):
    weechat.prnt(buf, '--Rooms--')
    weechat.prnt(buf, '\n'.join(rooms.keys()))
    weechat.prnt(buf, '---------')


def room_open(buf, name):
    room = rooms[name]
    newbuf = weechat.buffer_new("spark." + room.title, "buffer_input_cb", "",
                                "buffer_close_cb", "")
    def unixtime(msg):
        t = time.strptime(msg.created, '%Y-%m-%dT%H:%M:%S.%fZ')
        return int(time.mktime(t))

    messages = api.messages.list(roomId=room.id)
    for msg in sorted(messages, key=unixtime):
        text = msg.text.encode('ascii', 'replace') if msg.text else ''
        weechat.prnt_date_tags(newbuf, unixtime(msg), "", text)


COMMANDS = {
    'rooms': room_list,
    'open': room_open,
}


def spark_command_cb(data, buf, command):
    parts = shlex.split(command)
    cmd = parts[0]
    args = parts[1:]

    if not cmd in COMMANDS:
        weechat.prnt(buf, "Unknown command " + cmd)
        return weechat.WEECHAT_RC_ERROR

    try:
        COMMANDS[cmd](buf, *args)
        return weechat.WEECHAT_RC_OK
    except CommandException as ex:
        weechat.prnt(buf, 'Error: {}'.format(ex))
        return weechat.WEECHAT_RC_ERROR


weechat.hook_command(
    # Command name and description
    'spark', '',
    # Usage
    '[command] [command options]',
    # Description of arguments
    'Commands:\n' +
    '\n'.join(['history']) +
    '\nUse /spark help [command] to find out more\n',
    # Completions
    '|'.join(COMMANDS.keys()),
    # Function name
    'spark_command_cb', '')


weechat.register(SCRIPT_NAME, "rcorre", "0.1", "MIT", "Spark Client", "", "")
api = CiscoSparkAPI()
rooms = {room.title: room for room in api.rooms.list()}
listener = EventListener()
listener.connect()
