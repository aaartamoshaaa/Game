import sys

import pygame
import pygame_gui
from random import randint

FPS = 1440
SIZE = WIDTH, HEIGHT = 800, 400
THEME_COLOR_MAIN = "#0f3460"
THEME_COLOR_PINK = "#e94560"
THEME_COLOR_ORANGE = "#ff9900"
THEME_COLOR_DARK = "#1a1a2e"


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


def main_menu():
    running = True
    while running:
        screen.fill(THEME_COLOR_MAIN)
        time_delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        ip_want()
            manager_main.process_events(event)

        manager_main.update(time_delta)
        manager_main.draw_ui(screen)
        pygame.display.update()
        clock.tick(60)


def ip_want():
    running = True
    while running:
        screen.fill(THEME_COLOR_MAIN)
        time_delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    pass
                    # if event.ui_element == play_button:
                    #     pass
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    print(event.text)
                    game()
            manager_ip.process_events(event)

        manager_ip.update(time_delta)
        manager_ip.draw_ui(screen)
        pygame.display.update()
        clock.tick(60)


def game():
    player1 = player((100, 100), THEME_COLOR_PINK)
    player2 = enemy((200, 200), THEME_COLOR_ORANGE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        player1.move()
        player2.move()
        screen.fill(THEME_COLOR_MAIN)
        player1.render(screen)
        player2.render(screen)

        pygame.display.update()
        clock.tick(FPS)


pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
manager_main = pygame_gui.UIManager(SIZE, 'theme.json')
manager_ip = pygame_gui.UIManager(SIZE, 'theme.json')
# manager_ip.set_visual_debug_mode(True)
# manager_main.set_visual_debug_mode(True)
play_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH // 2 - 50, HEIGHT // 2 - 25), (100, 50)),
    text='Play',
    manager=manager_main)

ip_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH // 2 - 200, 45), (400, 30)),
    text='Enter IP of the server',
    manager=manager_ip)

ip_wanter = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((WIDTH // 2 - 200, HEIGHT // 2 - 100), (400, 50)),
    manager=manager_ip)
ip_wanter.set_allowed_characters(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ':'])

main_menu()