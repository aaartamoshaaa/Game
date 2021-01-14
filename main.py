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


class CreatureCircle(Creature):
    def __init__(self, surface, position=(0, 0), size=0, color=(255, 255, 0),
                 direction=3 * 3.14 / 4):
        super().__init__(surface, position)
        self.size = size
        self.color = color
        self.direction = direction
        self.xx, self.yy = -1, -1

    def draw(self):
        if not self.enable:
            return
        pygame.draw.circle(self.surface, self.color, self.position, int(self.size))

    def tick(self, fps):
        if not self.enable:
            return
        resize = .1 * (1000 / fps)
        self.size = self.size + resize


FPS = 60
clock = pygame.time.Clock()

size = (500, 500)
display = PygameSurface(size=size)
display.set_caption('Шар')
circle = CreatureCircle(display.get_display())
circle.set_enable(False)

while True:
    display.fill((0, 0, 255))
    circle.draw()
    circle.tick(FPS)
    display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            del circle
            circle = CreatureCircle(display.get_display(), pygame.mouse.get_pos())

    clock.tick(FPS)
