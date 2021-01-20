from async_socket import Socket
import socket

PACKET_SIZE = 1024


class Server(Socket):
    def __init__(self, count):
        super(Server, self).__init__()
        self.max_players_count = count
        self.players = []
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 256

    def set_up(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_players_count)
        print(f'Listening for {self.max_players_count} players...')
        self.socket.setblocking(False)
        print('-' * 20, f"{self.ip}:{self.port}", '-' * 20, sep='\n')

    async def send_data(self, data=None):
        for player in self.players:
            await self.main_loop.sock_sendall(player, data)

    async def listen_socket(self, listen_socket=None):
        if not listen_socket:
            return

        while True:
            try:
                data = await self.main_loop.sock_recv(listen_socket, PACKET_SIZE)
                await self.send_data(data)

            except ConnectionResetError:
                print('Client removed')
                self.players.remove(listen_socket)
                return

    async def accept_players(self):
        print('Begin accepting players')
        while len(self.players) < self.max_players_count:
            player_socket, address = await self.main_loop.sock_accept(self.socket)
            print(f'Player <{address[0]}> connected')
            self.players.append(player_socket)
            self.main_loop.create_task(self.listen_socket(player_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_players())


if __name__ == '__main__':
    server = Server(2)
    server.set_up()
    server.start()
