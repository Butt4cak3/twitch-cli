# What is this?

This is a CLI frontend for [Twitch](https://www.twitch.tv) and
[Streamlink](https://github.com/streamlink/streamlink). It lists currently live
streams and lets you pick one without typing the streamlink command.
Streams online now:

# Usage example
```
$ python3 twitch-cli.py
Streams online now:

[1] RocketLeague: RLCS Season 4 NA League Play Week 4
    rocketleague playing Rocket League for 69576 viewers

[2] Heroes of the Storm: HGC NA Phase 2 Playoffs - Round 2
    blizzheroes playing Heroes of the Storm for 17076 viewers

[3] GamesDoneQuick: GDQ HOTFIX Presents: Mystery Tournament Top 8 Weekend! - Sat 9/30 and Sun 10/1 at 2PM EDT
    gamesdonequick playing  for 4757 viewers

[4] ESL_CSGO: RERUN: FaZe vs. Team Liquid [Inferno] Map 1 - Grand Final - ESL One New York 2017
    esl_csgo playing Counter-Strike: Global Offensive for 632 viewers

Stream ID: 1

[cli][info] Found matching plugin twitch for URL twitch.tv/rocketleague
[plugin.twitch][info] Attempting to authenticate using OAuth token
...
```

# Installation

## Prerequisites

Install Python 3.x.

Install the *requests* package with `pip install requests`.

This program needs [Streamlink](https://github.com/streamlink/streamlink) to be
installed somewhere in your `$PATH` in order to open livestreams in a video
player.

## Download twitch-cli

Download *twitch-cli.py* and place it in any directory. To run the program, run
`python3 /path/to/twitch-cli.py/`.

You can also move *twitch-cli.py* to a directory in your `$PATH`, rename it to
*twitch-cli* (or anything you want) without a file extension and make it
executable. That way, you can simply run the command `twitch` from the terminal.

# Configuration

After executing the script for the first time, you will find a configuration
file in *$HOME/.config/twitch-cli/*. Everything you can configure will have a
default value in the configuration file. There are no hidden options. If you
want to reset an option to its default, delete it from the file and it will get
reset the next time you run the program.
