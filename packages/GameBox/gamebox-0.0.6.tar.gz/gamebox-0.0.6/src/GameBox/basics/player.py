import pygame
import os
from ..basics._core import GLOBAL

class Player:
    def __init__(self, pos, spritePath, dim, camera, scale = 1):
        self.last_pos = pos
        self.pos = pos
        self.camera = camera
        self.sprite = pygame.transform.scale_by(pygame.image.load(spritePath), scale)
        self.collisions = []
        self.width = dim[0]
        self.height = dim[1]
        self.Info = {
            "velocity": [0, 0],
            "on_ground": False
        }
        self.states = {}
        self.currentState = None
        GLOBAL.playerPosition = pygame.Rect(pos, dim)
        self.screen = GLOBAL.screen

    def display(self, dt):
        self.collisions = GLOBAL.collisions
        if self.currentState != None:
           #state logic
           self.changeState()
           image = self.states[self.currentState]["animation"].update(dt)
           self.screen.blit(image, self.pos)
        else:
            #if no states (when initalized first)
            self.screen.blit(self.sprite, self.pos)

    def changeState(self):
        # Define collision rectangles relative to the player
        collision_map = {
            "^": pygame.Rect(self.pos[0], self.pos[1]-10, self.width, 10),      
            "_": pygame.Rect(self.pos[0], self.pos[1] + self.height+10, self.width, 10), 
            "<": pygame.Rect(self.pos[0]-10, self.pos[1], 10, self.height),       
            ">": pygame.Rect(self.pos[0]+10 + self.width - 10, self.pos[1], 10, self.height), 
            "#": pygame.Rect((self.pos[0]-10, self.pos[1]-10), (self.width+20, self.height+20)),      
            "N": pygame.Rect((self.pos[0]-10, self.pos[1]-10), (self.width+20, self.height+20)),                  
        }

        for state, data in self.states.items():
            condition = data.get("condition", "")
            if len(condition) < 2:
                print("Invalid condition:", condition)
                continue

            type_code, dir_code = condition[0], condition[1]

            if type_code =="C":
                rect = collision_map[dir_code]
                hit = self.check_collisions(rect)
                os.system("cls")
                print(hit)

                # Handle state change
                if dir_code == "N":
                    if not hit:
                        self.currentState = state
                        break
                else:
                    if hit:
                        self.currentState = state
                        break
            elif type_code =="M":
                #setup
                if self.camera.type == "dynamic":
                    pos = self.camera.pos
                else:
                    pos = self.pos
                #code
                if dir_code == "^":
                    if pos[1] - self.last_pos[1] >0:
                        self.currentState = state
                        break
                elif dir_code == "_":
                    if pos[1] - self.last_pos[1] <0:
                        self.currentState = state
                        break
                elif dir_code == "<":
                    if pos[0] - self.last_pos[0] <0:
                        self.currentState = state
                        break
                elif dir_code == ">":
                    if pos[0] - self.last_pos[0] >0:
                        self.currentState = state
                        break
                elif dir_code != "#":
                    if pos[0] == self.last_pos[0]:
                        self.currentState = state
                        break
                elif dir_code == "N":
                    if pos[0] - self.last_pos[0] >0:
                        self.currentState = state
                        break
            else:
                raise Exception("Not combatible condition type")



    def check_collisions(self, test_rect):
        for collider in self.collisions:
            if test_rect.colliderect(collider):
                return True
        return False


    def Add_state(self, name, animation, condition):
        self.currentState = name
        self.states[name] = {"animation": animation, "condition": condition}


    def update_position(self, UP_A):
        x, y = self.pos
        vx, vy = self.Info.get("velocity", [0, 0])

        # --- Check X movement first ---
        new_x = x + UP_A[0]
        player_rect_x = pygame.Rect(new_x, y, self.width, self.height)

        blocked_x = None
        for rect in self.collisions:
            if rect.colliderect(player_rect_x):
                blocked_x = rect
                break

        if blocked_x:
            vx = 0  # stop horizontal velocity when colliding
        else:
            x = new_x

        # --- Check Y movement separately ---
        new_y = y + UP_A[1]
        player_rect_y = pygame.Rect(x, new_y, self.width, self.height)

        blocked_y = None
        for rect in self.collisions:
            if rect.colliderect(player_rect_y):
                blocked_y = rect
                break

        if blocked_y:
            if vy > 0:  # falling → landed on top of something
                y = blocked_y.top - self.height
                self.Info["on_ground"] = True
            elif vy < 0:  # jumping → hit head on ceiling
                y = blocked_y.bottom
            vy = 0  # stop vertical velocity
        else:
            y = new_y
            self.Info["on_ground"] = False

        # --- Apply movement ---
        if self.camera.type == "dynamic":
            self.last_pos = self.camera.pos
            dx = x - self.pos[0]
            dy = y - self.pos[1]
            self.camera.move(dx, dy)
        elif self.camera.type == "fixed":
            self.last_pos = self.pos
            self.pos = (x, y)
            GLOBAL.playerPosition = pygame.Rect((x, y) (self.width, self.height))

        # Save velocity (updated after collisions)
        self.Info["velocity"] = [vx, vy]



    #=== movement ===

    def move_by_WSAD(self, speed):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Update player position based on key presses\
        x,y = self.pos
        if keys[pygame.K_a]:
            x -= -speed
        if keys[pygame.K_d]:
            x += -speed
        if keys[pygame.K_w]:
            y -= -speed
        if keys[pygame.K_s]:
            y += -speed

        new_x = self.pos[0]
        new_x-=x

        new_y = self.pos[1]
        new_y -= y

        self.update_position((new_x, new_y))

    def move_by_arrows(self, speed):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Update player position based on key presses\
        x,y = self.pos
        if keys[pygame.K_UP]:
            x -= -speed
        if keys[pygame.K_DOWN]:
            x += -speed
        if keys[pygame.K_LEFT]:
            y -= -speed
        if keys[pygame.K_RIGHT]:
            y += -speed

        new_x = self.pos[0]
        new_x-=x

        new_y = self.pos[1]
        new_y -= y

        self.update_position((new_x, new_y))

    def platformer_movement(self, speed, gravity, jump_force, max_gravity):
        keys = pygame.key.get_pressed()

        # Current velocity
        vx, vy = self.Info.get("velocity", [0, 0])

        # Horizontal movement
        if keys[pygame.K_a]:
            vx = -speed
        elif keys[pygame.K_d]:
            vx = speed
        else:
            vx = 0

        # Gravity (affects vertical velocity, not position directly)
        vy += gravity
        if vy > max_gravity:
            vy = max_gravity

        # Jump (only if on_ground — assuming update_position sets this)
        if keys[pygame.K_w] and self.Info.get("on_ground", False):
            vy = -jump_force

        # Save velocity
        self.Info["velocity"] = [vx, vy]

        # Move position — let update_position handle collisions
        self.update_position((vx, vy))



class Animation:
    def __init__(self, image, tileSize, dim, speed, frames, scale, X_offset):
        self.image = image
        self.tileSize = tileSize
        self.fileDim = dim
        self.speed = speed
        self.images = []
        self.timer = 0
        self.frames = frames
        self.index = 0

        # Load images (crop each tile)
        for y in range(dim[1]):
            for x in range(dim[0]):
                # Create a fresh surface for this tile
                surface = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                # Define the rectangle area on the sheet
                rect = pygame.Rect(
                    x * tileSize +X_offset*tileSize,
                    y * tileSize,
                    tileSize,
                    tileSize
                )
                # Copy the correct tile into the new surface
                surface.blit(image, (0, 0), rect)
                # Store it in the images dictionary
                self.images.append(pygame.transform.scale_by(surface, scale))

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % self.frames
        return self.images[self.index]