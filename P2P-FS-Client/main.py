import socket
import sys
import display_commands as dc
import publish_files as pf
from Server import Server
from parse import parse_commands as pc
import pickle

# Functions which executes when user enters 'q' in the console. This is to De-register the user on "logout"
def cleanup_de_register(s, name):
# ************************************************************
# initiateTCPSocket:
#   Description: Function initializes the TCP socket
#   Parameters:
#       CLIENT_HOST: The client's hostname
#       CLIENT_PORT_TCP: The client's port is want to bind to
# ************************************************************


def initiateTCPSocket(CLIENT_HOST, CLIENT_PORT_TCP):
    socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketTCP.bind((CLIENT_HOST, CLIENT_PORT_TCP))
    socketTCP.connect(('', 11111))

    return socketTCP


# ************************************************************
# cleanupDeRegister:
#   Description: Functions which executes when user enters 'q' in the console.
#       This is to De-register the user on "logout"
#   Parameters:
#       socketUDP: The client's UDP socket
#       name: The client's unique name (username)
# ************************************************************


def cleanupDeRegister(socketUDP, name):
    if name:
        msg = 'DE-REGISTER 99998 ' + name
        sendDataToServer(socketUDP, msg)


# ************************************************************
# sendDataToServer:
#   Description: Function which sends the UDP message to the server
#   Parameters:
#       socketUDP: The client's UDP socket
#       msg: The command message the client inputted into the console
# ************************************************************


def sendDataToServer(socketUDP, msg):
    server = Server('localhost', 8888)
    while True:
        try:

            socketUDP.sendto(str.encode(msg), (server.host, server.port))

            d = socketUDP.recvfrom(1024)

            reply = str(d[0].decode())

            # Will check if the request # sent from the client matches the request # returned by the server
            # If they don't match then resend the msg...
            parsedReply = reply.split(' ')

            # Check to make sure the RQ# sent is the same one received, or else re-loop
            if len(parsedReply) > 2 and parsedReply[1].isnumeric():
                if msg.split(' ')[1] == parsedReply[1]:
                    print('Server Reply: ' + reply + '\n')
                    return reply
                else:
                    continue
            else:
                print('Server Reply: ' + reply + '\n')
                return reply
        except Exception as e:
            pass
    return ''


# ************************************************************
# startConnection:
#   Description: Function which starts the TCP and UDP connections and handles user command inputs
#   Parameters: NONE
# ************************************************************


def startConnection():
    client_host = ''  # Can be '0.0.0.0'
    client_port_UDP = 0  # Can be 8889
    client_port_TCP = 0  # Can be 10000
    isBound = False  # True if the socket has bound
    TCPConnected = False  # Check to see if client is connected to server over TCP
    name = ''
    response = ''

    # UDP & TCP Socket initialization
    try:
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    while True:
        msg = input('Enter message to send (Enter \'menu\' for list of commands. Enter \'q\' to quit): ')

        if msg == 'menu':
            dc.displayCommands()
        elif msg == 'q':
            # De-register the user when the program quits
            cleanupDeRegister(socketUDP, name)
            socketTCP.close()
            socketUDP.close()
            sys.exit()
        # If name does not exist then the user has not Registered
        elif not name:
            client_host, client_port_UDP, client_port_TCP, name = pc.validateUserCommand(msg)

            if not isBound and client_host and client_port_UDP and client_port_TCP:

                # Binding only needs to happen once
                socketUDP.bind((client_host, client_port_UDP))
                isBound = True

            if isBound:
                response = sendDataToServer(socketUDP, msg)

            # Require user to re-register if it has been denied
            if response.split(' ')[0] == 'REGISTER-DENIED':
                name = ''

            # Establish TCP connection with server on Register
            if name and not TCPConnected:
                try:
                    socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    socketTCP.bind(('', client_port_TCP))
                    socketTCP.connect(('', 11111))
                except Exception as e:
                    # Address already in use...
                    print(f"Error... {e}")
                    cleanupDeRegister(socketUDP, name)
                    socketTCP.close()
                    socketUDP.close()
                    sys.exit()

                socketTCP.send(name.encode())
                TCPConnected = True

        elif msg.split(' ')[0] == 'REGISTER':
            print('Client is already Registered')

        elif msg.split(' ')[0] == 'UPDATE-CONTACT':
            serverMsg = sendDataToServer(socketUDP, msg)
            if serverMsg.split(' ')[0] == 'UPDATE-CONFIRMED':
                # Have to close the ports and set the new ports
                try:
                    if int(msg.split(' ')[4]) != client_port_UDP:
                        # Close UDP and bind to new port
                        socketUDP.close()
                        client_port_UDP = int(msg.split(' ')[4])

                        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        socketUDP.bind((client_host, client_port_UDP))
                    if int(msg.split(' ')[5]) != client_port_TCP:
                        # Close TCP and bind to new port
                        socketTCP.close()
                        client_port_TCP = int(msg.split(' ')[5])

                        # Create new socket with new TCP port
                        socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                except Exception as e:
                    print(f"Error: {e}")

        elif msg.split(' ')[0] == 'PUBLISH':
            all_files = msg.split(' ')[3:]
            # Before sending all we should check to see if a connection is available
            try:
                socketTCP.sendall(pf.serializeFiles(msg, all_files))
                serverMsg = socketTCP.recv(1024)

                if not serverMsg:
                    # If serverMsg is empty then connection to server has ended. At this moment, the server may have
                    # terminated and then restored, so we have to create a new TCP socket

                    # Close TCP and bind to new port
                    socketTCP.close()

                    # Create new socket with new TCP port
                    socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                    socketTCP.sendall(pf.serializeFiles(msg, all_files))
                    serverMsg = socketTCP.recv(1024)

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
            sendDataToServer(socketUDP, msg)


if __name__ == '__main__':
    startConnection()
