from random import choice
from darwin.randomizer import generate_normalized_number
from darwin.utility import mean

class Individual:
    def __init__(self, bounds, less):
        self.name = ''
        self.id = 0
        self.strength = 0
        self.speed = 0
        self.luck = 0
        self.smart = 0
        self.dexterity = 0
        self.wisdom = 0
        self.charisma = 0
        self.beauty = 0
        self.ovr = 0
        self.hp = 0
        self.kills = 0

        self.weight_hp = 100
        self.bounds = bounds
        self.less = less

    def build_name(self, length=6):
        vowels = list('aeiou')
        consonants = list('bcdfgjklmnpqrstv')
        name = []

        for _ in range(length // 2):
            name.append(choice(consonants))
            name.append(choice(vowels))
        
        self.name = ''.join(name).capitalize()
    
    def build_attributs(self):
        self.strength = generate_normalized_number(self.bounds, self.less)
        self.speed = generate_normalized_number(self.bounds, self.less)
        self.luck = generate_normalized_number(self.bounds, self.less)
        self.smart = generate_normalized_number(self.bounds, self.less)
        self.dexterity = generate_normalized_number(self.bounds, self.less)
        self.wisdom = generate_normalized_number(self.bounds, self.less)
        self.charisma = generate_normalized_number(self.bounds, self.less)
        self.beauty = generate_normalized_number(self.bounds, self.less)
        self.overall()
        self.hp = self.ovr * self.weight_hp

    def overall(self):
        self.ovr = mean([self.strength, self.speed, self.luck, self.smart, self.dexterity, self.wisdom, self.charisma, self.beauty])
