import socket
import sys

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost',10010))
server_address=('localhost',10000)

print(sys.stderr, 'connecting up on %s port %s' % server_address)
sock.connect(server_address)

try:
    message='test message'
    print(sys.stderr,'sending"%s"' % message)
    sock.sendall(message)
    amount_recieved=0
    amount_expected=len(message)
    while amount_recieved<amount_expected:
        data=sock.recv(16)
        amount_recieved+=len(data)
        print(sys.stderr,'recieved "%s"' % data)
finally:
    print(sys.stderr,'closing socket')
    socket.close()