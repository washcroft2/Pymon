from settings import *

class Sprite(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, groups):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(bottomleft = (pos_x * TILE_SIZE, pos_y * TILE_SIZE + TILE_SIZE))

class TallGrassSprite(Sprite):
    def __init__(self, pos_x: int, pos_y: int, groups, frames = []):
        self.frame_index = 0
        image = frames[self.frame_index]
        super().__init__(pos_x, pos_y, image, groups)
        self.frames = frames

    def entered(self):
        self.image = self.frames[1]

    def exited(self):
        self.image = self.frames[0]