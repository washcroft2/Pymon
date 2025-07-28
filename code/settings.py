import pygame as pg
from os import walk
from os.path import join
from enum import IntEnum
import json

TILE_SIZE: int = 16
SCALED_SCREEN_SIZE = (640, 480)
PRESCALED_SCREEN_SIZE = (320, 240)
ANIMATION_SPEED = 6