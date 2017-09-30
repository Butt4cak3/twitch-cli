#!/usr/bin/python3
import os
import sys
import requests
import subprocess
import json

CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.config/twitch-cli')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def main():
    config = load_config()

    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = 'list'

    if command == 'help':
        show_usage()
    elif command == 'list':
        list_followed(config)
    elif command == 'play':
        if len(sys.argv) < 3:
            show_usage()
            return

        channel = sys.argv[2]
        play_stream(config, channel)
    else:
        play_stream(config, command)

def load_config():
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

def play_stream(config, channel):
    command = 'streamlink twitch.tv/{} best '.format(channel)
    if config['oauth'] != '':
        command += ' --twitch-oauth-token {}'.format(config['oauth'])
    if config['player'] != '':
        command += ' --player {}'.format(config['player'])

    process = subprocess.Popen(command.split(), stdout=None, stderr=None)
    output, error = process.communicate()

def list_followed(config):
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

    play_stream(config, response['streams'][selection - 1]['channel']['name'])

def show_usage():
    print('Usage:')
    print('  twitch-cli                  Same as list')
    print('  twitch-cli list             Lists followed channels')
    print('  twitch-cli play <channel>   Opens a stream')
    print('  twitch-cli <channel>        Same as play')
    print('  twitch-cli help             Prints this message')

if __name__ == '__main__':
    main()
