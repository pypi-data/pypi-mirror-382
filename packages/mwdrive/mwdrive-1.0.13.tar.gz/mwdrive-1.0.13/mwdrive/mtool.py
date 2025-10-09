"""Command-line entry point for mtool.

This module delays heavy imports until runtime and installs a temporary alias
so code that still does `import odrive` continues to work when the package is
installed as `mwdrive`.
"""
import sys
import argparse

def main(argv=None):
    # Delay heavy imports until invoked
    import importlib
    import logging

    # Import the package
    # mwdrive = importlib.import_module('mwdrive')
    import mwdrive.shell as mdrive_shell

    # Provide compatibility for modules that still import 'odrive'
    # if 'odrive' not in sys.modules:
        # sys.modules['odrive'] = mwdrive

    parser = argparse.ArgumentParser(prog='mtool', description='mwdrive interactive tool')
    parser.add_argument('--serial-number', dest='serial_number', help='Only connect to device with this serial number', default=None)
    parser.add_argument('--path', dest='path', help='USB path to look for devices', default=None)
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity')
    args = parser.parse_args(argv)

    # setup a simple logger compatible with the shell expectations
    level = logging.WARNING
    if args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO

    logger = logging.getLogger('mtool')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)

    # Delegate to the existing shell launcher
    mdrive_shell.launch_shell(args, logger)


if __name__ == '__main__':
    main()
