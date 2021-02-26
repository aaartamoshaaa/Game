from protocol import from_bytes, PACKET_SIZE, from_data, PacketType
from socket import socket, timeout, error as socket_error
from math import atan2, degrees, radians, cos, sin
from pygame.locals import *
from global_variables import *
import pygame

FPS = 144
ALL_SPRITES = pygame.sprite.Group()


class DynamicSprite(pygame.sprite.Sprite):
    def __init__(
            self, object_id, position, angle, image, size
    ):
        super(DynamicSprite, self).__init__()
        self.health = 1
        self._id = object_id

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
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

    def get_damage(self, harm):
        self.health -= harm
        if self.health <= 0:
            self.kill()

    @property
    def information(self):
        i = self.get_id()
        x, y = self.get_position()
        a = self.get_angle()
        return i, int(x), int(y), int(a)


class AllySpaceShip(DynamicSprite):
    def __init__(self, object_id, position, angle):
        super(AllySpaceShip, self).__init__(
            object_id, position, angle, './Textures/Ally.png', SPACESHIPS_SIZE
        )
        self.perks_ready = []
        self.perks_info = {}
        self.render_objects = pygame.sprite.Group()
        self.health = SPACESHIPS_HEALTH

        # ---------------------------

        self.perks_ready.append(Explosive)
        self.perks_info[Explosive] = 0

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
            if Explosive in self.perks_ready:
                x, y = pygame.mouse.get_pos()
                self.render_objects.add(
                    Explosive(self, (x, y))
                )
        # ---------------------------

        self.render_objects.update()


class EnemySpaceShip(DynamicSprite):
    def __init__(self, object_id, position, angle):
        super(EnemySpaceShip, self).__init__(
            object_id, position, angle, './Textures/Enemy.png', SPACESHIPS_SIZE
        )
        self.speed = SPACESHIPS_SPEED
        self.perks_ready = []
        self.perks_info = {}
        self.render_objects = pygame.sprite.Group()
        self.perks_ready.append(Explosive)
        self.perks_info[Explosive] = 0
        self.health = SPACESHIPS_HEALTH

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
        self.is_end = False
        self.is_game_active = False

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
        if spaceship in self.group:
            byte_data = from_data(
                *spaceship.information, packet_type
            )
        else:
            # sprite is killed
            byte_data = from_data(spaceship.get_id(), 0, 0, 0, PacketType.DEATH)

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
        except OSError:
            return
        else:
            for i in range(0, len(data), PACKET_SIZE):
                s_id, s_x, s_y, s_a, pack_type = from_bytes(
                    data[i:i + PACKET_SIZE]
                )
                yield s_id, s_x, s_y, s_a, pack_type

    def kill(self):
        self.server.close()

    def update(self):
        for s_id, s_x, s_y, s_a, pack_type in self.receive():
            if pack_type == PacketType.ALL_CONNECTED:
                self.server.send(
                    from_data(0, 0, 0, 0, PacketType.ALL_CONNECTED)
                )
                self.is_game_active = True
            if pack_type == PacketType.DEATH:
                self.server.send(
                    from_data(self.enemy.get_id(), 0, 0, 0, PacketType.DEATH)
                )
                self.is_end = True
                self.is_game_active = False
                for sprite in self.group:
                    sprite.kill()
                self.kill()
            if pack_type == PacketType.MOVEMENT:
                self.enemy.set_position((s_x, s_y))
                self.enemy.set_angle(s_a)
            if pack_type == PacketType.EXPLOSIVE:
                self.enemy.render_objects.add(
                    Explosive(self.enemy, (s_x, s_y))
                )

        if not self.is_game_active or self.is_end:
            return

        for spaceship in self.group:
            spaceship.render_objects.draw(self.screen)

        # call AllySpaceShip.update() and EnemySpaceShip.update()
        self.group.update()
        self.group.draw(self.screen)  # draw objects

        try:
            self.send(self.ally, PacketType.MOVEMENT)
        except socket_error:
            self.kill()

        # update ALL_SPRITES
        for obj in (
                *self.group,
                *self.ally.render_objects,
                *self.enemy.render_objects
        ):
            if obj not in ALL_SPRITES:
                ALL_SPRITES.add(obj)


class AnimatedDynamicSprite(DynamicSprite):
    def __init__(self, object_id, position, angle, image, size, animation_file,
                 ticks_for_update, count_of_frames):
        super(AnimatedDynamicSprite, self).__init__(
            object_id, position, angle, image, size
        )
        self.ticks_for_update = ticks_for_update
        self.count_of_frames = count_of_frames
        self.last_tick_animate = 0
        self.frames = []
        sheet = pygame.image.load(animation_file)
        self.rect = pygame.Rect(
            0, 0,
            sheet.get_width() // self.count_of_frames, sheet.get_height()
        )
        for i in range(self.count_of_frames):
            frame_location = (self.rect.w * i, 0)
            self.frames.append(
                sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
            )
        self.current_frame_id = 0
        self.image = self.frames[self.current_frame_id]

        self.move_to_on_touch = pygame.math.Vector2(
            -self.rect.w // 2,
            -self.rect.h // 2
        )

    def play_animation(self):
        self.move(self.move_to_on_touch)
        self.move_to_on_touch = pygame.math.Vector2(0, 0)

        now = pygame.time.get_ticks()
        if self.last_tick_animate + self.ticks_for_update < now:
            self.last_tick_animate = now
            self.current_frame_id += 1
            is_end = self.current_frame_id >= len(self.frames)
            if is_end:
                self.kill()
                return True
            else:
                self.image = self.frames[self.current_frame_id]
        return False


class Perquisite(AnimatedDynamicSprite):
    def __init__(
            self,
            summoner, aim_point, animation_image, speed, damage, cool_down_time,
            count_down_time, packet_type, ticks_for_update, count_of_frames,
            bullet_image, bullet_size
    ):
        aim_x, aim_y = aim_point
        this_x, this_y = summoner.get_position()

        delta_x = aim_x - this_x
        delta_y = aim_y - this_y

        angle = degrees(atan2(delta_y, delta_x))

        super(Perquisite, self).__init__(
            object_id=summoner.get_id(), position=summoner.get_position(),
            angle=angle, image=bullet_image, size=bullet_size,
            animation_file=animation_image, ticks_for_update=ticks_for_update,
            count_of_frames=count_of_frames
        )
        # object
        self.summoner = summoner
        self.damage = damage
        self.speed = speed
        self.aim = aim_point
        # time
        self.count_time = count_down_time
        self.cool_down_time = cool_down_time
        self.spawn_time = pygame.time.get_ticks()
        # network
        self.packet_type = packet_type
        # flags
        self.can_mode = True
        self.updated = False
        self.touch_something = None
        # image
        self.set_angle(self.get_angle())  # for rotating image
        # protect
        if self.__class__ in self.summoner.perks_ready:
            self.summoner.perks_ready.remove(self.__class__)
            self.summoner.perks_info[self.__class__] = pygame.time.get_ticks()
        else:
            self.kill()

    def update(self):
        if self.touch_something:
            self.animate_and_damage(self.touch_something)

        for sprite in ALL_SPRITES:
            if sprite != self.summoner and \
                    not isinstance(sprite, self.__class__):
                if self.rect.colliderect(sprite.rect):
                    if not self.touch_something:
                        self.touch_something = sprite
                        sprite.get_damage(self.damage)
                    return

        if self.can_mode:
            self.move((
                self.speed * cos(radians(self.get_angle())),
                self.speed * sin(radians(self.get_angle()))
            ))

        now = pygame.time.get_ticks()
        if now - self.summoner.perks_info[self.__class__] > \
                self.cool_down_time:
            self.return_perk(now)

        if self.spawn_time + self.count_time < now:
            self.kill()

    def return_perk(self, last_time_used):
        if self.__class__ not in self.summoner.perks_ready:
            self.summoner.perks_ready.append(self.__class__)
            self.summoner.perks_info[self.__class__] = last_time_used

    def animate_and_damage(self, sprite):
        self.can_mode = False
        is_end = self.play_animation()
        if is_end:
            self.return_perk(pygame.time.get_ticks())

    @property
    def information(self):
        if not self.updated:
            self.updated = True
            i = self.get_id()
            x, y = self.aim
            a = self.get_angle()
            return i, int(x), int(y), int(a)


class Explosive(Perquisite):
    def __init__(self, summoner, aim_point):
        super(Explosive, self).__init__(
            summoner, aim_point,
            animation_image=EXPLOSIVE_ANIMATION_IMAGE,
            speed=EXPLOSIVE_BULLET_SPEED,
            damage=EXPLOSIVE_DAMAGE,
            cool_down_time=EXPLOSIVE_PERK_COOLDOWN,
            count_down_time=EXPLOSIVE_PERK_COUNTDOWN,
            packet_type=PacketType.EXPLOSIVE,
            count_of_frames=EXPLOSIVE_ANIMATION_COUNT_OF_FRAMES,
            ticks_for_update=EXPLOSIVE_ANIMATION_TICKS_PER_FRAME,
            bullet_image=EXPLOSIVE_BULLET_IMAGE,
            bullet_size=EXPLOSIVE_BULLET_SIZE
        )