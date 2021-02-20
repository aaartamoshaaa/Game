from protocol import from_bytes, PACKET_SIZE, from_data, PacketType
from socket import socket, timeout, error as socket_error
from math import atan2, degrees, radians, cos, sin
from pygame.locals import *
import pygame

FPS = 144
SPACESHIPS_SPEED = 4


class DynamicSprite(pygame.sprite.Sprite):
    def __init__(
            self, object_id, position, angle, image
    ):
        super(DynamicSprite, self).__init__()
        self._id = object_id

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 75))
        self._original_image = self.image

        self._position = pygame.math.Vector2(position)
        self._angle = angle
        self.rect = self.image.get_rect(center=self._position)
        self.packet_type = PacketType.DEFAULT

    # ---------------------------

    def set_angle(self, angle):
        self._angle = angle % 360
        self.image = pygame.transform.rotate(
            self._original_image, -self._angle
        )
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_angle(self):
        return self._angle

    # ---------------------------

    def set_position(self, vector):
        self._position = pygame.math.Vector2(vector)
        self.rect.center = self._position

    def get_position(self):
        return self._position

    def move(self, vector):
        self.set_position(
            self.get_position() + pygame.math.Vector2(vector)
        )

    # ---------------------------

    def get_id(self):
        return self._id

    # ---------------------------

    @property
    def information(self):
        i = self.get_id()
        x, y = self.get_position()
        a = self.get_angle()
        return i, int(x), int(y), int(a)


class AllySpaceShip(DynamicSprite):
    def __init__(self, object_id, position, angle):
        super(AllySpaceShip, self).__init__(
            object_id, position, angle, './Textures/Ally.png'
        )
        self.perks_ready = []
        self.render_objects = pygame.sprite.Group()
        # ---------------------------

        self.perks_ready.append(Perquisite)

        # ---------------------------
        self.speed = SPACESHIPS_SPEED

    def update(self):
        # ---------------------------

        mouse_x, mouse_y = pygame.mouse.get_pos()
        this_x, this_y = self.get_position()

        delta_x = mouse_x - this_x
        delta_y = mouse_y - this_y

        angle = degrees(atan2(delta_y, delta_x)) + 90
        self.set_angle(angle)

        # ---------------------------

        keys = pygame.key.get_pressed()
        if keys[K_w]:
            self.move((0, -self.speed))
        if keys[K_s]:
            self.move((0, self.speed))
        if keys[K_a]:
            self.move((-self.speed, 0))
        if keys[K_d]:
            self.move((self.speed, 0))
        if keys[K_q]:
            if Perquisite in self.perks_ready:
                x, y = pygame.mouse.get_pos()
                self.render_objects.add(
                    Perquisite(self, (x, y))
                )

        # ---------------------------

        self.render_objects.update()


class EnemySpaceShip(DynamicSprite):
    def __init__(self, object_id, position, angle):
        super(EnemySpaceShip, self).__init__(
            object_id, position, angle, './Textures/Enemy.png'
        )
        self.speed = SPACESHIPS_SPEED
        self.perks_ready = []

        self.perks_ready.append(Perquisite)

        self.render_objects = pygame.sprite.Group()

    def update(self):
        self.render_objects.update()


class Observer:
    def __init__(self, screen):
        self.screen = screen
        self.server = socket()
        self.long_timeout = 2
        self.timeout = 0.01
        self.max_packets = 2
        self.group = pygame.sprite.Group()

    def connect(self, address):
        self.server.settimeout(self.long_timeout)
        try:
            self.server.connect(address)
            self.register()
        except timeout:
            raise Exception('Server is offline')

        self.server.settimeout(self.timeout)

    def register(self):
        a_id, a_x, a_y, a_a, packet = from_bytes(
            self.server.recv(PACKET_SIZE)
        )
        self.ally = AllySpaceShip(a_id, (a_x, a_y), a_a)
        self.group.add(self.ally)

        e_id, e_x, e_y, e_a, packet = from_bytes(
            self.server.recv(PACKET_SIZE)
        )
        self.enemy = EnemySpaceShip(e_id, (e_x, e_y), e_a)
        self.group.add(self.enemy)

    def send(self, spaceship, packet_type):
        byte_data = from_data(
            *spaceship.information, packet_type
        )
        self.server.send(byte_data)

        for perquisite in spaceship.render_objects:
            to_send = perquisite.information
            if to_send:
                self.server.send(from_data(
                    *to_send, perquisite.packet_type
                ))

    def receive(self):
        try:
            data = self.server.recv(self.max_packets * PACKET_SIZE)
        except timeout:  # if no data from server
            return
        else:
            for i in range(0, len(data), PACKET_SIZE):
                s_id, s_x, s_y, s_a, pack_type = from_bytes(
                    data[i:i + PACKET_SIZE]
                )
                yield s_id, s_x, s_y, s_a, pack_type

    def kill(self):
        try:
            self.server.recv(1024)  # read all left data from server
        except timeout:
            pass
        self.server.close()  # close connection

    def update(self):
        try:
            self.send(self.ally, PacketType.MOVEMENT)
        except socket_error:
            self.server.close()
            raise socket_error

        for s_id, s_x, s_y, s_a, pack_type in self.receive():
            if pack_type == PacketType.MOVEMENT:
                self.enemy.set_position((s_x, s_y))
                self.enemy.set_angle(s_a)
            if pack_type == PacketType.DEFAULT:
                self.enemy.render_objects.add(
                    Perquisite(self.enemy, (s_x, s_y))
                )

        # call AllySpaceShip.update() and EnemySpaceShip.update()
        self.group.update()
        self.group.draw(self.screen)  # draw objects

        for spaceship in self.group:
            spaceship.render_objects.draw(self.screen)


class Perquisite(DynamicSprite):
    def __init__(
            self,
            summoner, aim_point,
            speed=SPACESHIPS_SPEED,
            damage=10,
            cool_down_time=0,
            count_down_time=600,
            packet_type=PacketType.DEFAULT
    ):
        aim_x, aim_y = aim_point
        this_x, this_y = summoner.get_position()

        delta_x = aim_x - this_x
        delta_y = aim_y - this_y

        angle = degrees(atan2(delta_y, delta_x))

        super(Perquisite, self).__init__(
            summoner.get_id(), summoner.get_position(),
            angle, './Textures/bullet.png'
        )
        self.summoner = summoner
        self.damage = damage
        self.speed = speed
        self.aim = aim_point
        self.count_time = count_down_time
        self.cool_down_time = cool_down_time
        self.lifetime = 0
        self.packet_type = packet_type
        self.updated = False
        self.set_angle(self.get_angle())  # for rotating image
        self.last_used_time = cool_down_time
        self.summoner.perks_ready.remove(Perquisite)

    def update(self):
        self.lifetime += 1000/FPS
        self.move((
            self.speed*cos(radians(self.get_angle())),
            self.speed*sin(radians(self.get_angle()))
        ))

        # if self.lifetime - self.last_used_time > self.cool_down_time:
        #     self.last_used_time = self.lifetime
        #     self.summoner.perks_ready.append(Perquisite)

        if self.lifetime >= self.count_time:
            self.summoner.perks_ready.append(Perquisite)
            self.kill()

    @property
    def information(self):
        if not self.updated:
            self.updated = True
            i = self.get_id()
            x, y = self.aim
            a = self.get_angle()
            return i, int(x), int(y), int(a)
        return False


if __name__ == '__main__':
    pygame.init()
    fps_clock = pygame.time.Clock()
    from interface import Window, Theme

    display = pygame.display.set_mode(Window.size)
    observer = Observer(display)

    observer.connect(('92.242.40.206', 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

        display.fill(Theme.Colors.main)

        observer.update()

        pygame.display.update()
        fps_clock.tick(FPS)
