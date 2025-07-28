from settings import *
from states.state import State
from ui import DialogueBox

class Dialogue(State):
    def __init__(self, game, dialogue):
        super().__init__(game)
        self.game = game
        self.dialogue = dialogue
        self.dialogue_group = pg.sprite.Group()
        self.dialogue_index = 0

    def enter_state(self):
        super().enter_state()
        self.dialogue_box = DialogueBox(self.dialogue_group, self.dialogue['default'][self.dialogue_index]['text'], self.dialogue['default'][self.dialogue_index]['choices'])
        self.game.reset_events()

    def update(self, dt, events):

        if self.dialogue_box.choice_box:
            if events['up']:
                self.dialogue_box.choice_box.selected_choice = (self.dialogue_box.choice_box.selected_choice - 1) % len(self.dialogue_box.choice_box.choices)
                self.dialogue_box.choice_box.update_choice()

            if events['down']:
                self.dialogue_box.choice_box.selected_choice = (self.dialogue_box.choice_box.selected_choice + 1) % len(self.dialogue_box.choice_box.choices)
                self.dialogue_box.choice_box.update_choice()

        if events['confirm']:
            self.dialogue_index += 1
            self.dialogue_group.empty()
            if self.dialogue_index < len(self.dialogue['default']):
                self.dialogue_box = DialogueBox(self.dialogue_group, self.dialogue['default'][self.dialogue_index]['text'], self.dialogue['default'][self.dialogue_index]['choices'])
            else:
                self.exit_state()

        self.game.reset_events()

    def render(self, surface):
        self.previous_state.render(surface)
        self.dialogue_group.draw(surface)