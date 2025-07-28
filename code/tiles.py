from settings import *
from entities import Player, Entity

class Tile():
    def __init__(self, walkable: bool = True, entity = None, encounter_chance = 0.0):
        self.walkable = walkable
        self.entity = entity
        self.encounter_chance = encounter_chance

    def on_entered(self, entity):
        self.entity = entity
        self.walkable = False
        self.on_entered_action()

    def on_exit(self):
        self.walkable = True
        self.entity = None
        self.on_exit_action()

    def on_entered_action(self):
        pass

    def on_exit_action(self):
        pass

class TallGrassTile(Tile):
    def __init__(self, animated_sprites, walkable: bool = True, entity: Entity = None, encounter_chance = 0.1):
        super().__init__(walkable, entity, encounter_chance)
        self.animated_sprites = animated_sprites

    def on_entered_action(self):
        for animated_sprite in self.animated_sprites:
            animated_sprite.entered()

    def on_exit_action(self):
        for animated_sprite in self.animated_sprites:
            animated_sprite.exited()

class UpdateTile(Tile):
    def __init__(self, walkable: bool = True, entity = None):
        super().__init__(walkable, entity)
        
    def update(self, dt):
        pass       

class TeleportTile(UpdateTile):
    def __init__(self, target_map, target_x, target_y, map, walkable: bool = True, entity = None):
        super().__init__(walkable, entity)
        self.target_map = target_map
        self.target_x = target_x
        self.target_y = target_y
        self.map = map
        
    def on_entered_action(self):
        if isinstance(self.entity, Player):
            self.entity.accepting_input = False
        
    def update(self, dt):
        if self.entity == None:
            return
        if isinstance(self.entity, Player) and self.entity.render_pos_aligned():
            self.map.load_map(self.target_map, self.target_x, self.target_y)
            self.entity.accepting_input = True
            
            #Make character render at edge of map and walk in to map
            match self.entity.direction:
                case 'up':
                    self.entity.render_pos_y += TILE_SIZE
                case 'down':
                    self.entity.render_pos_y -= TILE_SIZE
                case 'left':
                    self.entity.render_pos_y += TILE_SIZE
                case 'right':
                    self.entity.render_pos_y -= TILE_SIZE