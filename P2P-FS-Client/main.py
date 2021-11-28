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
    TCPConnected = False  # Check to see if client is connected to server over TCP
    name = ''
    response = ''

    # UDP Socket
    try:
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    while True:
        msg = input('Enter message to send (Enter \'menu\' for list of commands. Enter \'q\' to quit): ')

        if msg == 'menu':
            dc.display_commands()
        elif msg == 'q':
            # De-register the user when the program quits
            cleanup_de_register(socketUDP, name)
            socketTCP.close()
            socketUDP.close()
            sys.exit()
        # If name does not exist then the user has not Registered
        elif not name:
            client_host, client_port_UDP, client_port_TCP, name = pc.get_data(msg)

            if not isBound and client_host and client_port_UDP and client_port_TCP:

                # Binding only needs to happen once
                socketUDP.bind((client_host, client_port_UDP))
                socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socketTCP.bind(('', client_port_TCP))
                isBound = 1

            if isBound:
                response = send_data_to(socketUDP, msg)

            # Require user to re-register if it has been denied
            if response.split(' ')[0] == 'REGISTER-DENIED':
                name = ''

            # Establish TCP connection with server on Register
            if name and not TCPConnected:
                try:
                    # socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    socketTCP.connect(('', 11111))

                    # socketTCPBackup.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    # socketTCPBackup.connect(('', 22222))
                except Exception as e:
                    # Address already in use...
                    print(f"Error... {e}")
                    cleanup_de_register(socketUDP, name)
                    socketTCP.close()
                    socketUDP.close()
                    sys.exit()

                socketTCP.send(name.encode())
                TCPConnected = True

        elif msg.split(' ')[0] == 'REGISTER':
            print('Client is already Registered')

        elif msg.split(' ')[0] == 'UPDATE-CONTACT':
            serverMsg = send_data_to(socketUDP, msg)
            if serverMsg.split(' ')[0] == 'UPDATE-CONFIRMED':
                # Have to close the ports and set the new ports
                try:
                    if int(msg.split(' ')[4]) != client_port_UDP:
                        # Close UDP and bind to new port
                        socketUDP.close()

                        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        client_port_UDP = int(msg.split(' ')[4])
                        socketUDP.bind((client_host, client_port_UDP))
                    if int(msg.split(' ')[5]) != client_port_TCP:
                        # Close TCP and bind to new port
                        socketTCP.close()

                        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_port_TCP = int(msg.split(' ')[5])
                        socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        socketTCP.bind((client_host, client_port_TCP))

                        socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        socketTCP.connect(('', 11111))
                except Exception as e:
                    print(f"Error: {e}")
        elif msg.split(' ')[0] == 'PUBLISH':
            all_files = msg.split(' ')[3:]
            # Before sending all we should check to see if a connection is available
            try:
                socketTCP.sendall(pf.SerializeFiles(msg, all_files))
                serverMsg = socketTCP.recv(1024)

                if not serverMsg:
                    # If serverMsg is empty then connection to server has ended.
                    print("Server Connection Terminated...")
                    # Need to reconnect
                    socketTCP.detach()
                    socketTCP.connect(('', 11111))
                    socketTCP.sendall(pf.SerializeFiles(msg, all_files))

                else:
                    print(f"Server Reply: {serverMsg.decode()}")

            except Exception as e:
                print(f"Error {e}... Server may be down. Wait a few seconds and then try again...")
                # socketTCP.close()
                # socketUDP.close()
                # sys.exit()

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
            send_data_to(socketUDP, msg)


if __name__ == '__main__':
    start_UDP_connection()
