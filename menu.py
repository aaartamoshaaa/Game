import sys

import pygame
import pygame_gui
from random import randint

FPS = 1440


class player:
    def __init__(self, position, color):
        self.x, self.y = position
        self.color = color

    def move(self):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x -= 30 / FPS * 20
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x += 30 / FPS * 20
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.y -= 30 / FPS * 20
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.y += 30 / FPS * 20

    def render(self, screen):
        pygame.draw.rect(screen, (self.color), (self.x, self.y, 50, 50))


class enemy(player):
    def render(self, screen):
        pygame.draw.rect(screen, (self.color), (randint(100, 600), randint(100, 300), 50, 50))


def game():
    player1 = player((100, 100), 'red')
    player2 = enemy((200, 200), 'green')

    running = True
    while running:
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player1.move()
        player2.move()
        # отрисовка и изменение свойств объектов
        screen.fill((255, 255, 255))
        player1.render(screen)
        player2.render(screen)

        # обновление экрана
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


def main_menu():
    menu = True
    while menu:
        screen.fill((100, 100, 100))
        time_delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        game()
            manager.process_events(event)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    sys.exit()


pygame.init()
size = width, height = 800, 400
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((800, 400))

play_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((300, 150), (100, 50)),
    text='Play',
    manager=manager)

main_menu()
