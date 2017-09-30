#!/usr/bin/python3
import os
import sys
import requests
import subprocess
import json
import argparse

# The configuration file is located at $HOME/.config/twitch-cli/config.json.
CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.config/twitch-cli')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def main():
    parser = argparse.ArgumentParser(description='List or play Twitch streams.')
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list', help='List followed channels')
    parser_list.set_defaults(func=cmd_list)

    parser_play = subparsers.add_parser('play', help='Play a stream')
    parser_play.add_argument('channel', help='Channel name')
    parser_play.set_defaults(func=cmd_play)

    args = parser.parse_args()

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

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4)

    return config

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
        print('You have to provide a Twitch OAuth token to list followed streams.')
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
        print('Something went wrong while trying to fetch data from the Twitch API')
        sys.exit(1)

    print('Streams online now:')
    print('')

    i = 1
    for stream in response['streams']:
        print('[{}] {}: {}'.format(i, stream['channel']['display_name'], stream['channel']['status']))
        print('    {} playing {} for {} viewers'.format(stream['channel']['name'], stream['game'], stream['viewers']))
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

if __name__ == '__main__':
    main()
