import pygame
import sys
import protocol
import socket
import threading
import time

WIDTH, HEIGHT = 1280, 720
_window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Client')


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
    def move(self, *args):
        self.x, self.y = args[:2]
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


class Enemy(Model):
    def move(self, *args):
        self.x, self.y = args[:2]
        super(Enemy, self).move()


def redraw_window(*objects):
    _window.fill((255, 255, 255))
    for element in objects:
        element.draw(_window)
    pygame.display.update()


data = None
send = None
ID = int(input('Your id'))


def get_data(server, player, enemy):
    data = list(server.recv(protocol.PACKET_SIZE))
    print('data', data)
    who = int.from_bytes(data[:1], byteorder='big', signed=True)
    print('who', who)
    coors = [int.from_bytes(data[i:i + 2], byteorder='big', signed=True) for i in range(1, len(data), 2)]
    print('GET', coors)
    if who == ID:
        player.move(*coors)
    else:
        enemy.move(*coors)


def send_coors(s, player):
    who = ID.to_bytes(byteorder='big', signed=True, length=1)
    x = player.x.to_bytes(byteorder='big', signed=True, length=2)
    y = player.y.to_bytes(byteorder='big', signed=True, length=2)
    s.sendall(who + x + y)


def main():
    s = socket.socket()
    s.connect(
        ('127.0.1.1', 255)
    )
    player = Player(*map(int, input('Player   >>>   ').split()), 75, 75, (0, 255, 0))
    enemy = Enemy(*map(int, input('Enemy   >>>   ').split()), 75, 75, (255, 0, 0))
    clock = pygame.time.Clock()
    # threading.Thread(target=send_coors, args=(s, player)).start()
    # threading.Thread(target=get_data, args=(s, player, enemy)).start()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        get_data(s, player, enemy)
        send_coors(s, player)
        player.move(player.x, player.y)
        redraw_window(player, enemy)
        clock.tick(60)


main()
