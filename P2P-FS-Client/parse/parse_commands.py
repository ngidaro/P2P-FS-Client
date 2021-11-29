REGISTER = 'REGISTER'
DEREGISTER = 'DE_REGISTER'
PUBLISH = 'PUBLISH'
REMOVE = 'REMOVE'
RETRIEVEALL = 'RETRIEVE-ALL'
RETRIEVEINFOT = 'RETRIEVE-INFOT'
SEARCHFILE = 'SEARCH-FILE'
DOWNLOAD = 'DOWNLOAD'
UPDATECONTACT = 'UPDATE-CONTACT'


# ************************************************************
# validateUserCommand:
#   Description: Function which checks to see if the command inputted by the user is valid. Also checks to see if
#         the user is registered before sending any data to the server
#   Parameters:
#       msg: Is the command entered by the user in the console
# ************************************************************


def validateUserCommand(msg):
    commands = [REGISTER, DEREGISTER, PUBLISH, REMOVE, RETRIEVEALL, RETRIEVEINFOT, SEARCHFILE, DOWNLOAD, UPDATECONTACT]
    IP_address = ''
    port_UDP = ''
    port_TCP = ''
    name = ''

    parsed_msg = msg.split(' ')

    # Check to make sure a command was given
    if parsed_msg[0] in commands:
        # If new user is being registered, we need to save the client address and port numbers
        if parsed_msg[0] == REGISTER:
            if len(parsed_msg) == 6:
                name = parsed_msg[2]
                IP_address = parsed_msg[3]
                port_UDP = int(parsed_msg[4]) or 0
                port_TCP = int(parsed_msg[5]) or 0
            else:
                print("Invalid Command")
        else:
            print('Need to REGISTER first')
    else:
        print("Invalid Command")

    return IP_address, port_UDP, port_TCP, name

