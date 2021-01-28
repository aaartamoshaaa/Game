from math import atan
from socket import socket, timeout
from protocol import PACKET_SIZE, from_data, from_bytes, PacketType
import pygame

FPS = 144
SPEED = int(600 / FPS)


class SpaceShip:
    def __init__(self, id, position, angle, abilities, health, color, image_file):
        """
        id is needed for identify players
        Position is coordinates of the spaceship on board
        angle of movement and look-angle
        abilities is a list of perks for this spaceship
        health is health
        color is color of spaceship
        image what will be used for drawing spaceship on screen
        """
        self.id = id
        self.x, self.y = position
        self.angle = angle
        self.abilities = abilities
        self.health = health
        self.color = color
        self.icon = image_file

    def render(self, screen):
        # todo Redraw spaceship image here
        pygame.draw.rect(screen, self.color, (self.x, self.y, 100, 100))

    def get_position(self):
        return self.x, self.y

    def get_angle(self):
        return self.angle

    def set_position(self, x, y):
        self.x, self.y = x, y

    def set_angle(self, angle):
        self.angle = angle
        self.angle %= 360


class Observer:
    def __init__(self, address, screen):
        self.screen = screen
        self.server = socket()
        self.server.connect(address)
        self.server.settimeout(0.2)

        rival_id, rival_x, rival_y, rival_angle, packet_type = from_bytes(self.server.recv(PACKET_SIZE))
        enemy_id, enemy_x, enemy_y, enemy_angle, packet_type = from_bytes(self.server.recv(PACKET_SIZE))
        print(rival_id, rival_x, rival_y, rival_angle)
        print(enemy_id, enemy_x, enemy_y, enemy_angle)
        self.rival = SpaceShip(rival_id, (rival_x, rival_y), rival_angle, [], 100, '#00ff00', '')
        self.enemy = SpaceShip(enemy_id, (enemy_x, enemy_y), enemy_angle, [], 100, '#ff0000', '')

    def move_rival(self):
        keys = pygame.key.get_pressed()
        x, y = self.rival.get_position()
        old_x, old_y = x, y
        if keys[pygame.K_w]:
            y -= SPEED
        if keys[pygame.K_s]:
            y += SPEED
        if keys[pygame.K_a]:
            x -= SPEED
        if keys[pygame.K_d]:
            x += SPEED
        if old_x != x or old_y != y:
            bytes_data = from_data(self.rival.id, x, y, self.rival.angle, PacketType.MOVEMENT)
            self.server.send(bytes_data)

    def update(self):
        self.move_rival()
        try:
            some_id, some_x, some_y, some_angle, packet_type = from_bytes(self.server.recv(10*PACKET_SIZE)[:PACKET_SIZE])
        except timeout:
            return
        else:
            if some_id == self.rival.id:
                self.rival.set_position(some_x, some_y)
                self.rival.set_angle(some_angle)
            else:
                self.enemy.set_position(some_x, some_y)
                self.enemy.set_angle(some_angle)
        finally:
            self.rival.render(self.screen)
            self.enemy.render(self.screen)
