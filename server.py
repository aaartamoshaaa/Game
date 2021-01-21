import socket
import threading
import sys
import protocol


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Server:
    def __init__(self):
        # Network settings
        self._ip = socket.gethostbyname(socket.gethostname())
        self._port = 255
        self._address = (self._ip, self._port)
        # Create socket object
        self._socket = socket.socket()
        # Other settings
        self._count = 2  # maximum number of users
        self._users = []  # list of sockets and addresses of users
        self.__all_users_connected__ = False  # flag, if all connected
        self.__threads = []  # list of threads to safely KILL THEM ALL
        self.__send_data = None
        self.__get_data = None

    def start(self):
        print('[INFO] Server starting')
        print('[INFO] Set up some settings')
        self.setup()
        print('[INFO] Setup complete')
        print('[INFO] Starting accepting users')
        self.accept_users()

    def stop(self):
        while len(self.__threads):  # stop all threads
            self.__threads[0].stop()
            self.__threads.pop(0)
        else:
            print('[INFO] Server stopped')
            sys.exit(0)
            exit(0)

    def setup(self):
        try:
            self._socket.bind(self._address)
        except socket.error as error_message:
            print(f"[ERROR] {error_message}")
            self._socket.close()
            print('[INFO] Server stopped')
            sys.exit(1)
        else:
            print(f'[INFO] Server bound to {self._address}')

    def accept_users(self):
        self._socket.listen(self._count)
        print('[INFO] Server started')
        print(f'[INFO] Server waiting for {self._count} users')
        while not self.__all_users_connected__:
            new_user, address = self._socket.accept()
            self._users.append((new_user, address))  # save new user
            print(
                f'[INFO] User <{address}> connected. '
                f'Now its {len(self._users)}/{self._count}'
            )
            # check if all connected
            self.__all_users_connected__ = len(self._users) == self._count
            # new thread, which will be sending warning message
            if not self.__all_users_connected__:
                new_listening_thread = StoppableThread(
                    target=self.__warning_thread__,
                    args=(new_user, address)
                )
                self.__threads.append(new_listening_thread)
                new_listening_thread.start()
        else:
            print('[INFO] All users are connected')
            # all users are connected
            for user, address in self._users:
                new_listening_thread = StoppableThread(
                    target=self.__listening_thread__,
                    args=(user, address)
                )
                new_sending_thread = StoppableThread(
                    target=self.__sending_thread__,
                    args=(user, address)
                )
                self.__threads.append(new_sending_thread)
                self.__threads.append(new_listening_thread)
                new_listening_thread.start()
                new_sending_thread.start()

    def __warning_thread__(self, waiting_user, user_address):
        try:
            waiting_user.send('Wait for others please'.encode())
            while not self.__all_users_connected__:
                waiting_user.recv(protocol.PACKET_SIZE)
        except socket.error as error_message:
            print(f'[ERROR] {error_message}')
            waiting_user.close()
            print(f'[INFO] Disconnecting user <{user_address}>')
            self._users.remove((waiting_user, user_address))

    def __listening_thread__(self, user_socket, user_address):
        while self.__all_users_connected__:
            try:
                data = user_socket.recv(protocol.PACKET_SIZE)
                print(f'[FROM <{user_address}>] {self.data_processing(data)}')
                if not data:
                    print(f'[INFO] User <{user_address}> disconnected')
                    self.__all_users_connected__ = False
                    self._users.remove((user_socket, user_address))
                    break
                else:
                    self.__get_data = data
            except socket.error as error_message:
                print(f'[ERROR] {error_message}')
                print('[INFO] Closing server')
                self._socket.close()
                print('[INFO] Server stopped')
                break

    def __sending_thread__(self, user_socket, user_address):
        while self.__all_users_connected__:
            try:
                if self.__send_data:
                    user_socket.sendall(self.__send_data)
                    print(f'[INFO] Data sent to <{user_address}>')
                    self.__send_data = None
            except socket.error as error_message:
                print(f'[ERROR] {error_message}')
                print('[INFO] Closing server')
                self._socket.close()
                print('[INFO] Server stopped')
                break

    def send(self, data):
        self.__send_data = data

    def get(self):
        return self.__get_data

    def data_processing(self, data):
        return (data, type(data))


def listen(s):
    print('[INFO] Server listening to your commands')
    command = input()
    if command == 'close':
        print('[INFO] Stopping server')
        s.stop()


def start():
    s = Server()

    t = threading.Thread(
        target=listen,
        args=(s,)
    )
    t.start()

    s.start()
    s.send('Hi!'.encode())


if __name__ == "__main__":
    start()