import configparser, sys, re, os, subprocess, time

time.sleep(1)

def pause():
    programPause = input("Press the <ENTER> key to continue...")

# exit if we don't get a nxm url
nxm_url = ''
if len(sys.argv) <= 1:
    print('NXM URL was not provided.')
    pause()
    sys.exit(1)

nxm_url = sys.argv[1]

try:
    # load config
    config_path = os.path.dirname(sys.argv[0]) + '/nxmproxy.ini'
    if not os.path.exists(config_path):
        print(f'Settings file was not found at `{config_path}`')
        pause()
        sys.exit(2)

    config = configparser.ConfigParser()
    config.read(config_path)

    if len(config.sections()) == 0:
        print(f'Settings file looks incorrect.')
        pause()
        sys.exit(3)


    # process the url
    # nxm://fallout76/mods/405/files/4959?key=XXXX&expires=####&user_id=####
    match = re.match(r"^nxm:\/\/([^\/]+)(.+)$", nxm_url, re.IGNORECASE)

    if match == None:
        print(f'NXM URL `{nxm_url}` is invalid.')
        pause()
        sys.exit(4)

    game = match[1]


    # get the correct handler for the game, and it's path
    if game not in config['HANDLERS'] and 'default' not in config['HANDLERS']:
        print(f'Game `{game}` was not defined under HANDLERS, and no default handler was defined either.')
        pause()
        sys.exit(5)
    elif game not in config['HANDLERS']:
        handler = config['HANDLERS']['default']
    else:
        handler = config['HANDLERS'][game]

    if handler not in config['PATHS'] or not config['PATHS'][handler]:
        print(f'Handler `{handler}` was not defined under PATHS.')
        pause()
        sys.exit(6)

    path = config['PATHS'][handler]


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
    print("Error: " + str(err))
    pause()
    sys.exit(50)
