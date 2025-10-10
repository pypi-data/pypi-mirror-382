import argparse, platformdirs, configparser, sys
from loguru import logger
from pprint import pprint, pformat
from pathlib import Path


CONF_FILE = 'mamsync.cfg'
LOG_FILE = 'mamdone.txt'

logger.remove()
# logger.add(sys.stdout, level="DEBUG")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "write_conf")


def print_out_conf(raw_root, synced_root, snd_root, proxies=''):
    print(f'RAWROOT (source with TC): "{raw_root}"')
    print(f'SYNCEDROOT (destination of synced folder): "{synced_root}"')
    print(f'SNDROOT (destination of ISOs sound files): "{snd_root}"')
    if proxies != '':
        print(f'PROXIES (NLE proxy clips folder): "{proxies}"')

def write_conf(conf_key, conf_val):
    # args are pahtlib.Paths.
    # RAWROOT: files with TC (and ROLL folders), as is from cameras
    # SYNCEDROOT: synced and no more TC (ROLL flattened)
    # Writes configuration on filesystem for later retrieval
    # Clears log of already synced clips.
    conf_dir = platformdirs.user_config_dir('mamsync', 'plutz', ensure_exists=True)
    current_values = dict(zip(['RAWROOT', 'SYNCEDROOT', 'SNDROOT', 'PROXIES'],
                        get_proj()))
    logger.debug(f'old values {current_values}')
    current_values[conf_key] = conf_val
    logger.debug(f'updated values {current_values}')
    conf_file = Path(conf_dir)/CONF_FILE
    logger.debug('writing config in %s'%conf_file)
    # print(f'\nWriting folders paths in configuration file "{conf_file}"')
    # print_out_conf(raw_root, synced_root, snd_root)
    conf_prs = configparser.ConfigParser()
    conf_prs['SECTION1'] = current_values
    with open(conf_file, 'w') as configfile_handle:
        conf_prs.write(configfile_handle)
    with open(conf_file, 'r') as configfile_handle:
        logger.debug(f'config file content: \n{configfile_handle.read()}')

def get_proj(print_conf_stdout=False):
    # check if user started a project before.
    # stored in platformdirs.user_config_dir
    # returns a tuple of strings (RAWROOT, SYNCEDROOTS, SNDROOT, PROXIES)
    # if any, or a tuple of 4 empty strings '' otherwise.
    # print location of conf file if print_conf_stdout
    conf_dir = platformdirs.user_config_dir('mamsync', 'plutz')
    conf_file = Path(conf_dir)/CONF_FILE
    logger.debug('try reading config in %s'%conf_file)
    if print_conf_stdout:
        print(f'\nTrying to read configuration from file {conf_file}')
    if conf_file.exists():
        conf_prs = configparser.ConfigParser()
        conf_prs.read(conf_file)
        try:
            RAWROOT = conf_prs.get('SECTION1', 'RAWROOT')
        except configparser.NoOptionError:
            RAWROOT = ''
        try:
            SYNCEDROOT = conf_prs.get('SECTION1', 'SYNCEDROOT')
        except configparser.NoOptionError:
            SYNCEDROOT = ''
        try:
            PROXIES = conf_prs.get('SECTION1', 'PROXIES')
        except configparser.NoOptionError:
            PROXIES = ''
        try:
            SNDROOT = conf_prs.get('SECTION1', 'SNDROOT')
        except configparser.NoOptionError:
            SNDROOT = ''
        logger.debug('read from conf: RAWROOT= %s SYNCEDROOT= %s SNDROOT=%s PROXIES=%s'%
                                    (RAWROOT, SYNCEDROOT, SNDROOT, PROXIES))
        return RAWROOT, SYNCEDROOT, SNDROOT, PROXIES
    else:
        logger.debug(f'no config file found at {conf_file}')
        print('No configuration found.')
        return '', '', '', ''

def new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rawroot',
                        nargs = 1,
                        dest='rawroot',
                        help='Sets new value for raw root folder (i.e.: clips with TC)')
    parser.add_argument('--syncedroot',
                        nargs = 1,
                        dest='syncedroot',
                        help="""Sets where the synced files will be written, to be used by the NLE. Will contain a mirror copy of RAWROOT """)
    parser.add_argument('--proxies',
                        nargs = 1,
                        dest='proxies',
                        help='Sets where the proxy files are stored by the NLE')
    parser.add_argument('--sndfolder',
                        nargs = 1,
                        dest='sndfolder',
                        help='Sets new value for sound folder (where ISOs sound files will be stored)')
    parser.add_argument('--clearconf',
                    action='store_true',
                    dest='clearconf',
                    help='Clear configured values.')
    parser.add_argument('--showconf',
                    action='store_true',
                    dest='showconf',
                    help='Show current configured values.')
    return parser

def main():
    parser = new_parser()
    args = parser.parse_args()
    logger.debug(f'arguments from argparse {args}')
    if args.rawroot:
        val = args.rawroot[0]
        write_conf('RAWROOT', val)
        print(f'Set source folder of unsynced clips (rawroot) to:\n{val}')
        sys.exit(0)
    if args.syncedroot:
        val = args.syncedroot[0]
        write_conf('SYNCEDROOT', args.syncedroot[0])
        print(f'Set destination folder of synced clips (syncedroot) to:\n{val}')
        sys.exit(0)
    if args.proxies:
        val = args.proxies[0]
        write_conf('PROXIES', args.proxies[0])
        print(f'Set proxies folder to:\n{val}')
        sys.exit(0)
    if args.sndfolder:
        val = args.sndfolder[0]
        write_conf('SNDROOT', args.sndfolder[0])
        print(f'Set destination folder of ISOs sound files (sndfolder) to:\n{val}')
        sys.exit(0)
    if args.clearconf:
        write_conf('RAWROOT', '')
        write_conf('SYNCEDROOT', '')
        write_conf('SNDROOT', '')
        write_conf('PROXIES', '')
        print_out_conf('','','','')
        sys.exit(0)
    if args.showconf:
        get_proj()
        print_out_conf(*get_proj(True))
        sys.exit(0)
    # roots = get_proj(False)
    # if any([r == '' for r in roots]):
    #     print("Can't sync if some folders are not set:")
    #     print_out_conf(*get_proj())
    #     print('Bye.')
    #     sys.exit(0)
    # for r in roots:
    #     if not r.is_absolute():
    #         print(f'\rError: folder {r} must be an absolute path. Bye')
    #         sys.exit(0)
    #     if not r.exists():
    #         print(f'\rError: folder {r} does not exist. Bye')
    #         sys.exit(0)
    #     if not r.is_dir():
    #         print(f'\rError: path {r} is not a folder. Bye')
    #         sys.exit(0)
    # raw_root, synced_root, snd_root = roots
    # if args.sub_dir != None:
    #     top_dir = args.sub_dir
    #     logger.debug(f'sub _dir: {args.sub_dir}')
    #     if not Path(top_dir).exists():
    #         print(f"\rError: folder {top_dir} doesn't exist, bye.")
    #         sys.exit(0)
    # else:
    #     top_dir = raw_root
    # if args.resync:
    #     clear_log()

if __name__ == '__main__':
    main()
