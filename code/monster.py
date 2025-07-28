class Monster():
    def __init__(self, name, health, attack, defense, experience, abilities):
        self.name = name
        self.health = health
        self.experience = experience
        self.attack = attack
        self.defense = defense
        self.abilities = abilities


    def is_alive(self):
        return self.health > 0