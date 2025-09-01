import random
from exploding_dice import roll
class Item:

    number = 0
    items = {}

    def __init__(self, x=None, y=None, z=None, name=None):
        self.x, self.y, self.z = x, y, z
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name
        self.number = Item.number
        Item.number += 1
        Item.items[self.number] = self



class Weapon(Item):

    def __init__(self,
                 name=None,
                 x=None,
                 y=None,
                 z=None,
                 attack=1,
                 defense=1,
                 damage=1,
                 reach=0.5,
                 verbs=['swing'],
                 ):
        super().__init__(x,y,z,name)
        self.attack_bonus = attack
        self.defense_bonus = defense
        self.damage_bonus = damage
        self.reach = reach
        self.hands = 1
        self.verbs = verbs
        #self.chance_for_blocking = 0.3

class Armor(Item):

    def __init__(self,
                 name=None,
                 x=None,
                 y=None,
                 z=None,
                 defense=0,
                 attack=0,
                 mass=0.5, # kg
                 **kwargs, # for body slots, like head=5, body=11, ...
                 ):
        super().__init__(x, y, z, name)
        self.defense_bonus = defense
        self.attack_bonus = attack
        self.mass = mass
        self.parts = {} # body_slot : armor_value
        for key, value in kwargs.items():
            self.parts[key] = value



class Monster:
    """ base Monster"""
    def __init__(self, nickname=None, hp=10, **kwargs):
        if nickname is None:
            self.name = self.__class__.__name__
        else:
            self.name = nickname
        self.original_hitpoints =  hp
        self.hitpoints = hp
        # % chance to hit a specific body part in %
        self.body_slots = {"head": 0.1,
                           "body": 0.5,
                           "left arm": 0.09,
                           "right arm": 0.09,
                           "left hand": 0.01,
                           "right hand": 0.01,
                           "left leg":0.09,
                           "right leg":0.09,
                           "left foot":0.01,
                           "right foot":0.01,
                           }

        self.attack_value = 0    # attack roll = attack_dice + attack_value
        self.defense_value = 0
        self.damage_value = 0
        self.armor_value = 0
        self.morale_value = 0
        self.attack_dice = "1d6"
        self.defense_dice = "1d6"
        self.damage_dice = "1d6"
        self.armor_dice = "1d6"
        self.morale_dice = "1d6"
        self.chance_for_critical_hit = 0.01 # 1% chance for double damage
        self.victories = 0
        self.weapon = None
        self.armor = []
        self.natural_armor_name = "skin"
        # overwrite kwargs
        for k,v in kwargs.items():
            self.__setattr__(k,v)

    def health(self):
        return f"hp: {self.hitpoints}/{self.original_hitpoints}"

    def full_heal(self):
        self.hitpoints += self.original_hitpoints - self.hitpoints

    def stats(self):
        return f"{self.__dict__}"

    def check_sum_of_body_percentages(self):
        # sum of body part percentages should be 1.0
        return sum(self.body_slots.values())

    def sum_of_defense_values(self):
        # sums all defense boni/mali from armor and weapon
        total  = self.defense_value
        # add boni of wielded weapon
        total += self.weapon.defense_bonus
        # add boni/mali from all equipped armor pieces
        for a in self.armor:
            total += a.defense_bonus # or malus
        return total

    def attack_roll(self):
        string = f"{self.attack_dice}{self.attack_value+self.weapon.attack_bonus:+}"
        return roll(string)

    def defense_roll(self):
        string = f"{self.defense_dice}{self.sum_of_defense_values():+}" # :+ forces to add sign (positive and negative)
        return roll(string)

    def damage_roll(self):
        string = f"{self.damage_dice}{self.damage_value+self.weapon.damage_bonus:+}"
        return roll(string)

    def armor_roll(self, body_part):
        a, piece = self.local_armor(body_part) # this includes natural armor
        string = f"{self.armor_dice}{a:+}"
        return roll(string), piece

    def morale_roll(self):
        string = f"{self.morale_dice}{self.morale_value:+}"
        return roll(string)


    def local_armor(self, body_part) -> (int, str):
        """returns armor value and armor name for a specific body part"""
        for armor_item in self.armor:
            if body_part in armor_item.parts:
                return armor_item.parts[body_part], armor_item.name
        return self.armor_value, self.natural_armor_name

    def random_body_part(self):
        """choose one body part (usually to hit) by random"""
        # sum of percentages should be one
        r = random.random() # generate random number between 0 and 1
        #print("r:",r)
        total = 0
        for part, percentage in self.body_slots.items():
            total += percentage
            #print(part, "total", total, "percent", percentage)
            if total > r:
                return part
        raise ValueError("did not found part")




class Orc(Monster):
    """strong, high attack and damage"""
    def __init__(self, **kwargs):
        super().__init__(hp=40,
                         attack_dice="2d6",
                         damage_dice="2d6",
                         **kwargs)

class Human(Monster):
    """weaker than an orc, but fights with skill,
       using exploding dice and critical chance
    """
    def __init__(self, **kwargs):
        super().__init__(hp=13,
                         attack_dice="1D6",
                         defense_dice="1D6",
                         damage_dice="1D6",
                         armor_dice="1D6",
                         moral_dice="1D6",
                         chance_for_critical_hit = 0.15,
                         **kwargs)

def strike(a,b):
    """
    combat rules:
    a...attacker (an instance of (a child of) the Monster class)
    d...defender (an instance of (a child of) the Monster class)

    1.) calculate values for both attacker and defender:
    attack_roll
    defense_roll
    attacked_body_part
    armor_roll
    damage_roll



    do calculation:
    if attacker has shorter weapon than defender:
        REPEL action:
            attacker must defend against defenders attack.
            (so the defender attacks the attacker)
            if damage occurs, the damage is capped at  1hp and
            attacker must win a morale check to continue the attack



    calculation if attacker actually HIT something
    if a. attack <= d.defense:
            defender evades, the attack is canceled
    attacker hits defender !
    damage = a.damage - d.armor[of selected body part]
    if damage <= 0:
        attack can not penetrate armor, attack is canceled
    if attacker makes CRITICAL Damage:
        damage is doubled
    d.hitpoints -= damage
    """

    # the :+ sufficx inside and f-string variable forces
    # the sign, also for positive numbers (including 0)
    # see https://docs.python.org/3/library/string.html#format-specification-mini-language
    w_a = a.weapon
    weapon_a = w_a.name
    w_b = b.weapon
    weapon_b = w_b.name

    attack_roll_a = a.attack_roll()
    defense_roll_b = b.defense_roll()
    part_b = b.random_body_part()
    armor_roll_b, armor_piece = b.armor_roll(part_b)
    damage_roll_a = a.damage_roll()
    repel = False
    if b.weapon.reach > a.weapon.reach:
        repel = True
        repel_attack_roll = b.attack_roll()
        repel_defense_roll = a.defense_roll()
        repel_part = a.random_body_part()
        repel_armor_roll, repel_piece = a.armor_roll(repel_part)
        repel_damage_roll = b.damage_roll()
        repel_morale_roll = a.morale_roll()
        morale_roll = b.morale_roll()

    verb = random.choice(w_a.verbs)+"s"
    textlines = []
    ## repel action ?
    if repel:
        if repel_attack_roll[0] < repel_defense_roll[0]:
            textlines.append(f"{a.name} successfully attacks {b.name} with a shorter weapon ({w_a.name}:{w_a.reach} vs. {w_b.name}:{w_b.reach}): {repel_defense_roll[1]} vs. {repel_attack_roll[1]}")
        else:
            # repel damage?
            textlines.append(f"{a.name} attacks {b.name} with a shorter weapon ({w_a.name}:{w_a.reach} vs. {w_b.name}:{w_b.reach})")
            textlines.append(f"and gets hit by {b.name}'s {w_b.name} in the {repel_part} during the attack. {repel_defense_roll[1]} vs. {repel_attack_roll[1]}")
            if repel_damage_roll[0] <= repel_armor_roll[0]:
                textlines.append(f"but suffers no damage {repel_damage_roll[1]} vs. {repel_armor_roll[1]}")
            else:
                textlines.append(f"and looses 1 hp (capped)") # TODO: strange combat strings {repel_damage_roll[1]} vs. {repel_armor_roll[1]}")
                a.hitpoints -= 1
                if a.hitpoints <= 0:
                    #textlines.append(f"{a.name} dies during attacking")
                    return textlines
                # morale check
                if repel_morale_roll[0] <= morale_roll[0]:
                    textlines.append(f"{a.name}'s morale is not high enough and he cancels the attack ({repel_morale_roll[1]} vs. {morale_roll[1]})")
                    return textlines
                textlines.append("but continues with the attack!")
    # --- normal attack (after repel) ----
    ## attack overcomes defense ?
    if attack_roll_a[0] <= defense_roll_b[0]:
        textlines.append(f"{a.name} {verb} {weapon_a} at {b.name} but {b.name} evades the attack ({attack_roll_a[1]} vs. {defense_roll_b[1]})")
        return textlines
    textlines.append(f"{a.name} {verb} {weapon_a} and hits {part_b} of {b.name}! ({attack_roll_a[1]} vs. {defense_roll_b[1]})")
    ## damage overcomes armor ?
    if damage_roll_a[0] <= armor_roll_b[0]:
        textlines.append(f"... but the damage is blocked by {b.name}'s {armor_piece} ({damage_roll_a[1]} vs. {armor_roll_b[1]})")
        return textlines
    textlines.append(f"... and penetrates {b.name}'s {armor_piece} ({damage_roll_a[1]} vs. {armor_roll_b[1]})")
    ## critical hit ?
    if random.random() < a.chance_for_critical_hit:
        damage = (damage_roll_a[0] - armor_roll_b[0]) *2
        textlines.append(f"{a.name} scores a CRITICAL HIT for double damage! ({damage//2}x2={damage})")
    else:
        damage = damage_roll_a[0] - armor_roll_b[0]
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


#if __name__ == "__main__":
    #alice = Monster()


    #print(alice.check_sum_of_body_percentages())
    #for _ in range(100):
    #    print(alice.random_body_part())

if __name__ == "__main__":
    #adam = Orc()
    adam = Human(nickname="Adam")
    bob = Human(nickname="Bob")
    sword = Weapon("Sword", attack=3, defense=3, reach=0.7,
                   damage=5,
                   verbs=["swing","thrust"])
    spear = Weapon("Spear", attack=2, defense=4, reach=1.8,
                   damage = 3,
                   verbs=["poke", "thrust", "swing"])
    iron_helmet = Armor(name="iron helmet",head=5)
    leather_armor = Armor(name="leather armor",body=3,left_arm=3,right_arm=3,
                          left_leg=3, right_leg=3)
    leather_cap = Armor(name="leather cap",head=2)
    iron_boots = Armor(name="iron boot",left_feet=4,right_feet=4)
    iron_trousers = Armor(name="iron trousers",left_leg=4, right_leg=4)
    adam.weapon = sword
    bob.weapon = spear
    adam.armor = [iron_helmet, iron_boots, iron_trousers]
    bob.armor = [leather_cap, leather_armor]

    # start one battle with verbose = True
    # or start many battles with verbose = False
    # change the stats inside the Human/Orc class
    # to see the differences (make 1000 battles)
    for _ in range(1):
        battle(adam, bob, verbose=True)
    print("Adam victories:", adam.victories)
    print("Bob victories:", bob.victories)


