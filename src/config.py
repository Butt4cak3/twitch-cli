import os
import json

CONFIG_FILE = None
config = None

def get_config_dir():
    if os.name == 'nt':
        return os.path.join(os.environ['APPDATA'], 'twitch-cli')
    elif os.name == 'posix':
        home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        return os.path.expanduser(os.path.join(home, 'twitch-cli'))

def load_config():
    global CONFIG_FILE
    global config

    if CONFIG_FILE is None:
        CONFIG_DIR = get_config_dir()
        CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
    else:
        CONFIG_DIR = os.path.dirname(CONFIG_FILE)

    if CONFIG_DIR != '' and not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.isfile(CONFIG_FILE):
        config = {}
        print('Creating configuration file at {}'.format(CONFIG_FILE))
    else:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

    config.setdefault('oauth', '')
    config.setdefault('quality', [])

    save_config()

def save_config():
    global config

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4)

def set_config_path(path):
    global CONFIG_FILE
    CONFIG_FILE = path = path

def get_config():
    return config
