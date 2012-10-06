#!/usr/bin/env python
import argparse
import lightblue
import signal
import sys
import time

DEFAULT_SERVICE = ('00:06:66:42:92:73', 1, 'SPP')


def signal_handler(signal, frame):
    sys.exit(0)


def get_connected_socket(use_default_socket):
    if not use_default_socket:
        service = lightblue.selectservice()
    else:
        service = DEFAULT_SERVICE

    if service == None:  # Used when user clicks on cancel
        sys.exit(0)

    socket = lightblue.socket()
    socket.connect((service[0], service[1]))
    signal.signal(signal.SIGINT, signal_handler)
    return socket


def send_medp(socket, command):
    MEDP_START = 'medp#'
    MEDP_END = '\n'
    MEDP_COMMAND_SEPARATOR = '&'

    if MEDP_START in command:
        command = command[len(MEDP_START):]
    if MEDP_END in command:
        command = command[-len(MEDP_END)]
    command = command.replace(' ', MEDP_COMMAND_SEPARATOR)

    socket.send(MEDP_START + command + MEDP_END)


def get_angle(socket):
    angle = ""
    while True:
        recv = socket.recv(1)
        if ord(recv) == 13:
            continue
        if ord(recv) == 10:
            break
        angle += recv
    return float(angle)


def test_angle(socket, direction, angle):
    time.sleep(2)
    command = direction + str(angle)
    send_medp(socket, command)
    result = get_angle(socket)
    print "{0:1}, {1:3}, {2:4}".format(direction, angle, result)


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
        '-d', '--default',
        action='store_false',
        help=('do not connect to the default bluetooth device [%s]' % DEFAULT_SERVICE[0])
    )

    arguments = parser.parse_args()

    if arguments.test:
        socket = get_connected_socket(arguments.default)
        for direction in ['l', 'r']:
            for angle in range(1, 361, 5):
                test_angle(socket, direction, angle)
        socket.close()

    elif arguments.interactive:
        socket = get_connected_socket(arguments.default)
        print "You are now connected. Press Ctrl+D to exit."
        while True:
            try:
                command = raw_input()
            except EOFError:
                exit(0)
            else:
                send_medp(socket, command)

    elif arguments.move != None:
        socket = get_connected_socket(arguments.default)
        for file in arguments.move:
            print 'Sending content of %s... ' % file.name,
            send_medp(socket, file.read())
            print 'done'
        socket.close()

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
