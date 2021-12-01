import socket
import sys
import display_commands as dc
import publish_files as pf
from Server import Server
from parse import parse_commands as pc
import pickle


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
        if sendDataToServer(socketUDP, msg, False) is False:
            return False
        else:
            return True


# ************************************************************
# sendDataToServer:
#   Description: Function which sends the UDP message to the server
#   Parameters:
#       socketUDP: The client's UDP socket
#       msg: The command message the client inputted into the console
#       printServerResponse: Let's the function know whether it should print or not
# ************************************************************


def sendDataToServer(socketUDP, msg, printServerResponse=True):
    server = Server('localhost', 8888)
    while True:
        try:
            socketUDP.sendto(str.encode(msg), (server.host, server.port))

            # 3 second timeout
            socketUDP.settimeout(3)
            d = socketUDP.recvfrom(1024)

            reply = str(d[0].decode())

            # Will check if the request # sent from the client matches the request # returned by the server
            # If they don't match then resend the msg...
            parsedReply = reply.split(' ')

            # Check to make sure the RQ# sent is the same one received, or else re-loop
            if len(parsedReply) > 2 and parsedReply[1].isnumeric():
                if msg.split(' ')[1] == parsedReply[1]:
                    if printServerResponse:
                        print('Server Reply: ' + reply + '\n')
                    return reply
                else:
                    continue
            else:
                if printServerResponse:
                    print('Server Reply: ' + reply + '\n')
                return reply
        except socket.timeout as e:
            print("Error: Connection Timed-out... Server may be down")
            return False
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
    serverMsg = ''

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
            if cleanupDeRegister(socketUDP, name) is not False:
                socketTCP.close()
                socketUDP.close()
                sys.exit()
        # If name does not exist then the user has not Registered
        elif not name:
            client_host, client_port_UDP, client_port_TCP, name = pc.validateUserCommand(msg)

            if not isBound and client_host and client_port_UDP and client_port_TCP:

                try:
                    # Binding only needs to happen once
                    socketUDP.bind((client_host, client_port_UDP))
                    isBound = True
                except Exception as e:
                    print(f"Error UDP: {e}")
                    socketUDP.close()
                    socketTCP.close()
                    sys.exit()

            if isBound:
                serverMsg = sendDataToServer(socketUDP, msg, False)

            if serverMsg is False:
                name = ''
                continue

            # Require user to re-register if it has been denied
            if 'REGISTER-DENIED' in serverMsg:
                name = ''

            # Establish TCP connection with server on Register
            if name and not TCPConnected:
                try:
                    socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    socketTCP.bind(('', client_port_TCP))
                    socketTCP.connect(('', 11111))
                except Exception as e:
                    # Address already in use...
                    print(f"Error TCP... {e}")
                    cleanupDeRegister(socketUDP, name)
                    socketTCP.close()
                    socketUDP.close()
                    sys.exit()

                socketTCP.send(name.encode())
                TCPConnected = True

            print(f"Server Reply: {serverMsg}")

        elif msg.split(' ')[0] == 'REGISTER':
            print('Client is already Registered')

        elif msg.split(' ')[0] == 'UPDATE-CONTACT':
            serverMsg = sendDataToServer(socketUDP, msg, False)
            if 'UPDATE-CONFIRMED' in serverMsg:

                try:
                    # Check to see if the port is available before binding
                    if int(msg.split(' ')[4]) != client_port_UDP:

                        # Have to close the ports and set the new ports
                        # Close UDP and bind to new port
                        socketUDP.close()
                        client_port_UDP = int(msg.split(' ')[4])

                        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        socketUDP.bind((client_host, client_port_UDP))

                    #     *** Changing TCP port causes address issue (address already in use) ***
                    # if int(msg.split(' ')[5]) != client_port_TCP:
                    #     # Close TCP and bind to new port
                    #     socketTCP.close()
                    #     client_port_TCP = int(msg.split(' ')[5])
                    #
                    #     # Create new socket with new TCP port
                    #     socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                    print(f"Server Reply: {serverMsg} \n")

                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Server Reply: {serverMsg} \n")

        elif msg.split(' ')[0] == 'PUBLISH':
            all_files = msg.split(' ')[3:]
            
            # Before sending all we should check to see if a connection is available
            try:
                filesToSend = pf.serializeFiles(msg, all_files)
                if not filesToSend:
                    print(f"PUBLISH-DENIED {msg.split(' ')[1]} File(s) does not exist")
                    continue

                # If closed is in the string in socketTCP, then we need to create a new one before sending files
                if "closed" in str(socketTCP):
                    socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                socketTCP.sendall(filesToSend)
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

        elif msg.split(' ')[0] == 'DOWNLOAD' and len(msg.split(' ')) == 3:
            chunkNumber = 1
            allContent = b""
            isDownloadError = False

            try:
                # # If closed is in the string in socketTCP, then we need to create a new one before sending files
                if "closed" in str(socketTCP):
                    socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                # Send DOWNLOAD request using TCP not UDP
                socketTCP.send(pickle.dumps([msg]))

                while True:
                    content = socketTCP.recv(200)

                    if not content:
                        # If content is empty then connection to server has ended. At this moment, the server may have
                        # terminated and then restored, so we have to create a new TCP socket

                        # Close TCP and bind to new port
                        socketTCP.close()

                        # Create new socket with new TCP port
                        socketTCP = initiateTCPSocket(client_host, client_port_TCP)

                        socketTCP.send(pickle.dumps([msg]))
                        continue
                    else:
                        try:
                            if content.decode().split(' ')[0] == "DOWNLOAD-ERROR":
                                print(f"Server reply: {content.decode()}")
                                isDownloadError = True
                                break
                        except UnicodeDecodeError as e:
                            # If this is the error, then the data passed from server has been dumped by pickle
                            pass

                        allContent += content
                        if len(content) < 200:
                            print(f"FILE-END {msg.split(' ')[1]} {msg.split(' ')[2]} CHUNK#{str(chunkNumber)}")
                            break
                        else:
                            print(f"FILE {msg.split(' ')[1]} {msg.split(' ')[2]} CHUNK#{str(chunkNumber)}")
                            chunkNumber += 1

                if not isDownloadError:
                    parsedMsg = msg.split(' ')
                    filename = parsedMsg[2].split('/')[1]
                    f = open(filename, 'w')

                    unserializedContent = pickle.loads(allContent)

                    for word in unserializedContent:
                        f.write(word)

                    f.close()
            except Exception as e:
                print(f"Error {e}... Server may be down. Wait a few seconds and then try again...")

        else:
            sendDataToServer(socketUDP, msg)


if __name__ == '__main__':
    startConnection()
