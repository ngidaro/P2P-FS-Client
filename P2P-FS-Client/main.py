import socket
import sys
import display_commands as dc
import parse_commands as pc


def send_data_to(s, msg, host, port):
    try:
        s.sendto(str.encode(msg), (host, port))
        d = s.recvfrom(1024)
        reply = str(d[0].decode())
        addr = d[1]

        print('Server Reply: ' + reply + '\n')
    except socket.error:
        print('Error')


def start_UDP_connection():
    client_host = ''  # Can be '0.0.0.0'
    client_port_UDP = 0  # Can be 8889
    client_port_TCP = 0  # Can be 10000

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
        msg = input('Enter message to send (Enter \'menu\' for list of commands): ')

        if msg == 'menu':
            dc.display_commands()
        else:

            if not client_host and not client_port_UDP and not client_port_TCP:
                client_host, client_port_UDP, client_port_TCP = pc.get_data(msg)
                if client_host and client_port_UDP and client_port_TCP:
                    s.bind((client_host, client_port_UDP))
                    send_data_to(s, msg, host, port)
            else:
                send_data_to(s, msg, host, port)


if __name__ == '__main__':
    start_UDP_connection()
