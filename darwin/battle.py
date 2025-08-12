import random

class Battle:
    def __init__(
        self,
        individuals,
        hp_multiplier=10,
        damage_weight=1.0,
        dodge_weight=0.5,
        crit_weight=0.5,
        escape_speed_weight=0.5,
        escape_charisma_weight=0.5,
        persuade_charisma_weight=0.7,
        persuade_wisdom_weight=0.3
    ):
        self.individuals = individuals
        self.hp_multiplier = hp_multiplier
        self.damage_weight = damage_weight
        self.dodge_weight = dodge_weight
        self.crit_weight = crit_weight
        self.escape_speed_weight = escape_speed_weight
        self.escape_charisma_weight = escape_charisma_weight
        self.persuade_charisma_weight = persuade_charisma_weight
        self.persuade_wisdom_weight = persuade_wisdom_weight
        for ind in self.individuals:
            if not hasattr(ind, 'hp'):
                ind.hp = ind.ovr * self.hp_multiplier

    def attempt_escape(self, attacker, defender):
        chance_escape = (
            defender.speed * self.escape_speed_weight +
            defender.charisma * self.escape_charisma_weight
        ) / 10
        return random.random() < chance_escape

    def attempt_persuade(self, persuader, target):
        chance_persuade = (
            persuader.charisma * self.persuade_charisma_weight +
            persuader.wisdom * self.persuade_wisdom_weight
        ) / 10
        return random.random() < chance_persuade

    def calculate_damage(self, attacker, defender):
        base_damage = attacker.strength * self.damage_weight
        dodge_chance = (
            defender.smart * self.dodge_weight +
            defender.luck * self.dodge_weight
        ) / 10
        if random.random() < dodge_chance:
            return base_damage * 0.5
        crit_chance = attacker.luck * self.crit_weight / 10
        if random.random() < crit_chance:
            return base_damage * 2
        return base_damage

    def run_turn(self):
        self.individuals.sort(key=lambda ind: ind.speed, reverse=True)
        for attacker in self.individuals[:]:
            if len(self.individuals) <= 1:
                break
            targets = [ind for ind in self.individuals if ind != attacker]
            target = random.choice(targets)
            if self.attempt_persuade(attacker, target):
                self.individuals.remove(target)
                continue
            if self.attempt_escape(attacker, target):
                self.individuals.remove(target)
                continue
            damage = self.calculate_damage(attacker, target)
            target.hp -= damage
            if target.hp <= 0:
                attacker.kills += 1
                print(f'{attacker.name} matou {target.name} {attacker.kills}')
                self.individuals.remove(target)

    def fight(self):
        while len(self.individuals) > 1:
            self.run_turn()
