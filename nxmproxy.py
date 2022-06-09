import configparser
import ctypes
import os
import re
import subprocess
import sys


#  Styles:
#  0 : OK
#  1 : OK | Cancel
#  2 : Abort | Retry | Ignore
#  3 : Yes | No | Cancel
#  4 : Yes | No
#  5 : Retry | Cancel
#  6 : Cancel | Try Again | Continue
def message_box(title, text, style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


# exit if we don't get a nxm url
if len(sys.argv) <= 1:
    message_box("NxmProxy Error", "NXM URL was not provided.")
    sys.exit(1)


nxm_url = sys.argv[1]

try:
    # load config
    config_path = os.path.dirname(sys.argv[0]) + '/nxmproxy.ini'
    if not os.path.exists(config_path):
        message_box("NxmProxy Error", f'Settings file was not found at `{config_path}`')
        sys.exit(2)

    config = configparser.ConfigParser()
    config.read(config_path)

    if len(config.sections()) == 0:
        message_box("NxmProxy Error", 'Settings file looks incorrect')
        sys.exit(3)

    # process the url
    # nxm://fallout76/mods/405/files/4959?key=XXXX&expires=####&user_id=####
    match = re.match(r"^nxm://([^/]+)(.+)$", nxm_url, re.IGNORECASE)

    if match is None:
        message_box("NxmProxy Error", f'NXM URL `{nxm_url}` is invalid.')
        sys.exit(4)

    game = match[1]

    # get the correct handler for the game, and it's path
    if game not in config['Handlers'] and 'default' not in config['Handlers']:
        message_box("NxmProxy Error", f'Game `{game}` was not defined under Handlers, and no default handler was defined either.')
        sys.exit(5)
    elif game not in config['Handlers']:
        defaultHandler = config['Handlers']['default']
        response = message_box("NxmProxy Error", f'A handler for `{game}` was not defined under Handlers, would you like to open the config file? Click "No" to use the default handler ({defaultHandler}), or click "Cancel" to abort.', style=3)
        print(response)
        # 6 = Yes, 7 = No, 2 = Cancel
        if response == 7:
            handler = defaultHandler
        if response == 6:
            subprocess.Popen(f'notepad.exe {config_path}')
            sys.exit(0)
        if response == 2:
            sys.exit(7)
    else:
        handler = config['Handlers'][game]

    if handler not in config['Paths'] or not config['Paths'][handler]:
        message_box("NxmProxy Error", f'Handler `{handler}` was not defined under Paths.')
        sys.exit(6)

    path = config['Paths'][handler]

    # pass the nxm:// url to the proxied executable
    if path[0] != '"':
        path = f'"{path}"'

    if "{0}" in path:
        cmd = path.replace("{0}", nxm_url)
    else:
        cmd = f'{path} "{nxm_url}"'

    print('Launching...')
    subprocess.Popen(cmd)
    sys.exit(0)
except Exception as err:
    message_box("NxmProxy Error", "Error: " + str(err))
    sys.exit(50)
