from math import atan2, pi
from socket import socket, timeout
from protocol import PACKET_SIZE, from_data, from_bytes, PacketType
import pygame

FPS = 144
SPEED = int(600 / FPS)


class SpaceShip:
    def __init__(
        self, id, position, angle,
        abilities, health, color, image_file
    ):
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
        self.origin_image = pygame.image.load(image_file)
        self.icon = self.origin_image
        self.size = self.origin_image.get_size()
        self.side = self.size[0]

    def render(self, screen):
        # rotate image by angle (make spaceship look at cursor)
        self.icon = pygame.transform.rotate(self.origin_image, self.angle)
        # draw spaceship
        screen.blit(self.icon, (self.x, self.y))

    def get_position(self):
        return self.x, self.y

    def get_angle(self):
        return self.angle

    def set_position(self, x, y):
        self.x, self.y = x, y

    def set_angle(self, angle):
        self.angle = int(angle)


class Observer:
    def __init__(self, address, screen):
        self.screen = screen
        self.server = socket()
        self.server.connect(address)
        self.server.settimeout(0.5)

        rival_id, rival_x, rival_y, rival_angle, packet_type = from_bytes(
            self.server.recv(PACKET_SIZE))
        enemy_id, enemy_x, enemy_y, enemy_angle, packet_type = from_bytes(
            self.server.recv(PACKET_SIZE))
        self.rival = SpaceShip(
            rival_id,
            (rival_x, rival_y),
            rival_angle,
            [], 100,
            '#00ff00',
            'Textures/rival.png'
        )
        self.enemy = SpaceShip(
            enemy_id,
            (enemy_x, enemy_y),
            enemy_angle,
            [], 100,
            '#ff0000',
            'Textures/enemy.png'
        )

    def rotate_rival(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        old = self.rival.get_angle()
        rel_x, rel_y = mouse_x - self.rival.x, mouse_y - self.rival.y
        angle = (180 / pi) * - atan2(rel_y, rel_x) - 90
        self.rival.set_angle(angle)
        return int(angle)

    def move_rival(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        x, y = self.rival.get_position()

        if keys[pygame.K_w]:
            y -= SPEED
        if keys[pygame.K_s]:
            y += SPEED
        if keys[pygame.K_a]:
            x -= SPEED
        if keys[pygame.K_d]:
            x += SPEED
        return x, y

    def send(self, x, y, angle, packet_type):
        bytes_data = from_data(
            self.rival.id, x, y, angle, packet_type
        )
        self.server.send(bytes_data)

    def update(self):
        x, y = self.move_rival()
        angle = self.rotate_rival()
        self.send(x, y, angle, PacketType.MOVEMENT)
        try:
            some_id, some_x, some_y, some_angle, packet_type = from_bytes(
                self.server.recv(6*PACKET_SIZE)[:PACKET_SIZE])
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

    def kill(self):
        self.server.close()

















