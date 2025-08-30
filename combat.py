import random
from exploding_dice import roll

class Monster:
    """ base Monster"""
    def __init__(self, nickname=None, hp=10):
        if nickname is None:
            self.name = self.__class__.__name__
        else:
            self.name = nickname
        self.original_hitpoints =  hp
        self.hitpoints = hp
        self.attack_value = 0    # attack roll = attack_dice + attack_value
        self.defense_value = 0
        self.damage_value = 0
        self.armor_value = 0
        self.attack_dice = "1d6"
        self.defense_dice = "1d6"
        self.damage_dice = "1d6"
        self.armor_dice = "1d6"
        self.chance_for_critical_hit = 0.01 # 1% chance for double damage
        self.victories = 0

    def health(self):
        return f"hp: {self.hitpoints}/{self.original_hitpoints}"

    def full_heal(self):
        self.hitpoints += self.original_hitpoints - self.hitpoints

    def stats(self):
        return f"{self.__dict__}"

class Orc(Monster):
    """strong, high attack and damage"""
    def __init__(self):
        super().__init__(hp=40)
        # overwrite values
        self.attack_value = 8
        self.defense_value = 2
        self.damage_value = 5
        self.armor_value = 3
        self.attack_dice = "2d6"
        self.damage_dice = "2d6"


class Human(Monster):
    """weaker than an orc, but fights with skill,
       using exploding dice and critical chance
    """
    def __init__(self):
        super().__init__(hp=13)
        self.attack_value = 4
        self.defense_value = 6
        self.damage_value = 0
        self.armor_value = 3
        self.attack_dice = "1D6"
        self.defense_dice = "1D6"
        self.damage_dice = "1D6"
        self.armor_dice = "1D6"
        self.chance_for_critical_hit = 0.15 # chance for double damage

def strike(a,b):
    attack_string = f'{a.attack_dice}{"+" if a.attack_value >0 else ""}{a.attack_value}'
    attack_roll = roll(attack_string)
    defense_string = f'{b.defense_dice}{"+" if b.defense_value >0 else ""}{b.defense_value}'
    defense_roll = roll(defense_string)
    damage_string =  f'{a.damage_dice}{"+" if a.damage_value >0 else ""}{a.damage_value}'
    damage_roll = roll(damage_string)
    armor_string = f'{b.armor_dice}{"+" if b.armor_value >0 else ""}{b.armor_value}'
    armor_roll = roll(armor_string)
    ## attack overcomes defense ?
    textlines = []
    if attack_roll[0] <= defense_roll[0]:
        textlines.append(f"{a.name} swings at {b.name} but {b.name} evades the attack ({attack_string}:{attack_roll[0]} vs. {defense_string}:{defense_roll[0]})")
        return textlines
    textlines.append(f"{a.name} hits {b.name} ({attack_string}:{attack_roll[0]} vs. {defense_string}:{defense_roll[0]})...")
    ## damage overcomes armor ?
    if damage_roll[0] <= armor_roll[0]:
        textlines.append(f"... but the damage is blocked by {b.name}'s armor ({damage_string}:{damage_roll[0]} vs. {armor_string}:{armor_roll[0]})")
        return textlines
    textlines.append(f"... and find a weak spot in {b.name}'s armor ({damage_string}:{damage_roll[0]} vs. {armor_string}:{armor_roll[0]})")
    ## critical hit ?
    if random.random() < a.chance_for_critical_hit:
        damage = (damage_roll[0] - armor_roll[0]) *2
        textlines.append(f"{a.name} scores a CRITICAL HIT for double damage! ({damage//2}x2={damage * 2})")
    else:
        damage = damage_roll[0] - armor_roll[0]
    textlines.append(f"{b.name} looses {damage} hp and has {b.hitpoints - damage} hp left")
    b.hitpoints -= damage
    if b.hitpoints < 0:
        textlines.append(f"{b.name} dies!")
    return textlines

def combat(a,b):
        lines = []
        lines.append(f"STRIKE: {a.name} ({a.health()}hp) vs. {b.name} ({b.health()}hp)")
        lines.extend(strike(a,b))
        if b.hitpoints > 0:
            lines.append(f"COUNTERSTRIKE: {b.name} strikes back")
            lines.extend(strike(b,a))
        return lines

def battle(a,b, verbose = True):
    combat_round = 0
    lines = []
    while (a.hitpoints > 0) and (b.hitpoints > 0):
        combat_round += 1
        lines.append(f"--- combat round {combat_round} ---")
        lines.extend(combat(a, b))
    if a.hitpoints > b.hitpoints:
        a.victories += 1
        lines.append(f"{a.name} wins")
    else:
        b.victories += 1
        lines.append(f"{b.name} wins")
    if verbose:
        for line in lines:
            print(line)
    # restore both
    adam.full_heal()
    bob.full_heal()


if __name__ == "__main__":
    adam = Orc()
    bob = Human()
    # start one battle with verbose = True
    # or start many battles with verbose = False
    # change the stats inside the Human/Orc class
    # to see the differences (make 1000 battles)
    for _ in range(1000):
        battle(adam, bob, verbose=False)
    print("Orc victories:", adam.victories)
    print("Human victories:", bob.victories)


