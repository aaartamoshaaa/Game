# ui objects
from interface import UI, UIElement, Padding, Margin
from pygame_gui.elements import UILabel, UIButton, UITextEntryLine
# handlers
from interface import main_menu_events_handler, \
    change_interface, quit_from_game, load_game, exit_event_handler
# gam objects
from interface import Game


game = Game()
# main menu
game.add_interface(
    'main',
    interface=UI(
        elements=[
            UIElement(UILabel, 300, 50, text='SPACESHIPS'),
            UIElement(UIButton, 200, 75, text='PLAY', ui_id='play-button'),
            UIElement(UIButton, 200, 75, text='EXIT', ui_id='exit-button')
        ],
        hor_layout=UI.Center,
        ver_layout=UI.Top,
        padding=Padding.all(200),
        margin=Margin.only(bottom=30)
    )
)
# main menu buttons
game.add_handler(
    interface_name='main',
    handler=main_menu_events_handler
)
# ip entry menu
game.add_interface(
    'ip-entry',
    interface=UI(
        elements=[
            UIElement(UILabel, 300, 50, text='Enter server IP address'),
            UIElement(UITextEntryLine, 300, 50),
        ],
        hor_layout=UI.Center,
        ver_layout=UI.Top,
        padding=Padding.all(0),
        margin=Margin.only(bottom=10)
    )
)
# main -> ip entry
game.add_handler(
    interface_name='main',
    handler=lambda event:
        change_interface(event, 'play-button', game, 'ip-entry')
)
# main - 1st interface
game.set_interface('main')

# game menu
game.add_interface(
    name='game',
    interface=UI(elements=[]),
    need_to_update_handlers=False  # we don`t need global handlers here
)
game.add_handler(
    interface_name='game',
    handler=lambda event: quit_from_game(event, game)
)

# ip entry -> game
game.add_handler(
    interface_name='ip-entry',
    handler=lambda event: load_game(event, game)
)
# exit button (Native)
game.add_global_handler(exit_event_handler)
# run game
game.start()
