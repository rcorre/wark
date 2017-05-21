import weechat
from spark import rooms, session

SCRIPT_NAME = "spark"
FULL_NAME = "plugins.var.python.{}".format(SCRIPT_NAME)


weechat.register(SCRIPT_NAME, "rcorre", "0.1", "MIT", "Spark Client", "", "")


spark_session=None


def room_list(buf):
    names = [room.title for room in rooms.Room.get(spark_session)]
    weechat.prnt(buf, 'rooms: ' + ', '.join(names))
    return weechat.WEECHAT_RC_OK


COMMANDS = {
    'room': {
        'list': room_list,
    }
}


def buffer_input_cb(data, buf, input_data):
    weechat.prnt(buf, input_data)
    return weechat.WEECHAT_RC_OK


def buffer_close_cb(data, buf):
    return weechat.WEECHAT_RC_OK


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
    except:
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


def init():
    weechat.prnt("", "Initializing Spark plugin...")
    token = weechat.config_get_plugin("token")
    spark_session = session.Session('https://api.ciscospark.com', token)
    for room in rooms.Room.get(spark_session):
        buf = weechat.buffer_new("spark." + room.title, "buffer_input_cb", "",
                                 "buffer_close_cb", "")
        weechat.buffer_set(buf, "title", room.title)
    weechat.prnt("", "Spark plugin initialized!")


if weechat.config_is_set_plugin("token"):
    init()
else:
    weechat.prnt("", "Spark token unset")
    weechat.prnt("", "Run /set {}.token <token>".format(FULL_NAME))
