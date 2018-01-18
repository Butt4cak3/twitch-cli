#!/usr/bin/python3
import os
import sys
import requests
import subprocess
import json
import click
from termcolor import colored, COLORS
from urllib.parse import urlencode
import webbrowser
from config import *

TWITCH_CLIENT_ID = 'e0fm2z7ufk73k2jnkm21y0gp1h9q2o'
COLORS.update({
    'light_grey': 90,
    'light_red': 91,
    'light_green': 92,
    'light_yellow': 93,
    'light_blue': 94,
    'light_magenta': 95,
    'light_cyan': 96,
    'light_white': 97
})

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
@click.option('-q', '--quality', multiple=True, help='Stream quality')
def cmd_live(flat, game, quality):
    """List live channels"""
    list_streams(game=game, flat=flat, playback_quality=quality)

@main.command('vods')
@click.option('--flat', is_flag=True, help='Don\'t show detailed information or prompt')
@click.argument('channel')
@click.option('-q', '--quality', multiple=True, help='Stream quality')
def cmd_vods(channel, flat, quality):
    """List past streams of a channel"""
    list_vods(channel, flat, playback_quality=quality)

@main.command('play')
@click.option('-q', '--quality', multiple=True, help='Stream quality')
@click.argument('channel')
def cmd_play(channel, quality):
    """Play a livestream"""
    play_stream(channel, quality=quality)

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
    config = get_config()
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

def get_available_streams(url):
    command = 'streamlink -j {}'.format(url)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    j_out = json.loads(output.decode())
    streams = []
    for stream in j_out['streams']:
        streams.append(stream)

    return streams

def play_url(url, quality=None):
    if quality is None or len(quality) == 0:
        config = get_config()
        quality = config['quality']

    stream = 'best'
    if len(quality) > 0 and quality[0] not in ('best', 'worst'):
        streams = get_available_streams(url)
        for q in quality:
            if q in streams:
                stream = q
                break

    command = 'streamlink {} {}'.format(url, stream)
    process = subprocess.Popen(command.split(), stdout=None, stderr=None)
    output, error = process.communicate()

def play_stream(channel, quality=None):
    """Load a stream and open the player"""

    channel_id = get_channel_id(channel)

    if channel_id is None:
        print('The channel "{}" does not exist'.format(channel))
        return

    play_url('twitch.tv/{}'.format(channel), quality=quality)

def list_streams(game=None, flat=False, playback_quality=None):
    """Load the list of streams and prompt the user to chose one."""
    config = get_config()

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
    elif len(streams) == 0:
        print('No streams online now')
        return

    print_stream_list(streams, title='Streams online now', flat=flat)

    if not flat:
        selection = input('Stream ID: ')
        try:
            selection = int(selection)
        except:
            return
    else:
        return

    if not (0 < selection <= len(streams)):
        return

    play_stream(streams[selection - 1]['channel']['name'], quality=playback_quality)

def get_followed_streams():
    config = get_config()

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
    config = get_config()

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

def list_vods(channel, flat, playback_quality=None):
    vods = get_channel_vods(channel)

    if vods is None:
        return
    elif len(vods) == 0:
        print('No recent VODs for {}'.format(channel))
        return

    print_vod_list(vods, title='{}\'s recent VODs'.format(channel))
    if not flat:
        selection = input('VOD ID: ')
        try:
            selection = int(selection)
        except:
            return

        if (0 < selection <= len(vods)):
            play_url(vods[selection-1]['url'], quality=playback_quality)

def get_channel_vods(channel):
    config = get_config()
    channel_id = get_channel_id(channel)

    if channel_id is None:
        print('The channel "{}" does not exist'.format(channel))
        return

    url = 'https://api.twitch.tv/kraken/channels/{}/videos?broadcast_type=archive'.format(channel_id)
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Authorization': 'OAuth {}'.format(config['oauth'])
    }
    request = requests.get(url, headers=headers)
    response = request.json()

    if 'videos' not in response:
        return None

    return response['videos']

def print_stream_list(streams, title=None, flat=False):
    if title and not flat:
        print(title)
        print('')

    if flat:
        format = '{1[channel][name]}'
    else:
        ind_len = len(str(len(streams)))
        bullet          = '{0: >' + str(ind_len + 2) + 's}'
        display_name    = '{1[channel][display_name]}'
        status          = '{1[channel][status]}'
        #channel_name    = '{1[channel][name]}'
        game            = '{1[channel][game]}'
        viewers         = '[{1[viewers]} viewers]'
        format = (colored(bullet + ' ',         'light_red')
                + colored(display_name + ': ',  'light_blue', attrs=['bold'])
                + colored(game + ' ',           'light_yellow')
                + colored(viewers + '\n',       'light_green')
                + (' ' * (ind_len + 3))
                + colored(status + '\n',        'light_grey'))

    i = 1
    for stream in streams:
        print(format.format('[' + str(i) + ']', stream))
        i += 1

def print_vod_list(vods, title=None, flat=False):
    if title and not flat:
        print(title)
        print('')

    if flat:
        format = '{1[url]}'
    else:
        ind_len = len(str(len(vods)))
        bullet  = '{0: >' + str(ind_len + 2) + 's}'
        game    = '{1[game]}'
        title   = '{1[title]}'
        date    = 'Recorded: {1[created_at]}'
        format = (colored(bullet + ' ',     'light_red')
                + colored(game + ': ',      'light_blue', attrs=['bold'])
                + colored(title + '\n',     'light_yellow')
                + (' ' * (ind_len + 3))
                + colored(date + '\n',      'light_grey'))

        i = 1
        for vod in vods:
            print(format.format('[' + str(i) + ']', vod))
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
    config = get_config()

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
