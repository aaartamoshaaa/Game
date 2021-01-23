from multiprocessing import Process
from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname, error as socket_error
from sys import exit
from time import sleep

from protocol import from_data, from_bytes, PACKET_SIZE
import logging

# SPAWN = (x, y, angle)
LEFT_SPAWN = (100, 300, 0)
RIGHT_SPAWN = (500, 300, 180)
SPAWN = (LEFT_SPAWN, RIGHT_SPAWN)
MOVEMENT = 0
SHOOT = 1


class Server:
    def __init__(self):
        # Network settings
        self.__ip = gethostbyname(gethostname())
        self.__port = 255
        self.__address = (self.__ip, self.__port)
        # Create socket object
        self.__socket = socket(AF_INET, SOCK_STREAM)
        # Other settings
        self.__count = 2  # maximum number of users
        self.__users = []  # list of sockets and addresses of users
        self.__all_users_connected = False  # flag, if everyone is connected
        self.__processes = []  # list of threads to safely KILL THEM ALL

    def stop(self):
        try:
            logs.info('Begin killing processes')
            logs.info(f'Total of {len(self.__processes)} processes')
            while self.__processes:
                self.__processes[0].kill()
                self.__processes.pop(0)
            else:
                logs.info('All processes are killed')
        except Exception as error:
            logs.error(error)
        logs.info('Server stopped')
        exit(0)

    def start(self):
        logs.info('Server starting')
        logs.info('Setup server')
        self.setup()
        logs.info('Setup complete')
        logs.info('Starting accepting users')
        self.accept_users()

    def setup(self):
        try:
            self.__socket.bind(self.__address)
        except socket_error as error:
            logs.error(error)
            self.__socket.close()
            self.stop()
        else:
            logs.info(f'Server bound to {self.__address}')
            print(self.__address)

    def accept_users(self):
        self.__socket.listen(self.__count)
        logs.info('Server started')
        logs.info(f'Waiting for {self.__count} users')
        while not self.__all_users_connected:
            new_user, address = self.__socket.accept()
            self.__users.append((new_user, address))
            logs.info(f'User {address} connected. [{len(self.__users)}/{self.__count}]')
            user_id = len(self.__users) - 1
            x, y, angle = SPAWN[user_id]
            packet_type = MOVEMENT
            data = from_data(user_id, x, y, angle, packet_type)
            new_user.sendall(data)
            logs.info(f'Send  to {address} [id={user_id}, x={x} y={y} angle={angle} type={packet_type}]')

            # todo FUCK ME
            # костыль начинается тут
            enemy_id = abs(1 - user_id)
            x, y, angle = SPAWN[enemy_id]
            data = from_data(enemy_id, x, y, angle, packet_type)
            new_user.sendall(data)
            logs.info(f'Send  to {address} [id={enemy_id}, x={x} y={y} angle={angle} type={packet_type}]')
            # костыль заканчивается тут
            # todo FUCK ME

            self.__all_users_connected = len(self.__users) == self.__count
        logs.info('All users are connected')
        self.__run()

    def __run(self):
        logs.info('Begin main job')
        for user, address in self.__users:
            process = Process(target=self.__listening__process, args=(user, address))
            self.__processes.append(process)
            logs.info(f'Create process for {address}')
            process.start()

    def __sendall(self, data):
        for user, address in self.__users:
            user.sendall(data)
            logs.info(f'Send to {address} data: {from_bytes(data)}')

    def __listening__process(self, user_socket, user_address):
        while self.__all_users_connected:
            try:
                data = user_socket.recv(PACKET_SIZE)
                self.__sendall(data)
                logs.info(f'Get from {user_address}: {from_bytes(data)}')
            except socket_error as error:
                logs.error(error)
                self.__users.remove((user_socket, user_address))
                logs.info(f'Disconnect from {user_address}')
                self.__all_users_connected = False
                exit(-1)


if __name__ == '__main__':
    logging.basicConfig(level='INFO', filename='server.log', filemode='w')
    logs = logging.getLogger(__name__)
    s = Server()
    s.start()
    # s.stop()
