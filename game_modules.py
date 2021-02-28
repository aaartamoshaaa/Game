from socket import socket, timeout, error as SocketError
import pygame
from protocol import PACKET_SIZE, from_bytes, from_data, PacketType
from math import pi as PI, atan2

FPS = 144
SPEED = 4


class SpaceShip(pygame.sprite.Sprite):
    def __init__(
        self, player_id,
        start_position, angle, image_file
    ):
        # Creating sprite
        pygame.sprite.Sprite.__init__(self)
        # initializing
        self.id = player_id
        self.x, self.y = start_position
        self.angle = angle
        self.image_file = image_file
        # image loading
        self.origin_image = pygame.image.load(image_file)
        self.image = self.origin_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

    # # ANGLE
    def get_angle(self):
        return self.angle

    def set_angle(self, angle):
        self.angle = int(angle % 360)

    # # POSITION
    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    # # ID

    def set_id(self, player_id):
        self.id = player_id

    def get_id(self):
        return self.id

    def update(self):
        raise NotImplementedError


class AllySpaceShip(SpaceShip):
    def __init__(self, player_id, start_position, angle):
        super().__init__(
            player_id=player_id,
            start_position=start_position,
            angle=angle,
            image_file='./Textures/rival.png'
        )

    def update(self):
        """# ! this method is called by Group.update()
        Used to pre-render image (angle rotation)
        """
        self.__calculate_position()
        self.__calculate_angle()
        self.image = pygame.transform.rotate(self.origin_image, self.angle)

    def __calculate_angle(self):
        """Calculates the angle of deviation from the mouse coordinates
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
        angle = (180 / PI) * -atan2(rel_y, rel_x) - 90
        self.set_angle(angle)

    def __calculate_position(self):
        """Calculate the position of the spaceship. Change self.x and self.y
        """
        pygame.event.pump()  # pygame handlers
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # key W
            self.y -= SPEED
        if keys[pygame.K_s]:  # key S
            self.y += SPEED
        if keys[pygame.K_a]:  # key A
            self.x -= SPEED
        if keys[pygame.K_d]:  # key D
            self.x += SPEED
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y


class EnemySpaceShip(SpaceShip):
    def __init__(self, player_id, start_position, angle):
        super().__init__(
            player_id=player_id,
            start_position=start_position,
            angle=angle,
            image_file='./Textures/enemy.png'
        )

    def update(self):
        # ! this method is called by Group.update()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.image = pygame.transform.rotate(self.origin_image, self.angle)


class Observer:
    def __init__(self, screen):
        self.screen = screen
        self.server = socket()
        self.long_timeout = 2
        self.timeout = 0.2
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
        a_id, a_x, a_y, a_a, packet = from_bytes(self.server.recv(PACKET_SIZE))
        self.ally = AllySpaceShip(a_id, (a_x, a_y), a_a)
        self.group.add(self.ally)

        e_id, e_x, e_y, e_a, packet = from_bytes(self.server.recv(PACKET_SIZE))
        self.enemy = EnemySpaceShip(e_id, (e_x, e_y), e_a)
        self.group.add(self.enemy)

    def send(self, player_id, x, y, angle, packet_type):
        byte_data = from_data(player_id, x, y, angle, packet_type)
        self.server.send(byte_data)

    def receive(self):
        try:
            data = self.server.recv(self.max_packets*PACKET_SIZE)
        except timeout:
            return
        else:
            for i in range(0, len(data), PACKET_SIZE):
                s_id, s_x, s_y, s_a, pack_type = from_bytes(
                    data[i:i+PACKET_SIZE]
                )
                yield s_id, s_x, s_y, s_a, pack_type

    def kill(self):
        try:
            self.server.recv(1024)
        except timeout:
            pass
        self.server.close()

    def update(self):
        ally_id = self.ally.get_id()
        ally_x, ally_y = self.ally.get_position()
        ally_a = self.ally.get_angle()

        try:
            self.send(ally_id, ally_x, ally_y, ally_a, PacketType.MOVEMENT)
        except SocketError:
            self.server.close()
            raise SocketError

        for s_id, s_x, s_y, s_a, pack_type in self.receive():
            if s_id == self.ally.get_id():
                if pack_type == PacketType.MOVEMENT:
                    pass
                    # * self.ally.set_position((s_x, s_y))
                    # * self.ally.set_angle(s_a)
                else:
                    pass  # todo Perk usage
            elif s_id == self.enemy.get_id():
                if pack_type == PacketType.MOVEMENT:
                    self.enemy.set_position((s_x, s_y))
                    self.enemy.set_angle(s_a)
                else:
                    pass  # todo Perk usage

        self.group.update()
        self.group.draw(self.screen)
