import pygame
import json
from .editor import Editor
from ..basics._core import GLOBAL
from ..basics.Functions import IsWithinBounds
from ..game import Game

class Tilemap:
    def __init__(self, tileSize, fileDim, image, camera, scale=1):
        # Scale tile size
        self.size = int(tileSize * scale)

        self.fileDim = fileDim
        self.images = {}
        self.currentLayer = "ground"
        self.layers = {
            "ground": []
        }
        self.Crect = []
        self.collisions = {}
        self.camera = camera
        self.loadedImage = image
        self.isEditor = False
        self.scale = scale
        self.Tsize = tileSize
        self.createCollisionData()
        self.screen = GLOBAL.screen

        self.optim = IsWithinBounds(GLOBAL.BaseInfo["screenDim"], self.size)

        # Load images (crop each tile)
        for y in range(fileDim[1]):
            for x in range(fileDim[0]):
                # Create a fresh surface for this tile
                surface = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                # Define the rectangle area on the sheet
                rect = pygame.Rect(
                    x * tileSize,
                    y * tileSize,
                    tileSize,
                    tileSize
                )
                # Copy the correct tile into the new surface
                surface.blit(image, (0, 0), rect)
                # Store it in the images dictionary
                self.images[str([x, y])] = pygame.transform.scale(surface, (self.size, self.size))

        for tileID in self.images:
            self.collisions[tileID] = "none"

    def Add_layer(self, name):
        self.layers[name] = []

    def display(self, dt):
        self.draw_tiles()
        if self.isEditor:
            self.editor.update(self.camera)
            self.editor.display(self.screen, self.camera)


    def draw_tiles(self):
        if self.isEditor:
            self.layers = self.editor.layers
            self.collisions = self.editor.collision
            GLOBAL.collisions = self.Crect
            #update rects
            self.createCollisionRects()
        for layer in self.layers:
            for item in self.layers[layer]:
                tile, pos = item
                x = pos[0]*self.size
                x -= self.camera.pos[0]
                y = pos[1]*self.size
                y -= self.camera.pos[1]
                if self.optim.checkPos((x, y)):
                    self.screen.blit(self.images[str(tile)], (x, y))



    def createCollisionRects(self):
        self.Crect.clear()
        for layer in self.layers:
            for tile in self.layers[layer]:
                tx, ty = tile[0]
                x, y = tile[1]
                tile_type = self.collisions[str([tx, ty])]
                type = self.RealCollisionTiles[tile_type]
                if tile_type != "none":
                    x = (x*self.size)
                    y = (y*self.size)
                    x+=type[0][0] - self.camera.pos[0]
                    y+=type[0][1] - self.camera.pos[1]
                    width = type[1][0]
                    height = type[1][1]
                    self.Crect.append(pygame.Rect((x, y), (width, height)))


    def createCollisionData(self):
        size = self.Tsize
        self.CollisionTiles = {
            "none": ((0, 0), (size, size)),
            "full": ((0, 0), (size, size)),
            "half1": ((0, 0), (size, size//2)),
            "half2": ((0, size/2), (size, size/2)),
            "half3": ((0, 0), (size/2, size)),
            "half4": ((size/2, 0), (size/2, size)),
            "center": ((size/4, size/4), (size/2, size/2))
        }
        #real tile sizes
        size = self.size
        self.RealCollisionTiles = {
            "none": ((0, 0), (size, size)),
            "full": ((0, 0), (size, size)),
            "half1": ((0, 0), (size, size//2)),
            "half2": ((0, size/2), (size, size/2)),
            "half3": ((0, 0), (size/2, size)),
            "half4": ((size/2, 0), (size/2, size)),
            "center": ((size/4, size/4), (size/2, size/2))
        }

            

    def enable_editor(self, scren_width, screen_height):
        self.isEditor = True
        self.editor = Editor(self.size, self.loadedImage, (scren_width, screen_height), self.fileDim, self.images, self.layers, self.Tsize, self.currentLayer, self.collisions, self.CollisionTiles)


    def save_map(self, filepath):
        with open(filepath, "w") as file:
            data = {
                "TileData" : self.layers,
                "CollisionData": self.collisions
            }
            json.dump(data, file)

    def load_map(self, filepath):
        with open(filepath, "r") as file:
            data = dict(json.load(file))
            self.layers = dict(data["TileData"])
            self.collisions = dict(data["CollisionData"])
            self.currentLayer = "ground"

    def get_editor_status(self):
        return self.editor.active

        