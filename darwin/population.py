from darwin.generate import Individual
from darwin.social import Social

class Population:
    def __init__(self, size, bounds, less):
        self.bounds = bounds
        self.less = less
        self.individuals = [self.create_individual(i) for i in range(size)]
        self.social = Social(self.individuals, bounds, less)

    def create_individual(self, idx):
        ind = Individual(self.bounds, self.less)
        ind.id = idx
        ind.build_name()
        ind.build_attributs()
        return ind

    def simulate_day(self):
        for ind in self.individuals[:]:
            self.social.perform_action(ind)
        self.individuals = [ind for ind in self.individuals if ind.hp > 0]
        self.social.individuals = self.individuals

    def get_population_stats(self):
        stats = {
            'names': [ind.name for ind in self.individuals],
            'hp': [ind.hp for ind in self.individuals],
            'strength': [ind.strength for ind in self.individuals],
            'speed': [ind.speed for ind in self.individuals],
            'luck': [ind.luck for ind in self.individuals],
            'smart': [ind.smart for ind in self.individuals],
            'dexterity': [ind.dexterity for ind in self.individuals],
            'wisdom': [ind.wisdom for ind in self.individuals],
            'charisma': [ind.charisma for ind in self.individuals],
            'beauty': [ind.beauty for ind in self.individuals],
            'overall': [ind.ovr for ind in self.individuals],
            'kills': [getattr(ind, 'kills', 0) for ind in self.individuals],  # Garante kills mesmo que não exista
        }
        return stats

