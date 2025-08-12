import random
from darwin.battle import Battle

class Social:
    def __init__(self, individuals, bounds, less):
        self.individuals = individuals
        self.bounds = bounds
        self.less = less

    def clamp(self, value):
        return max(self.bounds[0], min(self.bounds[1], value))

    def sleep(self, individual):
        recovery = random.uniform(1, 5)
        if not hasattr(individual, 'hp'):
            individual.hp = individual.ovr * 10
        individual.hp = min(individual.hp + recovery, individual.ovr * 10)

    def walk(self, individual):
        change = random.uniform(-0.1, 0.1)
        individual.speed = self.clamp(individual.speed + change)

    def talk(self, ind1, ind2):
        charisma_boost = random.uniform(0, 0.5)
        ind1.charisma = self.clamp(ind1.charisma + charisma_boost)
        ind2.charisma = self.clamp(ind2.charisma + charisma_boost)

    def battle(self, participants):
        battle = Battle(participants)
        battle.fight()

    def train_strength(self, individual):
        increase = random.uniform(0.1, 0.5)
        individual.strength = self.clamp(individual.strength + increase)
        individual.hp = max(individual.hp - 1, 0)  # esforço diminui HP levemente

    def read(self, individual):
        increase = random.uniform(0.1, 0.4)
        individual.smart = self.clamp(individual.smart + increase)

    def exercise(self, individual):
        spd_increase = random.uniform(0.1, 0.3)
        dex_increase = random.uniform(0.1, 0.3)
        individual.speed = self.clamp(individual.speed + spd_increase)
        individual.dexterity = self.clamp(individual.dexterity + dex_increase)
        individual.hp = max(individual.hp - random.uniform(0.5, 2), 0)

    def flirt(self, ind1, ind2):
        charm_increase = random.uniform(0.1, 0.6)
        beauty_increase = random.uniform(0.1, 0.4)
        ind1.charisma = self.clamp(ind1.charisma + charm_increase)
        ind2.charisma = self.clamp(ind2.charisma + charm_increase)
        ind1.beauty = self.clamp(ind1.beauty + beauty_increase)
        ind2.beauty = self.clamp(ind2.beauty + beauty_increase)

    def meditate(self, individual):
        hp_recovery = random.uniform(1, 4)
        wisdom_increase = random.uniform(0.1, 0.5)
        individual.hp = min(individual.hp + hp_recovery, individual.ovr * 10)
        individual.wisdom = self.clamp(individual.wisdom + wisdom_increase)

    def argue(self, ind1, ind2):
        charisma_loss = random.uniform(0.1, 0.4)
        temper_increase = random.uniform(0.2, 0.6)
        luck_gain = random.uniform(0, 0.3)

        ind1.charisma = self.clamp(ind1.charisma - charisma_loss)
        ind2.charisma = self.clamp(ind2.charisma - charisma_loss)

        for ind in (ind1, ind2):
            if not hasattr(ind, 'temper'):
                ind.temper = 0
            ind.temper = min(ind.temper + temper_increase, 1.0)
            ind.luck = self.clamp(ind.luck + luck_gain)

    def rest(self, individual):
        hp_recovery = random.uniform(0.5, 2)
        temper_reduction = random.uniform(0.1, 0.3)

        individual.hp = min(individual.hp + hp_recovery, individual.ovr * 10)
        if hasattr(individual, 'temper'):
            individual.temper = max(individual.temper - temper_reduction, 0)

    def choose_action(self, individual):
        if not hasattr(individual, 'temper'):
            individual.temper = random.uniform(0, 1)

        # Ajusta probabilidade de ação baseada no temperamento
        if individual.temper > 0.8:
            return random.choice(['battle', 'argue'])
        elif individual.temper > 0.5:
            return random.choice(['train_strength', 'exercise', 'flirt', 'talk'])
        elif individual.temper > 0.2:
            return random.choice(['walk', 'read', 'meditate', 'rest'])
        else:
            return random.choice(['sleep', 'walk', 'rest'])

    def perform_action(self, individual):
        action = self.choose_action(individual)

        if action == 'sleep':
            self.sleep(individual)
        elif action == 'walk':
            self.walk(individual)
        elif action == 'talk':
            partner = random.choice([ind for ind in self.individuals if ind != individual])
            self.talk(individual, partner)
        elif action == 'battle':
            opponents = [ind for ind in self.individuals if ind != individual]
            if opponents:
                participants = [individual, random.choice(opponents)]
                self.battle(participants)
        elif action == 'train_strength':
            self.train_strength(individual)
        elif action == 'read':
            self.read(individual)
        elif action == 'exercise':
            self.exercise(individual)
        elif action == 'flirt':
            partner = random.choice([ind for ind in self.individuals if ind != individual])
            self.flirt(individual, partner)
        elif action == 'meditate':
            self.meditate(individual)
        elif action == 'argue':
            partner = random.choice([ind for ind in self.individuals if ind != individual])
            self.argue(individual, partner)
        elif action == 'rest':
            self.rest(individual)
