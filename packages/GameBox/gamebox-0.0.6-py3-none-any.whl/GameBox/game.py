import pygame
from .basics._core import GLOBAL

class Game:
    def __init__(self, width, height,  background_color = "black"):
        pygame.font.init()
        self.dim = width, height
        self.color = background_color
        self.objects = []
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        GLOBAL.BaseInfo["screenDim"] = self.screen.get_size()
        GLOBAL.screen = self.screen


    def show(self, obj):
        self.objects.append(obj)

    def update(self):
        GLOBAL.collisions.clear()
        self.screen.fill(self.color)
        dt = self.clock.tick(60)/1000
        for obj in self.objects:
            obj.display(dt)
        pygame.display.update()

    def show_list(self, objs):
        for item in objs:
            self.objects.append(item)