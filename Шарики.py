import pygame
import math
import sys


def exit(status=False):
    if status:
        print(status)
        input()
    sys.exit()


class PygameSurface(pygame.Surface):
    def __init__(self, size, mode=0, flipNow=True):
        super().__init__(size)
        self.size = size
        self.display = pygame.display.set_mode(self.size, mode)
        if flipNow:
            self.flip()

    def get_display(self):
        return self.display

    def flip(self):
        pygame.display.flip()

    def set_caption(self, caption):
        pygame.display.set_caption(caption)

    def fill(self, color):
        self.display.fill(color)


class Creature:
    def __init__(self, surface, position=None, visible=True, enable=True):
        self.surface = surface
        self.position = position
        self.visible = visible
        self.enable = enable

    def destroy(self):
        del self

    def set_position(self, position):
        self.position = position

    def set_visible(self, visible):
        self.visible = visible

    def set_enable(self, enable):
        self.enable = enable

    def event(self, event, parametres):
        if self.enable:
            if parametres is None:
                event()
            else:
                event(*parametres)


class CreatureCircle(Creature):
    def __init__(self, surface, position=None, size=10, color=(255, 255, 255),
                 direction=3 * 3.14 / 4):
        super().__init__(surface, position)
        self.size = size
        self.color = color
        self.direction = direction

    def draw(self):
        pygame.draw.circle(self.surface, self.color, self.position, self.size)

    def tick(self, fps):
        lenght = 100 / (1000 / fps)
        lowx, lowy, highx, highy = [True for i in range(4)]
        i = 0
        while lowx or lowy or highx or highy:
            i += 1
            newx = self.position[0] + lenght * math.cos(self.direction)
            newy = self.position[1] - lenght * math.sin(self.direction)
            lowx = newx < 10
            lowy = newy < 10
            highx = newx > self.surface.get_size()[0] - 10
            highy = newy > self.surface.get_size()[1] - 10
            if lowx or lowy or highx or highy:
                self.direction -= 1.57
                while self.direction < 0:
                    self.direction += 6.28
            if i > 10:
                self.destroy()
                return True
        self.set_position((int(newx), int(newy)))


FPS = 60
clock = pygame.time.Clock()

size = (500, 500)
display = PygameSurface(size=size)
display.set_caption('Шары')
circles = []

while True:

    todel = []
    display.fill((0, 0, 0))
    for i in circles:
        if i.tick(FPS):
            todel.append(i)
        i.draw()
    for i in todel:
        del circles[circles.index(i)]
    display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            circles.append(CreatureCircle(display.get_display(), pygame.mouse.get_pos()))

    clock.tick(FPS)
