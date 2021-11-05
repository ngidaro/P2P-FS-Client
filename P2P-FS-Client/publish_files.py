import pickle


def SerializeFile(file):

    myfile=open(file,'r')
    content=myfile.readlines()
    return pickle.dumps(content)
