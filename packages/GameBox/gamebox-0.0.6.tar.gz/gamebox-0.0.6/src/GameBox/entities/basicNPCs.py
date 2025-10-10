import pygame
from ..basics._core import GLOBAL

class Static_NPC:
    def __init__(self, pos, animation, dim, camera, collision = True):
        self.pos = pos
        self.anim = animation
        self.dim = dim
        self.cam = camera
        self.col = collision
        self.screen = GLOBAL.screen

    def display(self, dt):
        image = self.anim.update(dt)
        x, y = self.pos
        if self.cam.type == "dynamic":
            x-=self.cam.pos[0]
            y-=self.cam.pos[1]
        self.screen.blit(image, (x, y))
        if self.col:
            GLOBAL.collisions.append(pygame.Rect((x, y), self.dim))
