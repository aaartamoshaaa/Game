from async_socket import Socket
import asyncio

PACKET_SIZE = 1024


class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()

    def set_up(self):
        address = input('Connect to (ip:port) >>>   ').split(':')
        address = (address[0], int(address[1]))
        try:
            self.socket.connect(address)
        except ConnectionRefusedError:
            print('Unable to connect')
            exit(0)

        self.socket.setblocking(False)

    async def listen_socket(self, listened_socket=None):
        while True:
            data = await self.main_loop.sock_recv(self.socket, PACKET_SIZE)
            print(data.decode('utf-8'))

    async def send_data(self, data=None):
        while True:
            data = await self.main_loop.run_in_executor(None, input)
            await self.main_loop.sock_sendall(self.socket, data.encode('utf-8'))

    async def main(self):
        await asyncio.gather(
            self.main_loop.create_task(self.listen_socket()),
            self.main_loop.create_task(self.send_data())
        )


if __name__ == '__main__':
    cl = Client()
    cl.set_up()
    cl.start()
