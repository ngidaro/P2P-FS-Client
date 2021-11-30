import pickle

# ************************************************************
# serializeFiles:
#   Description: Function which serializes the files to be sent over TCP to the server
#   Parameters:
#       inputString: Is the command entered by the user in the console
#       files: Is an array of the file names entered by the user in the console
# ************************************************************


def serializeFiles(inputString, files):
    allFileContent = []
    try:
        for f in files:
            file = open(f, 'r')
            content = file.readlines()
            content.insert(0, "01111110")
            content.append("01111110")
            allFileContent += content

        return pickle.dumps([inputString, allFileContent])
    except FileNotFoundError:
        return False
