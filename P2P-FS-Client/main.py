import socket
import sys
import display_commands as dc
import parse_commands as pc
import publish_files as pf

def cleanup_de_register(s, host, port, name):
    if name:
        msg = 'DE-REGISTER 99998 ' + name
        send_data_to(s, msg, host, port)


def send_data_to(s, msg, host, port):
    try:
        s.sendto(str.encode(msg), (host, port))
        d = s.recvfrom(1024)
        reply = str(d[0].decode())
        addr = d[1]

        print('Server Reply: ' + reply + '\n')

        return reply
    except socket.error:
        print('Error')


def start_UDP_connection():
    client_host = ''  # Can be '0.0.0.0'
    client_port_UDP = 0  # Can be 8889
    client_port_TCP = 0  # Can be 10000
    isBound = 0  # True if the socket has bound
    name = ''

    # UDP Socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    # Server IP and Port
    host = 'localhost'
    port = 8888

    while 1:
        msg = input('Enter message to send (Enter \'menu\' for list of commands. Enter \'q\' to quit): ')

        if msg == 'menu':
            dc.display_commands()
        elif msg == 'q':
            # De-register the user when the program quits
            cleanup_de_register(s, host, port, name)
            s.close()
            sys.exit()
        # If name does not exist then the user has not Registered
        elif not name:
            client_host, client_port_UDP, client_port_TCP, name = pc.get_data(msg)

            if not isBound:
                s.bind((client_host, client_port_UDP))
                isBound = 1

            response = send_data_to(s, msg, host, port)

            # Require user to re-register if it has been denied
            if response.split(' ')[0] == 'REGISTER-DENIED':
                name = ''

        elif msg.split(' ')[0] == 'REGISTER':
            print('Client is already Registered')

        elif (msg.split(' ')[0] == 'PUBLISH' and len(msg.split(' '))>3):
            all_files=msg[3:]
            for file in all_files:
                pf.SerializeFile(file)
        else:
            send_data_to(s, msg, host, port)


if __name__ == '__main__':
    start_UDP_connection()
