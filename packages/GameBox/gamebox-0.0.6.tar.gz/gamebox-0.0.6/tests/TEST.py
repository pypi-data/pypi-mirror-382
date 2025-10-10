import pygame
from src.GameBox import game
from src.GameBox.basics import camera, player
from src.GameBox.tilemap import tilemap
from src.GameBox.basics.Functions import State_conditions
from src.GameBox.entities.basicTypes import Static_enemy, Dynamic_enemy
from src.GameBox.entities.basicNPCs import Static_NPC

width, height = 1800, 1000
win = game.Game(width, height)
cam = camera.Camera(width, height, "dynamic")
image = pygame.image.load("tests\sprites\image.png")
cond = State_conditions()

player_obj = player.Player((500, 400), "tests\sprites\playerSprite.png", (64, 64), cam, 0.3)
animation = player.Animation(image, 32, (13, 3), 0.2, 39, 2, 0)
player_obj.Add_state("main", animation, cond.any)

ghost_image = pygame.image.load("tests\sprites\ghost.png")
ghost_animation = player.Animation(ghost_image, 16, (4, 1), 0.2, 4, 4, 0)

staticE = Static_enemy((0, 0), ghost_animation, cam, (64, 64))
dynamicE = Dynamic_enemy((64, 0), (256, 0), True, ghost_animation, cam, (64, 64), True, 35)

npc = Static_NPC((100, 500), ghost_animation, (64, 64), cam)

map = tilemap.Tilemap(32, (13, 3), image, cam, 2)
map.load_map("SavedMap.json")
map.enable_editor(width, height)

win.show_list([map, player_obj, staticE, dynamicE, npc])
win.update()

#player_obj.Add_collision(map.Get_collisions())

#loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            map.save_map("SavedMap.json")
            pygame.quit()
            quit()

    #player_obj.platformer_movement(5, 1.2, 23, 12)
    player_obj.move_by_WSAD(7)

    win.update()
