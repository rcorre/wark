# Wark

[Weechat](https://weechat.org/) client for
[Cisco Spark](https://www.ciscospark.com/).

# Features

Wark is pre-alpha. Expect bugs, lacking functionality, and general instability.

- Connect to rooms and view messages

# Installation

Install the requirements:

- python**2**
- Weechat with the python plugin
- [ciscosparkapi](https://github.com/CiscoDevNet/ciscosparkapi) (`pip2 install --user ciscosparkapi`)

Link `wark.py` into `~/.weechat/python/autoload/`. Alternatively, link
`wark.py` into `~/.weechat/python/`, then load it at runtime with
`python load wark.py`.

You must set the `SPARK_ACCESS_TOKEN` environment variable. Get your token by
signing in to https://developer.ciscospark.com/getting-started.html.

# Commands

- `/spark rooms`: list available rooms.

- `/spark open <room_title>` : open a new buffer for the given room and load
  past messages.
