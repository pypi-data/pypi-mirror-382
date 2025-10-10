"""
GameBox - A beginner-friendly Python 2D game development library.
--------------------------------------------------------------
GameBox makes it easy to build 2D games with graphics, sound, and UI in just a few lines of code.
"""


__version__ = "0.0.3"
__author__ = "Sam Fertig"

#____imports____
from .game import Game
from .basics.camera import Camera
from .basics.shapes import Rect, Text
from .basics.player import Player, Animation
from .tilemap.tilemap import Tilemap
from .inputs.BasicInput import Input
from .sound.BasicSound import Sound
from .basics.Functions import State_conditions
from .entities.basicTypes import Static_enemy, Dynamic_enemy


__all__ = [
    "Game",
    "Camera",
    "Rect",
    "Player",
    "Tilemap",
    "Input",
    "Sound",
    "Text",
    "Animation",
    "State_conditions",
    "Static_enemy",
    "Dynamic_enemy",
]

