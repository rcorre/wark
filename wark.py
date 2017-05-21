import weechat
from spark import rooms, session

weechat.register("wark", "rcorre", "0.1", "MIT", "Spark Client", "", "")

if not weechat.config_is_set_plugin("token"):
    weechat.prnt("",
        "Spark token not set. Run: /set plugins.var.wark.token <token>")

token = weechat.config_get_plugin("token")
session = session.Session('https://api.ciscospark.com', token)

def buffer_input_cb(data, buf, input_data):
    weechat.prnt(buf, input_data)
    return weechat.WEECHAT_RC_OK


def buffer_close_cb(data, buf):
    return weechat.WEECHAT_RC_OK


# disable logging, by setting local variable "no_log" to "1"
#weechat.buffer_set(buf, "localvar_set_no_log", "1")


for room in rooms.Room.get(session):
    buf = weechat.buffer_new(room.title, "buffer_input_cb", "", "buffer_close_cb", "")
    weechat.buffer_set(buf, "title", room.title)
