from settings import *
from support import *
from states.map import Map
from states.dialogue import Dialogue

class Game():
    def __init__(self):
        pg.init()
        
        pg.display.set_caption('Pymon')
        pg.display.set_icon(pg.image.load('window_icon.png'))
        self.screen = pg.display.set_mode(SCALED_SCREEN_SIZE)
        self.game_canvas = pg.Surface(PRESCALED_SCREEN_SIZE)

        self.clock = pg.time.Clock()
        self.running = True
        
        #GAME FLAGS
        #These are used for keeping track of dialogue and events
        self.flags = {
            'default': True
        }

        #INPUTS
        self.events = {
            "left": False,
            "right": False,
            "up": False,  
            "down": False,
            "confirm": False,
            "cancel": False
        }

        #STATES
        self.state_stack = []
        self.load_states()
        

    def load_states(self):
        self.map_state = Map(self, 'test')
        self.state_stack.append(self.map_state)

    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.events["up"] = True
                if event.key == pg.K_s:
                    self.events["down"] = True
                if event.key == pg.K_a:
                    self.events["left"] = True
                if event.key == pg.K_d:
                    self.events["right"] = True
                if event.key == pg.K_SPACE:
                    self.events["confirm"] = True
                if event.key == pg.K_ESCAPE:
                    self.events["cancel"] = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    self.events["up"] = False
                if event.key == pg.K_s:
                    self.events["down"] = False
                if event.key == pg.K_a:
                    self.events["left"] = False
                if event.key == pg.K_d:
                    self.events["right"] = False
                if event.key == pg.K_SPACE:
                    self.events["confirm"] = False
                if event.key == pg.K_ESCAPE:
                    self.events["cancel"] = False

    def reset_events(self):
        for event in self.events:
            self.events[event] = False

    def update(self, dt):
        self.state_stack[-1].update(dt, self.events)

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pg.transform.scale(self.game_canvas, self.screen.size), (0, 0))
        pg.display.flip()

    def run(self):
        while self.running:

            dt = self.clock.tick(60) / 1000

            pg.display.set_caption(f'Pymon - FPS: {int(self.clock.get_fps())}')

            self.get_events()
            self.update(dt)
            self.render()
            
    pg.quit()

if __name__ == '__main__':
    game = Game()
    while game.running:
        game.run()