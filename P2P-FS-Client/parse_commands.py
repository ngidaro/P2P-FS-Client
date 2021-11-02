REGISTER = 'REGISTER'
DEREGISTER = 'DE_REGISTER'
PUBLISH = 'PUBLISH'
REMOVE = 'REMOVE'
RETRIEVEALL = 'RETRIEVE-ALL'
RETRIEVEINFOT = 'RETRIEVE-INFOT'
SEARCHFILE = 'SEARCH-FILE'
DOWNLOAD = 'DOWNLOAD'
UPDATECONTACT = 'UPDATE-CONTACT'


def get_data(msg):
    commands = [REGISTER, DEREGISTER, PUBLISH, REMOVE, RETRIEVEALL, RETRIEVEINFOT, SEARCHFILE, DOWNLOAD, UPDATECONTACT]
    IP_address = ''
    port_UDP = ''
    port_TCP = ''

    parsed_msg = msg.split(' ')

    # Check to make sure a command was given
    if parsed_msg[0] in commands:
        # If new user is being registered, we need to save the client address and port numbers
        if parsed_msg[0] == REGISTER:
            if len(parsed_msg) == 6:
                IP_address = parsed_msg[3]
                port_UDP = int(parsed_msg[4]) or 0
                port_TCP = int(parsed_msg[5]) or 0
            else:
                print("Invalid Command")
        else:
            print('Need to REGISTER first')
    else:
        print("Invalid Command")

    return IP_address, port_UDP, port_TCP

