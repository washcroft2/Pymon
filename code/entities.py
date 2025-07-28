from settings import *
from support import *
from sprites import Sprite
        
class Entity():
    def __init__(self, pos_x: int, pos_y: int):
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.target_pos_x = pos_x
        self.target_pos_y = pos_y
        
    def move(self):
        self.pos_x = self.target_pos_x
        self.pos_y = self.target_pos_y
    
    def interact(self):
        pass

    def update(self):
        pass
        
class Character(Entity):
    def __init__(self, pos_x, pos_y, groups, sprite_folder: str, facing = 'down'):
        super().__init__(pos_x, pos_y)

        #ANIMATION
        self.animation_frames = {
            'down': [],
            'left': [],
            'right': [],
            'up': [],
        }

        self.sprite_folder = sprite_folder
        self.import_animation_frames()
        self.facing = facing
        self.frame_index = 0
        self.animation_speed = 6
        
        self.sprite = Sprite(pos_x, pos_y, self.animation_frames[self.facing][0], groups)
        
        self.speed = 64

    def import_animation_frames(self):
        for key in self.animation_frames.keys():
            self.animation_frames[key] = import_folder('gfx', 'entities', self.sprite_folder, key)
        for frame in self.animation_frames['left']:
            self.animation_frames['right'].append(pg.transform.flip(frame, True, False))

    def slide_to_position(self, dt):       
        target_sprite_pos = (self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE + TILE_SIZE)

        if self.sprite.rect.bottomleft[0] < target_sprite_pos[0]:
            render_pos_x_step = self.sprite.rect.bottomleft[0] + self.speed * dt
            if render_pos_x_step < target_sprite_pos[0]:
                self.sprite.rect.update(self.sprite.rect.move(self.speed * dt, 0))
            else:
                self.sprite.rect.bottomleft = target_sprite_pos
            
        elif self.sprite.rect.bottomleft[0] > target_sprite_pos[0]:
            render_pos_x_step = self.sprite.rect.bottomleft[0] - self.speed * dt
            if render_pos_x_step > target_sprite_pos[0]:
                self.sprite.rect.update(self.sprite.rect.move(self.speed * dt * -1, 0))
            else:
                self.sprite.rect.bottomleft = target_sprite_pos
                
        elif self.sprite.rect.bottomleft[1] < target_sprite_pos[1]:
            render_pos_y_step = self.sprite.rect.bottomleft[1] + self.speed * dt
            if render_pos_y_step < target_sprite_pos[1]:
                self.sprite.rect.update(self.sprite.rect.move(0, self.speed * dt))
            else:
                self.sprite.rect.bottomleft = target_sprite_pos
            
        elif self.sprite.rect.bottomleft[1] > target_sprite_pos[1]:
            render_pos_y_step = self.sprite.rect.bottomleft[1] - self.speed * dt
            if render_pos_y_step > target_sprite_pos[1]:
                self.sprite.rect.update(self.sprite.rect.move(0, self.speed * dt * -1))
            else:
                self.sprite.rect.bottomleft = target_sprite_pos
    
    def render_pos_aligned(self) -> bool:
        return self.sprite.rect.bottomleft == (self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE + TILE_SIZE)

    def snap_to_position(self):
        self.sprite.rect.bottomleft = (self.pos_x * TILE_SIZE, self.pos_y * TILE_SIZE + TILE_SIZE)
        
    def animate(self, dt):
        if not self.render_pos_aligned():
            self.frame_index += self.animation_speed * dt
            self.sprite.image = self.animation_frames[self.facing][int(self.frame_index) % len(self.animation_frames[self.facing])]
            self.slide_to_position(dt)
        else:
            self.frame_index = 0
            self.sprite.image = self.animation_frames[self.facing][0]

    def update(self, dt):
        self.animate(dt)

class Player(Character):
    def __init__(self, pos_x, pos_y, groups, sprite_folder = 'player', facing = 'down'):
        super().__init__(pos_x, pos_y, groups, sprite_folder, facing)
        self.interact_target = None

    def handle_input(self, events):
        #reset move target
        self.target_pos_x = self.pos_x
        self.target_pos_y = self.pos_y
        
        #Checking if closer than 2 pixels to target position before allowing it to update to next target
        if abs(self.sprite.rect.bottomleft[1] - (self.pos_y * TILE_SIZE + TILE_SIZE)) < 2 and self.sprite.rect.bottomleft[0] == self.pos_x * TILE_SIZE: 
            if events['up']:
                self.target_pos_x = self.pos_x
                self.target_pos_y = self.pos_y - 1
                self.facing = 'up'
            if events['down']:
                self.target_pos_x = self.pos_x
                self.target_pos_y = self.pos_y + 1   
                self.facing = 'down'
        if abs(self.sprite.rect.bottomleft[0] - (self.pos_x * TILE_SIZE)) < 2 and self.sprite.rect.bottomleft[1] == self.pos_y * TILE_SIZE + TILE_SIZE:
            if events['left']:
                self.target_pos_y = self.pos_y
                self.target_pos_x = self.pos_x - 1
                self.facing = 'left'
            if events['right']:
                self.target_pos_y = self.pos_y
                self.target_pos_x = self.pos_x + 1
                self.facing = 'right'

        if events['confirm']:
            self.interact_target = (self.pos_x, self.pos_y)
            if self.facing == 'up':
                self.interact_target = (self.pos_x, self.pos_y - 1)
            elif self.facing == 'down':
                self.interact_target = (self.pos_x, self.pos_y + 1) 
            elif self.facing == 'left':
                self.interact_target = (self.pos_x - 1, self.pos_y)
            elif self.facing == 'right':
                self.interact_target = (self.pos_x + 1, self.pos_y)

class NPC(Character):
    def __init__(self, pos_x, pos_y, groups, sprite_folder, patrol_path = None, dialogue = None, facing = 'down'):
        super().__init__(pos_x, pos_y, groups, sprite_folder, facing)

        self.patrol_path = patrol_path
        self.patrol_path_index = 0

        self.dialogue = dialogue

    def patrol(self):
        if self.patrol_path:
            current_target = self.patrol_path[self.patrol_path_index]
            if current_target['x'] == self.pos_x and current_target['y'] == self.pos_y:
                self.patrol_path_index = (self.patrol_path_index + 1) % len(self.patrol_path)
            else:
                if abs(self.sprite.rect.bottomleft[1] - (self.pos_y * TILE_SIZE + TILE_SIZE)) < 2 and self.sprite.rect.bottomleft[0] == self.pos_x * TILE_SIZE:
                    self.target_pos_y = self.pos_y + int(max(min(self.pos_y - current_target['y'], 1), -1)) * -1                 
                if abs(self.sprite.rect.bottomleft[0] - (self.pos_x * TILE_SIZE)) < 2 and self.sprite.rect.bottomleft[1] == self.pos_y * TILE_SIZE + TILE_SIZE:
                    self.target_pos_x = self.pos_x + int(max(min(self.pos_x - current_target['x'], 1), -1)) * -1

        if self.target_pos_x > self.pos_x:
            self.facing = 'right'
        elif self.target_pos_x < self.pos_x:
            self.facing = 'left'
        elif self.target_pos_y > self.pos_y:
            self.facing = 'down'
        elif self.target_pos_y < self.pos_y:
            self.facing = 'up'

    def interact(self):
        print('Interacting with NPC:', self.dialogue['default'] if self.dialogue else 'No dialogue available.')

    def update(self, dt):
        self.patrol()
        super().update(dt)
