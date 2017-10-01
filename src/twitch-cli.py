#!/usr/bin/python3
import os
import sys
import requests
import subprocess
import json
import argparse
from urllib.parse import urlencode

# The configuration file is located at $HOME/.config/twitch-cli/config.json.
CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.config/twitch-cli')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def main():
    parser = argparse.ArgumentParser(description='List or play Twitch streams.')
    parser.add_argument('--oauth-token',
                        help='Save a Twitch oauth token to the config file')
    parser.add_argument('--player',
                        help='Save a player to the config file')

    subparsers = parser.add_subparsers(metavar='COMMAND')

    parser_list = subparsers.add_parser('list', help='List followed channels')
    parser_list.set_defaults(func=cmd_list)

    parser_play = subparsers.add_parser('play', help='Play a stream')
    parser_play.add_argument('channel', help='Channel name')
    parser_play.set_defaults(func=cmd_play)

    parser_auth = subparsers.add_parser('auth', help='Authenticate with Twitch')
    parser_auth.set_defaults(func=cmd_auth)

    args = parser.parse_args()

    config = load_config()

    if args.oauth_token is not None:
        oauth = args.oauth_token
        if oauth[0:6] == 'oauth:':
            oauth = oauth[6:]
        config['oauth'] = oauth

    if args.player is not None:
        config['player'] = args.player

    save_config(config)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        cmd_list(args)

# The cmd_* functions get called when their respective subcommand is executed
# Example: "python3 twitch-cli list" calls "cmd_list"

def cmd_list(args):
    list_followed()

def cmd_play(args):
    play_stream(args.channel)

def cmd_auth(args):
    config = load_config()

    if config['oauth'] != '':
        print('You are already authenticated.')

    config['oauth'] = authenticate(config)

    save_config(config)

def load_config():
    """Load the configuration file at ~/.config/twitch-cli/config.json and
    return a dict with configuration options."""

    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'a') as f:
            f.write('{}')
        print('Configuration file created at {}'.format(CONFIG_FILE))

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    config.setdefault('oauth', '')
    config.setdefault('player', '')

    save_config(config)

    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4)

def play_stream(channel, config=None):
    """Load a stream and open the player"""

    if config is None:
        config = load_config()

    command = 'streamlink twitch.tv/{} best '.format(channel)
    if config['oauth'] != '':
        command += ' --twitch-oauth-token {}'.format(config['oauth'])
    if config['player'] != '':
        command += ' --player {}'.format(config['player'])

    process = subprocess.Popen(command.split(), stdout=None, stderr=None)
    output, error = process.communicate()

def list_followed(config=None):
    """Load the list of followed streams and prompt the user to chose one."""

    if config is None:
        config = load_config()

    if config['oauth'] == '':
        print('You have to provide a Twitch OAuth token to list followed '
              'streams.')
        print('Look at the configuration file at {}'.format(CONFIG_FILE))
        sys.exit(1)

    url = 'https://api.twitch.tv/kraken/streams/followed'
    headers = {
        'Accept': 'application/vnd.twitchtv.v3+json',
        'Authorization': 'OAuth {}'.format(config['oauth'])
    }
    request = requests.get(url, headers=headers)
    response = request.json()

    if 'streams' not in response:
        print('Something went wrong while trying to fetch data from the '
              'Twitch API')
        sys.exit(1)

    print('Streams online now:')
    print('')

    ind_len = len(str(len(response['streams'])))
    format = ('{0: >' + str(ind_len + 2) + 's} {1[channel][display_name]}: '
              '{1[channel][status]}\n' +
              (' ' * (ind_len + 3)) + '{1[channel][name]} playing '
              '{1[channel][game]} for {1[viewers]} viewers')

    i = 1
    for stream in response['streams']:
        print(format.format('[' + str(i) + ']', stream))
        print('')
        i += 1

    selection = input('Stream ID: ')
    try:
        selection = int(selection)
    except:
        return

    if selection > len(response['streams']):
        return

    play_stream(response['streams'][selection - 1]['channel']['name'], config)

def authenticate(config):
    query = {
        'client_id' :'e0fm2z7ufk73k2jnkm21y0gp1h9q2o',
        'redirect_uri': 'https://butt4cak3.github.io/twitch-cli/oauth.html',
        'response_type': 'id_token',
        'scope': 'openid'
    }
    url = 'https://api.twitch.tv/kraken/oauth2/authorize?{}'.format(urlencode(query))
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json'
    }

    print(url)

if __name__ == '__main__':
    main()
