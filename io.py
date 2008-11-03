# Reads the entire contents of a file, given its path
def readFile(path):
    f = open(path)
    text = f.read()
    f.close()
    return text.decode('utf-8')