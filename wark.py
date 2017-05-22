import time
import weechat
from ciscosparkapi import CiscoSparkAPI


SCRIPT_NAME = "spark"
FULL_NAME = "plugins.var.python.{}".format(SCRIPT_NAME)


weechat.register(SCRIPT_NAME, "rcorre", "0.1", "MIT", "Spark Client", "", "")


weechat.prnt("", "Initializing Spark plugin...")
api = CiscoSparkAPI()
rooms = {room.title: room for room in api.rooms.list()}
weechat.prnt("", "Spark plugin initialized!")


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
    parse_time = lambda m: time.strptime(m.created, '%Y-%m-%dT%H:%M:%S.%fZ')
    messages = api.messages.list(roomId=room.id)
    for msg in messages:
        unixtime = int(time.mktime(parse_time(msg)))
        weechat.prnt_date_tags(newbuf, unixtime, "", msg.text)


COMMANDS = {
    'room': {
        'list': room_list,
        'open': room_open,
    }
}


def config_cb(data, option, value):
    if option == FULL_NAME + ".token":
        init()
    return weechat.WEECHAT_RC_OK


weechat.hook_config(FULL_NAME + ".*", "config_cb", "")


def spark_command_cb(data, buf, command):
    parts = command.split(' ')
    cmd = parts[0]
    subcmd = parts[1]
    args = parts[2:]

    if not cmd in COMMANDS:
        weechat.prnt(buf, "Unknown command " + cmd)
        return weechat.WEECHAT_RC_ERROR
    if not subcmd in COMMANDS[cmd]:
        weechat.prnt(buf, "Unknown command " + subcmd)
        return weechat.WEECHAT_RC_ERROR

    try:
        COMMANDS[cmd][subcmd](buf, *args)
        return weechat.WEECHAT_RC_OK
    except Exception as ex:
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
    '',
    # Function name
    'spark_command_cb', '')
