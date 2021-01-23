import pygame
import sys
import protocol
import socket

WIDTH, HEIGHT = 1280, 720
_window = None
my_id = 0
s = None


class Model:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = (x, y, width, height)
        self.speed = 5

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rectangle)

    def move(self, *args):
        self.rectangle = (self.x, self.y, self.width, self.height)


class Player(Model):
    def move(self):
        global my_id
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
        super(Player, self).move()
        send_coors(s, my_id, self.x, self.y)


class Enemy(Model):
    def move(self):
        super(Enemy, self).move()


def redraw_window(*objects):
    global s, my_id
    get_data(s, my_id, objects[0], objects[1])
    _window.fill((255, 255, 255))
    for element in objects:
        element.draw(_window)
    pygame.display.update()


def get_data(server, ID, player, enemy):
    _id, x, y, angle, _type = protocol.from_bytes(server.recv(protocol.PACKET_SIZE))
    if _id == ID:
        player.x, player.y, = x, y
    else:
        enemy.x, enemy.y, = x, y


def send_coors(s, _id, x, y):
    s.send(protocol.from_data(_id, x, y, 0, 0))


def main():
    global _window, my_id, s
    _window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Client')
    s = socket.socket()
    s.connect(('92.242.40.206', 255))
    _id, x, y, angle, _type = protocol.from_bytes(s.recv(protocol.PACKET_SIZE))
    my_id = _id
    ide, xe, ye, ae, te = protocol.from_bytes(s.recv(protocol.PACKET_SIZE))
    player = Player(x, y, 30, 30, (0, 255, 0))
    enemy = Enemy(xe, ye, 30, 30, (255, 0, 0))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        player.move()
        redraw_window(player, enemy)
        clock.tick(60)


main()
