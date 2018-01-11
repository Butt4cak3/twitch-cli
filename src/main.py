#!/usr/bin/python3
import os
import sys
import requests
import subprocess
import json
import click
from urllib.parse import urlencode
import webbrowser

def get_config_dir():
    if os.name == 'nt':
        return os.path.join(os.environ['APPDATA'], 'twitch-cli')
    elif os.name == 'posix':
        home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        return os.path.expanduser(os.path.join(home, 'twitch-cli'))

# The configuration file is located at $HOME/.config/twitch-cli/config.json.
CONFIG_DIR = get_config_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

TWITCH_CLIENT_ID = 'e0fm2z7ufk73k2jnkm21y0gp1h9q2o'

def save_config():
    global config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4)

def load_config():
    """Load the configuration file at ~/.config/twitch-cli/config.json and
    return a dict with configuration options."""

    global config

    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'a') as f:
            f.write('{}')
        print('Configuration file created at {}'.format(CONFIG_FILE))

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    config.setdefault('oauth', '')

    save_config()

def set_config_path(path):
    global CONFIG_DIR
    global CONFIG_FILE
    CONFIG_FILE = path
    CONFIG_DIR = os.path.dirname(CONFIG_FILE)

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', help='Configuration file location')
def main(ctx, config):
    """List or play Twitch streams"""
    if config is not None:
        set_config_path(config)

    load_config()

    if ctx.invoked_subcommand is None:
        cmd_live()

# The cmd_* functions get called when their respective subcommand is executed
# Example: "python3 twitch-cli live" calls "cmd_live"

@main.command('live')
@click.option('--flat', is_flag=True, help='Don\'t show detailed information or prompt')
@click.option('--game', help='Show live streams for a specific game')
def cmd_live(flat, game):
    """List live channels"""
    list_streams(game=game, flat=flat)

@main.command('play')
@click.argument('channel')
def cmd_play(channel):
    """Play a livestream"""
    play_stream(channel)

@main.command('follow')
@click.argument('channel')
def cmd_follow(channel):
    """Follow a channel"""
    follow_channel(channel)

@main.command('unfollow')
@click.argument('channel')
def cmd_unfollow(channel):
    """Unfollow a channel"""
    unfollow_channel(channel)

@main.command('auth')
@click.option('--force', '-f', help='Overwrite existing OAuth token')
def cmd_auth(force):
    """Authenticate with Twitch"""
    if (config['oauth'] != '') and (not force):
        print('You are already authenticated.')
        return

    token = authenticate()

    if token != '':
        config['oauth'] = token
        save_config()
        print('Authentication complete.')
    else:
        print('Authentication cancelled.')

def play_stream(channel):
    """Load a stream and open the player"""

    command = 'streamlink twitch.tv/{} best '.format(channel)

    process = subprocess.Popen(command.split(), stdout=None, stderr=None)
    output, error = process.communicate()

def list_streams(game=None, flat=False):
    """Load the list of streams and prompt the user to chose one."""

    if config['oauth'] == '':
        print('You have to provide a Twitch OAuth token to list followed '
              'streams.')
        print('Run "{} auth" to authenticate.'.format(sys.argv[0]))
        sys.exit(1)

    if game is not None:
        streams = get_game_streams(game)
    else:
        streams = get_followed_streams()

    if streams is None:
        print('Something went wrong while trying to fetch data from the '
              'Twitch API')
        sys.exit(1)

    print_stream_list(streams, title='Streams online now',
                      flat=flat)

    if not flat:
        selection = input('Stream ID: ')
        try:
            selection = int(selection)
        except:
            return
    else:
        return

    if selection > len(streams):
        return

    play_stream(streams[selection - 1]['channel']['name'])

def get_followed_streams():
    url = 'https://api.twitch.tv/kraken/streams/followed'
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Authorization': 'OAuth {}'.format(config['oauth'])
    }
    request = requests.get(url, headers=headers)
    response = request.json()

    if 'streams' not in response:
        return None

    return response['streams']

def get_game_streams(game):
    query = { 'game': game }
    url = 'https://api.twitch.tv/kraken/streams/?{}'.format(urlencode(query))
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Authorization': 'OAuth {}'.format(config['oauth'])
    }
    request = requests.get(url, headers=headers)
    response = request.json()

    if 'streams' not in response:
        return None

    return response['streams']

def print_stream_list(streams, title=None, flat=False):
    if title and not flat:
        print(title)
        print('')

    if flat:
        format = '{1[channel][name]}'
    else:
        ind_len = len(str(len(streams)))
        format = ('{0: >' + str(ind_len + 2) + 's} {1[channel][display_name]}: '
                  '{1[channel][status]}\n' +
                  (' ' * (ind_len + 3)) + '{1[channel][name]} playing '
                  '{1[channel][game]} for {1[viewers]} viewers\n')

    i = 1
    for stream in streams:
        print(format.format('[' + str(i) + ']', stream))
        i += 1

def follow_channel(channel):
    own_id = get_own_channel_id()
    channel_id = get_channel_id(channel)

    if channel_id is None:
        print('The channel "{}" does not exist'.format(channel))
        return

    url = 'users/{}/follows/channels/{}'.format(own_id, channel_id)
    response = twitchapi_request(url, method='put')
    print('You now follow {}'.format(channel))

def unfollow_channel(channel):
    own_id = get_own_channel_id()
    channel_id = get_channel_id(channel)

    if channel_id is None:
        print('The channel "{}" does not exist'.format(channel))
        return

    url = 'users/{}/follows/channels/{}'.format(own_id, channel_id)
    response = twitchapi_request(url, method='delete')
    print('You don\'t follow {} anymore'.format(channel))

def get_own_channel_id():
    url = ''
    response = twitchapi_request(url)
    return response['token']['user_id']

def get_channel_id(name):
    query = { 'login': name }
    url = 'users?{}'.format(urlencode(query))
    response = twitchapi_request(url)

    if response['_total'] == 0:
        return None

    return response['users'][0]['_id']

def authenticate():
    query = {
        'client_id': TWITCH_CLIENT_ID,
        'redirect_uri': 'https://butt4cak3.github.io/twitch-cli/oauth.html',
        'response_type': 'token',
        'scope': 'user_follows_edit'
    }
    url = ('https://api.twitch.tv/kraken/oauth2/authorize/?{}'
           .format(urlencode(query)))

    try:
        if not webbrowser.open_new_tab(url):
            raise webbrowser.Error
    except webbrowser.Error:
        print('Couldn\'t open a browser. Open this URL in your browser to '
              'continue:')
        print(url)
        return

    token = input('OAuth token: ')
    return token.strip()

def twitchapi_request(url, method='get'):
    url = 'https://api.twitch.tv/kraken/' + url
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': 'OAuth {}'.format(config['oauth'])
    }
    if method == 'get':
        request = requests.get(url, headers=headers)
    elif method == 'put':
        request = requests.put(url, headers=headers)
    elif method == 'delete':
        request = requests.delete(url, headers=headers)

    try:
        data = request.json()
    except:
        print(request.text)
        return None

    return data

if __name__ == '__main__':
    main()
