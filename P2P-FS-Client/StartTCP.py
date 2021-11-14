import socket
import sys

def SendFileNames(file, sock):

    print(sys.stderr,'sending"%s"' % file)
    sock.sendall(file)
