import socket
from _thread import start_new_thread

_ip = socket.gethostbyname(socket.gethostname())
_port = 255
PACKET = 48
_count = 1
_users = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((_ip, _port))
    print(f'Server binded to {_ip}:{_port}')
except Exception as error:
    print(error)
    server_socket.close()

server_socket.listen(_count)
print(f'Server listening for {_count} users')


def threaded_client(client_socket, address):
    while True:
        try:
            data = client_socket.recv(PACKET).decode('utf-8')
            if not data:
                print(f'User <{address}> dissconnected')
                break
            client_socket.send(data.encode('utf-8'))
        except Exception as error:
            print(error)
            server_socket.close()
            break


while True:
    connection, address = server_socket.accept()
    print(f'User <{address}> connected')
    _users.append(connection)
    start_new_thread(threaded_client, (connection, address))


class Server():
    def __init__(self):
        self.__ip = socket.gethostbyname(socket.gethostname())
        self.__port = 255
        self.__users = []
        self.__count = 1
        self.__address = (self.__ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setup(self):
        pass
