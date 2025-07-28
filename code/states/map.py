from settings import *
import pytmx
from pytmx import TiledMap, TiledObject
from typing import List
from entities import *
from sprites import *
from tiles import *
from states.state import State
from states.dialogue import Dialogue
from states.battle import Battle
from random import random

class Map(State):
    def __init__(self, game, map_name: str):
        super().__init__(game)
        self.width = 0
        self.height = 0
        
        self.game = game

        #Data path
        self.path = ''

        #Map Logic Array
        self.tile_array: List[List[Tile]] = []
        
        #Camera Offset
        self.offset_x = 0
        self.offset_y = 0
        
        #VISIBLE MAP LAYERS
        #Static Layers. Front always on top, back always below player
        self.static_layers = {
            'Back': None,
            'Front': None,
        }
        
        #Dynamic layer updates every frame, is y sorted
        self.dynamic_layer = pg.sprite.Group()

        #A list of tiles which need to run an update function ever frame
        self.update_tiles: List[UpdateTile] = []
        
        #Player
        self.player =  Player(pos_x = 0, pos_y = 0, groups = self.dynamic_layer, sprite_folder = 'player')
        
        self.load_map(map_name)

    def update(self, dt, events):

        #Pass input events to player
        self.player.handle_input(events)

        #Check if player is attempting to interact with an entity
        if self.player.interact_target:
            target_entity = self.tile_array[self.player.interact_target[0]][self.player.interact_target[1]].entity
            if target_entity:
                if target_entity.dialogue:
                    dialogue_state = Dialogue(self.game, target_entity.dialogue)
                    dialogue_state.enter_state()     
            self.player.interact_target = None
        
        #MOVE PLAYER AND CHECK FOR ENCOUNTER
        if self.update_entity_position(self.player) and self.tile_array[self.player.pos_x][self.player.pos_y].encounter_chance > 0:
            if random() <= self.tile_array[self.player.pos_x][self.player.pos_y].encounter_chance:
                #battle_state = Battle(self.game, "", "")
                #battle_state.enter_state()
                pass
        self.player.update(dt)

        #Update all non player entities
        for entity in self.entities:
            entity.update(dt)
            self.update_entity_position(entity)

        for tile in self.update_tiles:
            tile.update(dt)

    def render(self, surface):
        #Camera Offset clamped to Map Boundary
        self.offset_x = -self.player.sprite.rect.centerx + PRESCALED_SCREEN_SIZE[0] / 2
        self.offset_x = int(pg.math.clamp(self.offset_x, -(self.width * TILE_SIZE) + PRESCALED_SCREEN_SIZE[0], 0))
        self.offset_y = -self.player.sprite.rect.centery + PRESCALED_SCREEN_SIZE[1] / 2
        self.offset_y = int(pg.math.clamp(self.offset_y , -(self.height * TILE_SIZE) + PRESCALED_SCREEN_SIZE[1], 0))
        
        draw_surface = pg.surface.Surface(PRESCALED_SCREEN_SIZE)
        
        #Fill with Water Colour
        draw_surface.fill((79, 103, 181))
        
        #Draw back first, it is always below everything
        draw_surface.blit(self.static_layers['Back'], (self.offset_x, self.offset_y))
        
        #Cull dynamic layer, only blit sprites on screen
        culled_dynamic_layer = self.get_culled_dynamic_layer()
        
        #Y Sort Culled Dynamic layer
        culled_dynamic_layer.sort(key=lambda sprite: sprite.rect.centery)
        
        #Render Culled Dynamic Layer
        for sprite in culled_dynamic_layer:
                draw_surface.blit(sprite.image, (sprite.rect.x + self.offset_x, sprite.rect.y + self.offset_y))
        
        #Draw Front last, it is always on top of everything
        draw_surface.blit(self.static_layers['Front'], (self.offset_x, self.offset_y))
                 
        surface.blit(draw_surface, (0, 0))

    def update_entity_position(self, entity: Entity) -> bool:
        #Remove entity from last tile and add it to new tile if the tile is walkable and inside map boundary
        #Return true if entity moved
        if ((entity.target_pos_x != entity.pos_x or entity.target_pos_y != entity.pos_y) 
        and entity.target_pos_x < self.width and entity.target_pos_x >= 0
        and entity.target_pos_y < self.height and entity.target_pos_y >= 0
        and self.tile_array[entity.target_pos_x][entity.target_pos_y].walkable):
            self.tile_array[entity.pos_x][entity.pos_y].on_exit()
            self.tile_array[entity.target_pos_x][entity.target_pos_y].on_entered(entity)
            entity.move()
            return True
        return False

    def load_map(self, map_name, player_pos_x = 15, player_pos_y = 8):
        
        #Reset Map
        self.path = join('data', 'maps', map_name)
        tmxdata: TiledMap = pytmx.load_pygame(join(self.path, f'{map_name}.tmx'))
        self.width = tmxdata.width
        self.height = tmxdata.height

        #encounter properties
        self.encounter_chance = 0.1
        self.encounter_min_level = tmxdata.properties.get('encounter_min_level')
        self.encounter_max_level = tmxdata.properties.get('encounter_max_level')
        self.encounters = ['gigadeer']
         
        #Load Tall Grass Surfaces
        self.tall_grass_frames_front = import_folder('gfx', 'entities', 'grass', tmxdata.properties['tall_grass_type'], 'front')
        self.tall_grass_frames_back = import_folder('gfx', 'entities', 'grass', tmxdata.properties['tall_grass_type'], 'back')
        
        #Reset Dynamic Layer
        self.dynamic_layer.empty()
        self.dynamic_layer.add(self.player.sprite)

        #Reset Update Tiles
        self.update_tiles.clear()
        
        #Reset Entities
        self.entities = []
        
        #Update Player
        self.player.pos_x = player_pos_x
        self.player.pos_y = player_pos_y
        self.player.snap_to_position()
        
        self.create_tile_array(tmxdata)
        self.create_static_layers(tmxdata)
        
        self.create_encounter_tiles(tmxdata)
        self.create_update_tiles(tmxdata)
        self.create_entities(tmxdata)
        
        #Place entities in Tiles
        for entity in self.entities:
            self.tile_array[entity.pos_x][entity.pos_y].entity = entity

    def create_tile_array(self, tmxdata: TiledMap):
        self.tile_array = []
        for x in range(self.width):
            #Create columns in map array
            self.tile_array.append([])
            for y in range(self.height):
                #Create Tile at X, Y
                self.tile_array[x].append(Tile())
                
        #Update Tiles in Map Array according to map TMX
        for layer_index in tmxdata.visible_tile_layers:
            for x in range(self.width):    
                for y in range(self.height): 
                    properties = tmxdata.get_tile_properties(x, y , layer_index)
                    if properties:
                        #Only set if false, so higher layers dont overwrite
                        if 'walkable' in properties.keys() and properties['walkable'] == False:
                            self.tile_array[x][y].walkable = properties['walkable']

    def create_static_layers(self, tmxdata):
        #Back and middle end up on the same surface as the player is either above or can not stand on things in either
        layer_surface = pg.surface.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE), pg.SRCALPHA)
        for x, y, image in tmxdata.get_layer_by_name('Back').tiles():
            layer_surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
        self.static_layers['Back'] = layer_surface
        for x, y, image in tmxdata.get_layer_by_name('Middle').tiles():
            layer_surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
        self.static_layers['Back'] = layer_surface
    
        #This layer exists always on top of the player
        layer_surface = pg.surface.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE), pg.SRCALPHA)
        for x, y, image in tmxdata.get_layer_by_name('Front').tiles():
            layer_surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
        self.static_layers['Front'] = layer_surface

    def create_encounter_tiles(self, tmxdata: TiledMap):
         print('Creating encounter tiles')
         for encounter_tile in tmxdata.get_layer_by_name('Encounter Tiles'):
            encounter_tile: TiledObject = encounter_tile
            encounter_tile_x = int(encounter_tile.x / TILE_SIZE)
            encounter_tile_y = int(encounter_tile.y / TILE_SIZE)

            if encounter_tile.type == 'TallGrass':
                for x in range(encounter_tile_x, encounter_tile_x + int(encounter_tile.width / TILE_SIZE), 1):
                    for y in range(encounter_tile_y, encounter_tile_y + int(encounter_tile.height / TILE_SIZE), 1):
                        self.tile_array[x][y] = TallGrassTile([TallGrassSprite(x, y, self.dynamic_layer, self.tall_grass_frames_front), TallGrassSprite(x, y, self.dynamic_layer, self.tall_grass_frames_back)], encounter_chance = self.encounter_chance)       

    def create_update_tiles(self, tmxdata: TiledMap):
        print('Creating update tiles')
        for update_tile in tmxdata.get_layer_by_name('Update Tiles'):
            update_tile: TiledObject = update_tile
            update_tile_x = int(update_tile.x / TILE_SIZE)
            update_tile_y = int(update_tile.y / TILE_SIZE)
                        
            if update_tile.type == 'TeleportTile':
                properties = update_tile.properties
                self.tile_array[update_tile_x][update_tile_y] = TeleportTile(
                    properties['target_map'],
                    properties['target_x'],
                    properties['target_y'],
                    self,
                    self.tile_array[update_tile_x][update_tile_y].walkable,
                    self.tile_array[update_tile_x][update_tile_y].entity
                    )
                
                #Add to dynamic tiles so it runs its update function
                self.update_tiles.append(self.tile_array[update_tile_x][update_tile_y])

    def create_entities(self, tmxdata: TiledMap):
        entities_data = []
        for folder_path, _, file_names in walk(join(self.path, 'entities')):
            for file_name in file_names:
                with open(join(folder_path, file_name)) as entity_data_file:
                    entities_data.append(json.load(entity_data_file))
        
        for entity_data in entities_data:
            if entity_data['type'] == 'npc':
                npc = NPC(
                    pos_x = entity_data['position']['x'],
                    pos_y = entity_data['position']['y'],
                    groups= self.dynamic_layer,
                    sprite_folder = entity_data['sprite_path'],
                    patrol_path = entity_data['patrol_path'],
                    dialogue=entity_data['dialogue'],
                    facing= entity_data['facing'],
                )
            self.tile_array[npc.pos_x][npc.pos_y].entity = npc
            self.entities.append(npc)

    def get_culled_dynamic_layer(self):
        culled_dynamic_sprites = []
        for sprite in self.dynamic_layer.sprites():
            if (sprite.rect.right > -self.offset_x and
                sprite.rect.left < -self.offset_x + PRESCALED_SCREEN_SIZE[0] and
                sprite.rect.bottom > -self.offset_y and 
                sprite.rect.top < -self.offset_y + PRESCALED_SCREEN_SIZE[1]
                ):
                culled_dynamic_sprites.append(sprite)  
        return culled_dynamic_sprites