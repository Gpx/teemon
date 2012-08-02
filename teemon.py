#!/usr/bin/env python
import argparse
import lightblue
import signal
import sys


def signal_handler(signal, frame):
    sys.exit(0)


def get_connected_socket(verbose):
    service = lightblue.selectservice()
    if service == None:
        sys.exit(0)
    socket = lightblue.socket()
    socket.connect((service[0], service[1]))
    signal.signal(signal.SIGINT, signal_handler)
    if verbose:
        print 'You are now connected. Press Ctrl+D to exit.'
    return socket


def send_medp(socket, command):
    MEDP_START = 'medp#'
    MEDP_END = '\n'
    MEDP_COMMAND_SEPARATOR = '&'

    if MEDP_START in command:
        command = command[len(MEDP_START):]
    if MEDP_END in command:
        command = command[-len(MEDP_END)]
    command = command.upper().replace(' ', MEDP_COMMAND_SEPARATOR)

    socket.send(MEDP_START + command + MEDP_END)


def main():
    parser = argparse.ArgumentParser(
        description='Move Poomba and execute tests on it',
        epilog='Please Disney do not suit me'
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='start an interactive console to move Poomba'
    )
    parser.add_argument(
        '-m', '--move',
        nargs='+',
        type=argparse.FileType('r'),
        help='read a medp message from files and send it to Poomba'
    )
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='start default tests on Poomba and dysplay results'
    )
    parser.add_argument(
        '-v', '--no-verbose',
        action='store_false',
        help='disable help messages'
    )

    arguments = parser.parse_args()

    if arguments.test:
        pass
    elif arguments.interactive:
        socket = get_connected_socket(arguments.no_verbose)
        while True:
            try:
                command = raw_input()
            except EOFError:
                exit(0)
            send_medp(socket, command)
    elif arguments.move != None:
        socket = get_connected_socket(arguments.no_verbose)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
