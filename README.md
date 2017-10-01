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

## GNU/Linux

### Prerequisites

Install Python 3.x using your preferred package manager.

Install the *requests* package with `pip install requests`. Depending on your
distribution, the command may be `pip3` rather than just `pip`. To find out
which command is the right one, run `pip --version` and `pip3 --version` and
check the outputs.

This program needs [Streamlink](https://github.com/streamlink/streamlink) to be
installed somewhere in your `$PATH` in order to open livestreams in a video
player. You can follow the [installations instructions on the Streamlink GitHub
page](https://streamlink.github.io/install.html).

### Install twitch-cli

Download *twitch-cli.py* and place it in any directory. To run the program, run
`python3 /path/to/twitch-cli.py`.

You can also move *twitch-cli.py* to a directory in your `$PATH`
(*/usr/local/bin/* or *$HOME/bin/*), rename it to *twitch-cli* (or anything you
want) without a file extension and make it executable. That way, you can simply
run the command `twitch-cli` from the terminal.

## Windows

### Prerequisites

Download and install Python 3.x from
[the Python website](https://www.python.org).

Install the *requests* package with `pip install requests`.

This program needs [Streamlink](https://github.com/streamlink/streamlink) to be
installed somewhere in your `%PATH%` in order to open livestreams in a video
player. You can follow the [installations instructions on the Streamlink GitHub
page](https://streamlink.github.io/install.html).

### Install twitch-cli

Download *twitch-cli.py* and place it in any directory. To run the program, open
a command line and run `python3 X:\path\to\twitch-cli.py`.

To make the command `twitch-cli` available, follow these steps:
 1. Go to *C:\Users\YOURUSERNAME\AppData\Roaming\twitch-cli\\* (create the
   directory if it doesn't exist yet)
 2. Place the file *twitch-cli.py* in there
 3. Create a new text file called *twitch-cli.bat*
 4. Open it, paste the following code, save and close

```
@echo off
SET cwd=%~dp0
python "%cwd%\twitch-cli.py" %*
```

 5. Go to the environment variable dialog (not explained here) and edit the
    *Path* variable of your user account. Adda  new line with the content
    "%APPDATA%\twitch-cli" and hit OK.

You can now open a command line and run `twitch-cli` anywhere.

# Configuration

You can authenticate with Twitch using `python3 twitch-cli.py auth`. Follow the
instructions and copy the OAuth key into the application or the configuration
file.

## Configuration files

After executing the script for the first time, you will find a configuration
file at:

 * **GNU/Linux**: *$HOME/.config/twitch-cli/config.json*
 * **Windows**: *%APPDATA%/twitch-cli/config.json*

Everything you can configure will have a default value in the configuration
file. There are no hidden options. If you want to reset an option to its
default, delete it from the file and it will get reset the next time you run the
program.
