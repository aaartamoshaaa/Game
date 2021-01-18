import math

FPS = 1440
SPEED = 600 / FPS


class SpaceShip:
    def __init__(self, id, position, angle, abilities, health, image_file):
        # color is needed for identify players
        self.id = id
        # Coordinates of the spaceship on board
        self.x, self.y = position
        # angle of movement and look-angle
        self.angle = angle
        # color is needed for identify enemies and player
        # abilities is a list of perks for this spaceship
        self.abilities = abilities
        # health is health
        self.health = health
        # image what will be used for drawing spaceship on screen
        self.icon = image_file

    def render(self):
        # todo Redraw spaceship image here
        pass

    def rotate_by_angle(self, delta):
        """
        Increase angle by delta
        """
        self.angle += delta
        self.angle %= 360
        self.render()  # can be unnecessary

    def rotate(self, *args):
        """
        Function used to turn spaceship to coordinates
        If given 1 arg it must be tuple or list of x and y coordinates
        or 2 args as x and y
        for example rotate((123, 321)) or rotate(123, 321);
        """
        x, y = 0, 0
        if len(args) == 1:  # 1 argument - position (iterable)
            x, y = args[0]
        elif len(args) == 2:  # 2 arguments (x and y)
            x, y = args[:2]
        new_angle = round(math.atan((x - self.x) / (y - self.y)))
        self.angle = new_angle
        self.angle %= 360
        self.render()  # can be unnecessary

    def get_position(self):
        return self.x, self.y

    def get_angle(self):
        return self.angle

    def set_position(self, position):
        self.x, self.y = position

    def set_angle(self, angle):
        self.angle = angle
        self.angle %= 360


class Observer:
    pass
    # todo here must be pygame logic; move spaceship here
