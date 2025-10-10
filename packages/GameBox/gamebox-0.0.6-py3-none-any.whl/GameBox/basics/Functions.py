import pygame

def DisplayText(text, color, size, pos, screen):
    font = pygame.font.Font(None, size)
    textSurf = font.render(text, False, color)
    screen.blit(textSurf, pos)

def getTilePosInGrid(pos,  grid_size):
    x, y = pos
    return (x // grid_size, y // grid_size)

class IsWithinBounds:
    def __init__(self, dim, offset):
        self.offset = offset
        self.dim = dim

    def checkPos(self, pos):
        x, y = pos
        w, h = self.dim
        w+=self.offset
        h+=self.offset
        if x > w or y > h:
            return False
        w=-self.offset
        h=-self.offset
        if x < w or y < h:
            return False
        return True

class State_conditions:
    def __init__(self):
        self.top = "C^"
        self.bottom = "C_"
        self.left = "C<"
        self.right = "C>"
        self.any = "C#"
        self.none = "CN"
        self.move_up = "M^"
        self.move_down = "M_"
        self.move_left = "m<"
        self.move_right = "M>"
        self.move_any = "M#"
        self.move_none = "MN"
