import socket
import sys
import display_commands as dc
import publish_files as pf
from Server import Server
from parse import parse_commands as pc
import pickle

# Functions which executes when user enters 'q' in the console. This is to De-register the user on "logout"
def cleanup_de_register(s, name):
    if name:
        msg = 'DE-REGISTER 99998 ' + name
        send_data_to(s, msg)


# Function which sends the message to the server
def send_data_to(s, msg):
    # List of available servers
    servers = [Server('localhost', 8888), Server('localhost', 3000)]

    # Loop through all servers and send message to any one that is running
    for server in servers:
        exactRQNumber = 1
        while exactRQNumber:
            try:
                s.sendto(str.encode(msg), (server.host, server.port))

                # 3 second timeout... if there is a timeout, then try to send message to the next server
                s.settimeout(3)
                d = s.recvfrom(1024)

                reply = str(d[0].decode())
                addr = d[1]

                # Will check if the request # sent from the client matches the request # returned by the server
                # If they don't match then resend the msg...
                parsedReply = reply.split(' ')

                if len(parsedReply) > 2 and parsedReply[1].isnumeric():
                    if msg.split(' ')[1] == parsedReply[1]:
                        print('Server Reply: ' + reply + '\n')
                        return reply
                else:
                    print('Server Reply: ' + reply + '\n')
                    return reply

            except socket.timeout as e:
                # set this to 0 to break out of while loop and move on to next server
                exactRQNumber = 0
                continue

    return ''


def start_UDP_connection():
    client_host = ''  # Can be '0.0.0.0'
    client_port_UDP = 0  # Can be 8889
    client_port_TCP = 0  # Can be 10000
    isBound = 0  # True if the socket has bound
    name = ''
    response = ''

    # UDP Socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    while 1:
        msg = input('Enter message to send (Enter \'menu\' for list of commands. Enter \'q\' to quit): ')

        if msg == 'menu':
            dc.display_commands()
        elif msg == 'q':
            # De-register the user when the program quits
            cleanup_de_register(s, name)
            s.close()
            sock.close()
            sys.exit()
        # If name does not exist then the user has not Registered
        elif not name:
            client_host, client_port_UDP, client_port_TCP, name = pc.get_data(msg)

            if not isBound and client_host and client_port_UDP and client_port_TCP:
                server_address = ('', 10000)
                s.bind((client_host, client_port_UDP))
                sock.bind(('', 10010))
                isBound = 1
                sock.connect(server_address)

            if isBound:
                response = send_data_to(s, msg)

            # Require user to re-register if it has been denied
            if response.split(' ')[0] == 'REGISTER-DENIED':
                name = ''

        elif msg.split(' ')[0] == 'REGISTER':
            print('Client is already Registered')

        elif msg.split(' ')[0] == 'PUBLISH' and len(msg.split(' ')) > 3:
            all_files = msg.split(' ')[3:]

            sock.sendall(pf.SerializeFiles(all_files))
            send_data_to(s, msg)

        elif msg.split(' ')[0] == 'REMOVE' and len(msg.split(' ')) > 3:
            send_data_to(s, msg)

        elif msg.split(' ')[0] == 'DOWNLOAD' and len(msg.split(' ')) == 3:
            send_data_to(s, msg)
            f = open(msg.split(' ')[2], 'w')
            chunknumber = 1
            allcontent=b""
            while True:
                content=sock.recv(200)
                allcontent+=content
                if len(content)<200:
                    print('File-End' +' '+ msg.split(' ')[2] + ' ' + msg.split(' ')[1] + ' ' + str(chunknumber) + ' ' + 'TEXT')
                    break
                else:
                    print ('File ' + msg.split(' ')[2] + ' ' + msg.split(' ')[1] + ' ' + str(chunknumber)+ ' ' + 'TEXT')
                    chunknumber += 1
            unserializedcontent=pickle.loads(allcontent)
            print(unserializedcontent)
            for word in unserializedcontent:
                f.write(word)
            f.close()



        else:
            send_data_to(s, msg)


if __name__ == '__main__':
    start_UDP_connection()