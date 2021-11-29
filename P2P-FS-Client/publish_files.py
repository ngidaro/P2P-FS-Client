import pickle


def SerializeFiles(files):
    allfilecontent=[]

    for f in files:
        fil=open(f, 'r')
        content = fil.readlines()
        content.insert(0,"01111110")
        content.append("01111110")
        allfilecontent += content
        print(pickle.dumps(content))
    #if file doesnt exist

    return pickle.dumps(allfilecontent)

def Serializesingle(file):
    f=open(file,'r')
    content=f.readlines()
    return pickle.dumps(content)