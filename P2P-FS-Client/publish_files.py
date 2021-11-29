import pickle
from pathlib import Path

# ************************************************************
# serializeFiles:
#   Description: Function which serializes the files to be sent over TCP to the server
#   Parameters:
#       inputString: Is the command entered by the user in the console
#       files: Is an array of the file names entered by the user in the console
# ************************************************************


def serializeFiles(inputString, files):
    allFileContent = []
    for f in files:
        if Path(f).exists():
            fil = open(f, 'r')
            content = fil.readlines()
            content.insert(0, "01111110")
            content.append("01111110")
            allFileContent += content

    return pickle.dumps([inputString, allFileContent])
    # return pickle.dumps(allFileContent)
    # ----------------
    # allfilecontent=[]
    #
    # for f in files:
    #     fil=open(f, 'r')
    #     content = fil.readlines()
    #     content.insert(0,"01111110")
    #     content.append("01111110")
    #     allfilecontent += content
    #     print(pickle.dumps(content))
    # #if file doesnt exist
    #
    # return pickle.dumps(allfilecontent)

def Serializesingle(file):
    f=open(file,'r')
    content=f.readlines()
    return pickle.dumps(content)
    return pickle.dumps(content)
