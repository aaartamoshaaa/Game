import pygame
import sys

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
    def move(self, x, y):
        self.x, self.y = x, y
        super(Enemy, self).move()


def redraw_window(*objects):
    _window.fill((255, 255, 255))
    for element in objects:
        element.draw(_window)
    pygame.display.update()


def main():
    player = Player(50, 50, 75, 75, (0, 255, 0))
    enemy = Enemy(350, 350, 75, 75, (255, 0, 0))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        player.move()
        enemy.move(350, 350)
        redraw_window(player, enemy)
        clock.tick(60)


main()
