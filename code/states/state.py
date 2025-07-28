from settings import *

class State():
    def __init__(self, game):
        self.game = game
        self.previous_state = None

    def update(self, dt, events):
        pass

    def render(self, surface):
        pass

    def enter_state(self):
        self.game.state_stack.append(self)
        if len(self.game.state_stack) > 1:
            self.previous_state = self.game.state_stack[-2]

    def exit_state(self):
        self.game.state_stack.pop()