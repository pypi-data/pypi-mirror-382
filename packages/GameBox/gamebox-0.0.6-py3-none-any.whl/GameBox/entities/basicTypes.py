import pygame
from ..basics._core import GLOBAL

class Static_enemy:
    def __init__(self, pos, animation, camera, dim, collision = True):
        self.pos = pos
        self.animation = animation
        self.cam = camera
        self.dim = dim
        self.col = collision
        self.screen = GLOBAL.screen

    def display(self, dt):
        if self.cam.type == "dynamic":
            x, y = self.pos
            x -= self.cam.pos[0]
            y -= self.cam.pos[1]
        self.screen.blit(self.animation.update(dt), (x, y))
        if self.col:
            GLOBAL.collisions.append(pygame.Rect((x, y), self.dim))


class Dynamic_enemy:
    def __init__(self, pos, travelPos, flip, animation, camera, dim, collision=True, speed=100):
        self.pos = list(pos)  # mutable copy for movement
        self.start_pos = list(pos)  # remember starting position
        self.travel = list(travelPos)  # target position
        self.flip = flip
        self.animation = animation
        self.cam = camera
        self.dim = dim
        self.dir = 1  # 1 = toward travelPos, -1 = back to start
        self.speed = speed  # pixels per second
        self.col = collision
        self.screen = GLOBAL.screen

    def move(self, dt):
        target = self.travel if self.dir == 1 else self.start_pos
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]

        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            return  # Already at target

        move_dist = self.speed * dt
        if move_dist >= distance:
            next_pos = target.copy()  # would snap to target
        else:
            next_pos = [
                self.pos[0] + (dx / distance) * move_dist,
                self.pos[1] + (dy / distance) * move_dist
            ]

        # --- Collision check with player ---
        enemy_next_rect = pygame.Rect(
            next_pos[0]-self.cam.pos[0], next_pos[1]-self.cam.pos[1], self.dim[0], self.dim[1]
        )
        if enemy_next_rect.colliderect(GLOBAL.playerPosition):
            return  # Stop movement this frame if player is blocking

        # If no collision, commit the move
        self.pos = next_pos if move_dist < distance else target.copy()
        if move_dist >= distance:
            self.dir *= -1  # reverse direction


    def display(self, dt):
        self.move(dt)

        x, y = self.pos
        if self.cam.type == "dynamic":
            x -= self.cam.pos[0]
            y -= self.cam.pos[1]
        self.screen.blit(self.animation.update(dt), (x, y))
        if self.col:
            GLOBAL.collisions.append(pygame.Rect((x, y), self.dim))


