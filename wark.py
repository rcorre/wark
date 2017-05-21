import weechat

weechat.register("wark", "rcorre", "0.1", "MIT", "Spark Client", "", "")

options = [
    ("token", "")
]

for option, default_value in options:
    if not weechat.config_is_set_plugin(option):
        weechat.config_set_plugin(option, default_value)

if not weechat.config_is_set_plugin("token"):
    weechat.prnt("", "Spark token not set")
else:
    weechat.prnt("", "Got token!")

token = weechat.config_get_plugin("token")

def buffer_input_cb(data, buf, input_data):
    weechat.prnt(buf, input_data)
    return weechat.WEECHAT_RC_OK

def buffer_close_cb(data, buf):
    return weechat.WEECHAT_RC_OK

buf = weechat.buffer_new("wark", "buffer_input_cb", "", "buffer_close_cb", "")
weechat.buffer_set(buf, "spark", "Spark")
weechat.prnt(buf, "Connecting to Cisco Spark...")

# disable logging, by setting local variable "no_log" to "1"
#weechat.buffer_set(buf, "localvar_set_no_log", "1")
