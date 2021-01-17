from async_socket import Socket
import asyncio
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
        print('Run setup...')
        print(f'Binding on {self.ip}:{self.port}...')
        self.socket.bind((self.ip, self.port))
        print('Binding done')
        self.socket.listen(self.max_players_count)
        print(f'Listening for {self.max_players_count} players...')
        self.socket.setblocking(False)
        print('Set blocking to False')

    async def listen_socket(self, socket):
        if not socket:
            return

        while True:
            data = self.main_loop.sock_recv(socket, PACKET_SIZE)
            await self.send_data(data)

    async  def accept_players(self):
        while len(self.players) < self.max_players_count:
            player_socket, address = await self.main_loop.sock_accept(self.socket)
            print(f'User <{address[0]}> connected')
            self.players.append(player_socket)
            self.main_loop.create_task(self.listen_socket(player_socket))


    async def send_data(self, data):
        for player in self.players:
            await self.main_loop.sock_sendall(data)

    async def main(self):
        await self.main_loop.create_task(self.accept_players())

if __name__ == '__main__':
    server = Server(2)
    server.set_up()
    server.start()
