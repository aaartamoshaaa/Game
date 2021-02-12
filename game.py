import sys
import pygame
import pygame_gui
from game_objects import *


# ----------------------------------------------------------------

#  THIS MODULE DEPRECATED, DO NOT USE THIS

# ----------------------------------------------------------------

IP = ''
PORT = 0
SIZE = WIDTH, HEIGHT = 800, 600
THEME_COLOR_MAIN = "#0f3460"
THEME_COLOR_PINK = "#e94560"
THEME_COLOR_ORANGE = "#ff9900"
THEME_COLOR_DARK = "#1a1a2e"


def main_menu():
    global observer
    running = True
    while running:
        screen.fill(THEME_COLOR_MAIN)
        time_delta = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                if observer:
                    observer.kill()
                sys.exit()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        ip_want()
            manager_main.process_events(event)

        manager_main.update(time_delta)
        manager_main.draw_ui(screen)
        pygame.display.update()
        clock.tick(FPS)


def ip_want():
    global IP, PORT
    running = True
    while running:
        screen.fill(THEME_COLOR_MAIN)
        time_delta = clock.tick(FPS) / 1000
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
                    IP, PORT = event.text.split(':')
                    PORT = int(PORT)
                    game()
            manager_ip.process_events(event)

        manager_ip.update(time_delta)
        manager_ip.draw_ui(screen)
        pygame.display.update()
        clock.tick(FPS)


observer = None


def game():
    global IP, PORT, observer
    observer = Observer((IP, PORT), screen)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        observer.move_rival()
        screen.fill(THEME_COLOR_MAIN)
        observer.update()
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
# ip_wanter.set_allowed_characters(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ':'])

main_menu()
