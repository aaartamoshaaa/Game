import socket
import time
import threading
import sys

PACKET_SIZE = 48


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
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
            sys.exit(0)

    def setup(self):
        try:
            self._socket.bind(self._address)
        except socket.error as error_message:
            print(f"[ERROR] {error_message}")
            self._socket.close()
            print('[INFO] Server stopped')
            sys.exit(1)
        else:
            print(f'[INFO] Server binded to {self._address}')

    def accept_users(self):
        self._socket.listen(self._count)
        ('[INFO] Server started')
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
                new_thread = StoppableThread(
                    target=self.warning_thread,
                    args=(new_user, address)
                )
                self.__threads.append(new_thread)
                new_thread.start()
        else:
            # all users are connected
            for user, address in self._users:
                new_thread = StoppableThread(
                    target=self.listening_thread,
                    args=(user, address)
                )
                self.__threads.append(new_thread)
                new_thread.start()
                # todo sending thread

    def warning_thread(self, waiting_user, user_address):
        while not self.__all_users_connected__:
            try:
                waiting_user.send('Wait for others please'.encode())
                time.sleep(0.5)
            except socket.error as error_message:
                print(f'[ERROR] {error_message}')
                waiting_user.close()
                print(f'[INFO] Disconnecting user <{user_address}>')
                self._users.remove((waiting_user, user_address))
                break

    def listening_thread(self, user_socket, user_address):
        while self.__all_users_connected__:
            try:
                data = user_socket.recv(PACKET_SIZE).decode()
                if not data:
                    print(f'[INFO] User <{user_address}> disconnected')
                    self.__all_users_connected__ = False
                    self._users.remove((user_socket, user_address))
                    break
            except socket.error as error_message:
                print(f'[ERROR] {error_message}')
                self._socket.close()
                break


s = Server()
s.start()
s.stop()
