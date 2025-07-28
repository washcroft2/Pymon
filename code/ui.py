from settings import *
from support import *

class Box(pg.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)


class DialogueBox(pg.sprite.Sprite):
    def __init__(self, groups, text = "This is a test dialogue box for testing the dialogue box.", choices = ['Yes', 'No']):
        super().__init__(groups)
          
        #Settings
        self.width = 300
        self.height = 60
        
        self.fill_colour = (10, 10, 15, 200)
        self.border_colour = (72, 74, 119, 255)
        self.dec_colour = (255, 255, 255)
        
        self.border_radius = 3
        self.border_margin = 2
        self.deco_line_gap = 6
        self.margin_bottom = 5
        
        #FONT
        self.text = text
        self.font = pg.font.Font(join('gfx', 'fonts', 'monogram.ttf'), 16)
        self.font_margin = 8
        self.font_margin = self.font_margin + self.border_margin
        
        #Surface and Rect
        self.image = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        self.rect = self.image.get_rect(midbottom = (PRESCALED_SCREEN_SIZE[0] / 2, PRESCALED_SCREEN_SIZE[1] - self.margin_bottom))
        self.deco_image = import_image('gfx', 'ui', 'corner_decoration').convert_alpha()
        
        #Draw Fill
        pg.draw.rect(self.image, self.fill_colour, pg.Rect((0,0), (self.width, self.height)), border_radius = self.border_radius)
 
        #Draw Border
        pg.draw.rect(self.image, self.border_colour, pg.Rect((0,0), (self.width, self.height)), int(self.border_margin + self.deco_image.height / 2) + 1, self.border_radius)
                
        #Draw Corner Decorations
        self.image.blit(self.deco_image, (0 + self.border_margin, 0 + self.border_margin))
        self.image.blit(self.deco_image, (self.width - self.border_margin - self.deco_image.width, 0 + self.border_margin))
        self.image.blit(self.deco_image, (0 + self.border_margin, self.height - self.border_margin - self.deco_image.height))
        self.image.blit(self.deco_image, (self.width - self.border_margin -self.deco_image.width,  self.height - self.border_margin - self.deco_image.height))

        #Draw Border lines
        #LEFT  
        pg.draw.line(
            self.image, self.dec_colour, 
            (0 + self.border_margin + self.deco_image.width / 2, 0 + self.border_margin + self.deco_image.height + self.deco_line_gap),
            (0 + self.border_margin + self.deco_image.width / 2, self.rect.height - self.border_margin - self.deco_image.height - self.deco_line_gap - 1)
            )
        
        #RIGHT  
        pg.draw.line(
            self.image, self.dec_colour, 
            (self.rect.width - self.border_margin - self.deco_image.width / 2, 0 + self.border_margin + self.deco_image.height + self.deco_line_gap),
            (self.rect.width - self.border_margin - self.deco_image.width / 2, self.rect.height - self.border_margin - self.deco_image.height - self.deco_line_gap - 1)
            )
        
        #TOP
        pg.draw.line(
            self.image, self.dec_colour, 
            (0 + self.border_margin + self.deco_image.width + self.deco_line_gap, 0 + self.border_margin + self.deco_image.height / 2),
            (self.rect.width - self.border_margin - self.deco_image.width - self.deco_line_gap - 1, 0 + self.border_margin + self.deco_image.height / 2)
            )
        
        #BOTTOM
        pg.draw.line(
            self.image, self.dec_colour, 
            (0 + self.border_margin + self.deco_image.width + self.deco_line_gap, self.rect.height - self.border_margin - self.deco_image.height / 2),
            (self.rect.width - self.border_margin - self.deco_image.width - self.deco_line_gap - 1, self.rect.height - self.border_margin - self.deco_image.height / 2)
            )
        
        
        font_surface = self.font.render(self.text, False, self.dec_colour, wraplength = self.width - self.font_margin)
        self.image.blit(font_surface, (self.font_margin, self.font_margin))
        
        if len(choices) > 1:
            self.choice_box = DialogueChoiceBox(groups, self, choices)
        else:
            self.choice_box = None
        
class DialogueChoiceBox(pg.sprite.Sprite):
    def __init__(self, groups, dialogue_box: DialogueBox, choices = []):
        super().__init__(groups)

        self.dialogue_box = dialogue_box

        #Settings
        self.choices = ['Yes', 'No',]
        self.selector_image = import_image('gfx', 'ui', 'selector').convert_alpha()
        
        self.border_radius = 3
        self.border_margin = 4
        
        self.height = dialogue_box.font.get_height() * len(self.choices) + self.border_margin * 2
        self.width = 45
        
        #Surface and Rect
        self.image = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        
        #Draw Fill
        pg.draw.rect(self.image, dialogue_box.fill_colour, pg.Rect((0,0), (self.width, self.height)), border_radius = self.border_radius)
 
        #Draw Border
        pg.draw.rect(self.image, dialogue_box.border_colour, pg.Rect((0,0), (self.width, self.height)), self.border_margin, self.border_radius)
        
        #Draw Inner Border
        pg.draw.rect(self.image, dialogue_box.dec_colour, pg.Rect((self.border_radius, self.border_radius), (self.width - self.border_radius * 2, self.height - self.border_radius * 2)), 1, self.border_radius)       
         
        self.selected_choice = 0
        self.text_margin_x = 4
        self.background_image = self.image.copy()
        self.update_choice()

    def update_choice(self):
        choice_index = 0

        #clear the image
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.background_image)

        for choice in self.choices:
            if self.selected_choice == choice_index:
                self.image.blit(self.selector_image, (self.border_margin + self.text_margin_x, choice_index * self.dialogue_box.font.get_height() + self.border_margin + self.selector_image.height / 2))
            font_surface = self.dialogue_box.font.render(choice, False, self.dialogue_box.dec_colour)
            self.image.blit(font_surface, (self.image.width - font_surface.width - self.border_margin - self.text_margin_x, choice_index * self.dialogue_box.font.get_height() + self.border_margin - 1))
            choice_index += 1
            
        self.rect = self.image.get_rect(bottomright = (self.dialogue_box.rect.topright[0], self.dialogue_box.rect.topright[1] - self.dialogue_box.margin_bottom))