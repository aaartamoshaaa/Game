import pygame

FPS = 15


class kvadrat:
    def __init__(self, position, color):
        self.x, self.y = position
        self.color = color

    def move(self, sobitye):
        pass

    def render(self, screen):
        pygame.draw.rect(screen, (self.color), (self.x, self.y, 50, 50))


if __name__ == '__main__':
    pygame.init()
    size = width, height = 800, 400
    screen = pygame.display.set_mode(size)

    player1 = kvadrat((100, 100), 'red')

    clock = pygame.time.Clock()
    running = True
    while running:
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
        screen.fill((255, 255, 255))
        clock.tick(FPS)

        # отрисовка и изменение свойств объектов
        player1.render(screen)

        # обновление экрана
        pygame.display.flip()
    pygame.quit()
