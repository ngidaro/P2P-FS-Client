import pickle


def SerializeFiles(files):
    allfilecontent=[]
    try:
        for f in files:
            fil=open(f, 'r')
            content = fil.readlines()
            content.insert(0,"01111110")
            content.append("01111110")
            allfilecontent += content
        return pickle.dumps(allfilecontent)
    except FileNotFoundError:
        return "error"
