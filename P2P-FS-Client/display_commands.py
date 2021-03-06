# ************************************************************
# displayCommands:
#   Description: Function which displays all the possible commands. (Displayed when user input 'menu' in console)
#   Parameters: NONE
# ************************************************************


def displayCommands():
    print('To Register/De-Register a User:')
    print('\tREGISTER RQ# Name IP-Address UDP_Socket# TCP_Socket#')
    print('\tDE-REGISTER RQ# Name\n')
    print('To Publish/Remove a File:')
    print('\t PUBLISH RQ# Name List_of_files')
    print('\t REMOVE RQ# Name List_of_files\n')
    print('Retrieve Information from the Server:')
    print('\t RETRIEVE-ALL RQ#')
    print('\t RETRIEVE-INFOT RQ# Name\n')
    print('Search for Specific Files:')
    print('\t SEARCH-FILE RQ# File-name\n')
    print('Downloading a File:')
    print('\t DOWNLOAD RQ# username-to-download-from/filename.txt\n')
    print('Update Contact Information:')
    print('\t UPDATE-CONTACT RQ# Name NEW-IP NEW-UDP_PORT\n')

