import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIButton
import sys

FPS = 100


class Window:
    size = width, height = 1280, 720


class Theme:
    file = 'theme.json'

    class Colors:
        main = '#0f3460'
        pink = '#e94560'
        orange = '#ff9900'
        dark = '#1a1a2e'


class UIElement:
    """All for u
    """

    def __init__(self, prototype, width, height, ui_id='', **additional):
        if ui_id:
            self.id = ui_id
        else:
            self.id = str(id(self))
        self.prototype = prototype
        self.width = width
        self.height = height
        self.args = additional

    def spawn(self, x, y, manager):
        rect = pygame.Rect(x, y, self.width, self.height)
        self.prototype(
            relative_rect=rect,
            manager=manager,
            object_id=self.id,
            **self.args
        )


class Padding:
    def __init__(self, top, bottom, right, left):
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left

    def symmetric(horizontal=0, vertical=0):
        return Padding(vertical, vertical, horizontal, horizontal)

    def all(x):
        return Padding(x, x, x, x)

    def only(top=0, bottom=0, right=0, left=0):
        return Padding(top, bottom, right, left)


Margin = Padding


class UI:
    """I live in an abstract world
    Designed for easy interface assembly
    """
    Center = 0
    Top = 1
    Bottom = 2
    Right = 3
    Left = 4

    def __init__(self, elements, width=Window.width, height=Window.height,
                 hor_layout=Right, ver_layout=Top, margin=Margin.all(0), padding=Padding.all(0)):
        self.manager = pygame_gui.UIManager((width, height), Theme.file)
        self.handlers = []
        self.element_ids = []
        x_cords = []
        y_cords = []
        # * Horizontal layout
        if hor_layout == UI.Center:
            x_cords = [(width - element.width)/2 for element in elements]
        elif hor_layout == UI.Right:
            last_x = width - padding.right
            for element in elements:
                last_x -= element.width + margin.left + margin.right
                x_cords.append(last_x)
        elif hor_layout == UI.Left:
            last_x = padding.left
            for element in elements:
                last_x += element.width + margin.left + margin.right
                x_cords.append(last_x)
        else:
            raise ValueError(
                'Horizontal layout must be either left or right or center')
        # * Vertical layout
        if ver_layout == UI.Top:
            last_y = padding.top
            for element in elements:
                last_y += element.height + margin.top + margin.bottom
                y_cords.append(last_y)
        elif ver_layout == UI.Bottom:
            last_y = height - padding.bottom
            for element in elements:
                last_y -= element.height + margin.top + margin.bottom
                y_cords.append(last_y)
        else:
            raise ValueError('Vertical layout must be either top or bottom')

        for i in range(len(elements)):
            self.element_ids.append(elements[i].id)
            elements[i].spawn(
                x_cords[i],
                y_cords[i],
                self.manager,
            )

    def draw(self, screen):
        self.handle_events()
        self.manager.draw_ui(screen)

    def add_handler(self, function):
        self.handlers.append(function)

    def handle_events(self):
        for event in pygame.event.get():
            for handler in self.handlers:
                handler(event)
            self.manager.process_events(event)


class Game:
    """Main class
    Combines all classes into one beautiful thing
    """

    def __init__(self, size=Window.size):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.current_interface = None
        self.interfaces = {}

    def add_interface(self, name, interface):
        self.interfaces[name] = interface

    def add_handler(self, interface_name, handler):
        self.interfaces[interface_name].add_handler(handler)

    def add_global_handler(self, handler):
        for interface in self.interfaces:
            self.interfaces[interface].add_handler(handler)

    def set_interface(self, name):
        self.current_interface = self.interfaces[name]

    def start(self):
        done = False
        while not done:
            self.screen.fill(Theme.Colors.main)
            self.current_interface.manager.update(1000/FPS)
            self.current_interface.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

def exit_event_handler(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)

def change_interface(event, button_id, obj, new_interface_name):
    if event.type == pygame.USEREVENT:
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == button_id:
                obj.set_interface(new_interface_name)

def main_handler(event): 
    if event.type == pygame.USEREVENT:
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == 'exit':
                pygame.quit()
                sys.exit(0)


if __name__ == '__main__':
    game = Game()
    game.add_interface(
        name = 'main', 
        interface = UI(
            elements=[
                UIElement(UILabel, 300, 50, text='SpaceShip Game'),
                UIElement(UIButton, 100, 50, text='Play', ui_id='play'),
                UIElement(UIButton, 100, 50, text='Volume', ui_id='volume'),
                UIElement(UIButton, 100, 50, text='Exit', ui_id='exit')
            ],
            hor_layout=UI.Center,
            ver_layout=UI.Top,
            margin=Margin.only(bottom=10),
            padding=Padding.all(0),
        )
    )
    game.add_handler(interface_name='main', handler=main_handler)

    game.add_interface(
        name='game',
        interface = UI(
            elements=[
                UIElement(UILabel, 300, 50, text='Game'),
            ],
            hor_layout=UI.Center,
            ver_layout=UI.Top,
            margin=Margin.all(0),
            padding=Padding.all(0),
        )
    )
    game.add_handler('main', handler=lambda event: 
        change_interface(event, 'play', game, 'game')
    )
    game.add_interface(
        name='settings',
        interface = UI(
            elements=[
                UIElement(UILabel, 300, 50, text='Volume'),
                UIElement(UIButton, 100, 50, text='Back', ui_id='back')
            ],
            hor_layout=UI.Center,
            ver_layout=UI.Top,
            margin=Margin.all(0),
            padding=Padding.all(0),
        )
    )
    game.add_handler('settings', handler=lambda event:
        change_interface(event, 'back', game, 'main')
    )
    game.add_handler('main', handler=lambda event:
        change_interface(event, 'volume', game, 'settings')
    )

    game.add_global_handler(exit_event_handler)
    game.set_interface('main')
    game.start()
