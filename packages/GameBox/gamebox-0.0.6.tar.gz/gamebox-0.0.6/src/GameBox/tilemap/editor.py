import pygame
import math
from ..basics.Functions import DisplayText
from ..basics.Functions import getTilePosInGrid as getTilePos

class Editor:
    def __init__(self, tilesize, file, winDim, fileDim, imageDict, layers, size, currentLayer, C_tiles, C_Data):
        print("""====INGAME EDITOR ENABLED, PRESS "e" TO USE====""")
        self.Tsize = tilesize
        self.image = file
        self.width = winDim[0]
        self.height = winDim[1]
        self.fileDim = fileDim
        self.images = imageDict
        self.layers = layers
        self.currentLayer = currentLayer

        self.active = False
        self.Constdis = {
            "title" : "TileMap Editor",
            "T_color" : "white",
            "T_size" : 50,
            "T_pos" : (self.width-(self.width/4)+40, self.height-(self.height/6)+40)
        }

        self.state = "standby"
        self.selectedTile = (0, 0)
        self.SelTileDict = [0, 0]
        self.DictPos = (0, 0)
        self.imageSize = size
        self.collision = C_tiles
        self.Cdata = C_Data
        self.Col = {
            "state" : "standby",
            "selected": "none",
            "exit": False
        }

        #self.space_pressed_last = False

    def update(self, cam):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_e] and not self.e_pressed_last:
            self.active = not self.active
        self.e_pressed_last = keys[pygame.K_e]
        if self.active:
            self.key_toggles(keys)
        else:
            self.resetStates()
        #erase tiles
        if pygame.mouse.get_pressed(3)[2] and self.active:
            mx, my = pygame.mouse.get_pos()
            # Convert mouse to world coordinates
            world_x = mx + cam.pos[0]
            world_y = my + cam.pos[1]
            # Snap to grid
            x, y = getTilePos((world_x, world_y), self.Tsize)
            # Remove any tile at that world grid position
            tiles = self.layers[self.currentLayer]
            tiles = [tile for tile in tiles if tile[1] != [x, y]]
            self.layers[self.currentLayer] = tiles


    def display(self, screen, cam):
        if self.active:
            self.basicUI(screen)
            if self.state == "picking":
                self.Picking(screen)
            if self.state == "paint":
                self.Paint(screen, cam)
            if self.state == "collisionEditing":
                self.collision_editing(screen)

    def collision_editing(self, screen):
        screen.fill("black")
        screen.blit(self.image, (0, 0))
        self.collision_Base_ui(screen)
        self.collisionOverlay(screen)
        if self.Col["state"] == "painting":
            if pygame.mouse.get_pos()[1] > self.height - self.height//6 and self.Col["exit"]:
                self.Col["exit"] = False
                self.Col["state"] = "standby"
            data = self.Cdata[self.Col['selected']]
            #tile to follow mouse
            x, y = pygame.mouse.get_pos()
            pos = (getTilePos((x, y), self.imageSize))
            pygame.draw.rect(screen, "yellow", pygame.Rect((pos[0]*self.imageSize+data[0][0], pos[1]*self.imageSize+data[0][1]), data[1]))
            if pygame.mouse.get_pressed(3)[0] and self.Col["exit"]:
                #get index
                index = getTilePos(pygame.mouse.get_pos(), self.imageSize)
                x, y = index
                if x<self.fileDim[0] and y<self.fileDim[1] and x>=0 and y>=0:
                    self.collision[str([x, y])] = self.Col["selected"]


    def collisionOverlay(self, screen):
        x, y = 0, self.fileDim[1]*self.imageSize+25
        screen.blit(self.image, (0, y))
        rect = pygame.Rect(x, y, self.fileDim[0]*self.imageSize, self.fileDim[1]*self.imageSize)
        pygame.draw.rect(screen, "white", rect, 2)
        for value in self.collision.values():
            data = self.Cdata[value]
            if value != "none":
                pygame.draw.rect(screen, "yellow", pygame.Rect((data[0][0]+x, data[0][1]+y), data[1]))
            x+=self.imageSize
            if x>=self.fileDim[0]*self.imageSize:
                y+=self.imageSize
                x=0
            

    def collision_Base_ui(self, screen):
        pygame.draw.rect(screen, "gray", pygame.Rect((0, self.height-self.height//6), (self.width, self.height-self.height//6)))
        self.basicUI(screen)
        #display tileset
        #display collision paintable tiles
        x = 0
        y = (self.height - self.height//6)
        for tile in self.Cdata:
            data = self.Cdata[tile]
            if tile!="none":
                pygame.draw.rect(screen, "yellow", pygame.Rect(data[0][0]+x, data[0][1]+y, data[1][0], data[1][1]))
            else:
                pygame.draw.rect(screen, "green", pygame.Rect(data[0][0]+x, data[0][1]+y, data[1][0], data[1][1]), 7)
            x+=self.Tsize
        if pygame.mouse.get_pos()[1] < self.height - self.height//6:
            self.collisionPointer_paint(screen)
        else:
            self.collisionPointer_change(screen)

        if pygame.mouse.get_pos()[1] < self.height - self.height//6:
                self.Col["exit"] = True

        if pygame.mouse.get_pressed(3)[0] and pygame.mouse.get_pos()[1] >= self.height - self.height//6:
            self.Col["exit"] = False
            #get sellected tile position
            x, y = pygame.mouse.get_pos()
            nx, ny = (getTilePos((x, y), self.imageSize))
            additive = 0
            for i in range(nx):
                additive+=self.imageSize/4
            pos = nx, self.height - self.height//6
            x, y = nx*self.imageSize, self.height//6
            #divide to get tile index numbers
            nx = x/self.imageSize
            if nx%2 == 0:
                self.Col["state"] = "painting"
                data = list(self.Cdata.items())[int(nx//2)]
                self.Col["selected"] = data[0]


    def collisionPointer_change(self, screen):
        x, y = pygame.mouse.get_pos()
        nx, ny = (getTilePos((x, y), self.imageSize))
        additive = 0
        for i in range(nx):
            additive+=self.imageSize/4
        pos = nx, self.height - self.height//6
        pygame.draw.rect(screen, "white", pygame.Rect((pos[0]*self.imageSize, pos[1]), (self.imageSize, self.imageSize)), 2)

    def collisionPointer_paint(self, screen):
        x, y = pygame.mouse.get_pos()
        pos = (getTilePos((x, y), self.imageSize))
        pygame.draw.rect(screen, "white", pygame.Rect((pos[0]*self.imageSize, pos[1]*self.imageSize), (self.imageSize, self.imageSize)), 2)
        


    def Paint(self, screen, cam):
        mx, my = pygame.mouse.get_pos()
        # 1. Convert screen pos → world pos
        world_x = mx + cam.pos[0]
        world_y = my + cam.pos[1]
        # 2. Snap world pos → grid
        x, y = getTilePos((world_x, world_y), self.Tsize)
        # 3. Draw highlight (subtract camera for screen-space display)
        pygame.draw.rect(
            screen, "white",
            pygame.Rect(x*self.Tsize - cam.pos[0], y*self.Tsize - cam.pos[1], self.Tsize, self.Tsize),
            5
        )
        # 4. Place tile in world grid space
        if pygame.mouse.get_pressed(3)[0]:
            tiles = self.layers[self.currentLayer]
            tiles = [tile for tile in tiles if tile[1] != [x, y]]
            tiles.append([self.SelTileDict, [x, y]])
            self.layers[self.currentLayer] = tiles


    def Picking(self, screen):
        #display tileset / tile follow mouse
        screen.blit(self.image, (10, 10))
        x, y = pygame.mouse.get_pos()
        pos = getTilePos((int(x), int(y)), self.imageSize)   # (grid_x, grid_y)
        x = ((pos[0]) * self.imageSize)+10
        y = ((pos[1]) * self.imageSize)+10
        pygame.draw.rect(screen, "white", pygame.Rect((x, y), (self.imageSize, self.imageSize)), 2)
        #wait for selection
        X = int(pos[0])
        Y = int(pos[1])
        if pygame.mouse.get_pressed(3)[0] and X<self.fileDim[0] and Y<self.fileDim[1]:
            self.state = "paint"
            #get sellected tile
            self.selectedTile = self.images[str([X,Y])]
            self.SelTileDict = [X, Y]
        self.DF_DictPos(screen,pos[0], pos[1])

    def DF_DictPos(self, screen, x, y):
        DisplayText(str((x, y)), "green", 35, (self.width//2, self.height//2), screen)
        DisplayText(str(self.imageSize), "green", 35, (self.width//2, self.height//2-50), screen)

    def key_toggles(self, keys):
        #toggle
        if keys[pygame.K_TAB] and self.active:
            #pick tile
            self.state = "picking"
        if keys[pygame.K_ESCAPE] and self.state == "picking":
            self.state = "standby"
        elif keys[pygame.K_ESCAPE] and self.state == "paint":
            self.state = "picking"
        elif keys[pygame.K_c]:
            self.state = "collisionEditing"
        self.switchLayers(keys)

    def switchLayers(self, keys):
        if keys[pygame.K_SPACE] and not self.space_pressed_last:
            layer_names = list(self.layers.keys())
            idx = layer_names.index(self.currentLayer)
            self.currentLayer = layer_names[(idx + 1) % len(layer_names)]
        self.space_pressed_last = keys[pygame.K_SPACE]

    def resetStates(self):
        self.state = "standby"

    def basicUI(self, screen):
        # Panel size scales with window
        panel_w = int(self.width * 0.25)   # 25% of screen width
        panel_h = int(self.height * 0.2)   # 20% of screen height
        panel_x = self.width - panel_w
        panel_y = self.height - panel_h
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Draw background
        pygame.draw.rect(screen, (136, 148, 150), panel_rect)

        # Dynamic font sizes based on panel height
        title_size = max(20, panel_h // 6)   # min 20 to avoid being too small
        text_size  = max(15, panel_h // 8)

        margin = 20

        # Title
        DisplayText(self.Constdis["title"], self.Constdis["T_color"], title_size,
                    (panel_x + margin, panel_y + margin), screen)

        # State & Layer
        DisplayText(f"State: {self.state}", "white", text_size,
                    (panel_x + margin, panel_y + margin + text_size + 5), screen)

        DisplayText(f"Layer: {self.currentLayer}", "white", text_size,
                    (panel_x + margin, panel_y + margin + 2 * (text_size + 5)), screen)

        # Selected tile preview (anchored bottom-right inside panel)
        if self.state == "paint":
            tile_x = panel_x + panel_w - self.Tsize - margin
            tile_y = panel_y + panel_h - self.Tsize - margin
            screen.blit(self.selectedTile, (tile_x, tile_y))

