from states.state import State

class Battle(State):
    def __init__(self, game, player_party, enemy_party):
        super().__init__(game)
        self.game = game
        self.player_party = player_party
        self.enemy_party = enemy_party

    def enter_state(self):
        super().enter_state()
        self.game.reset_events()
        print("Entering Battle State")
    
    def update(self, dt, events):
        pass