# Developed by Anton Melnychuk          March 1st 2024
# For ASTR 330 Class                    Yale University

# Imports
import math
import random
import Constants


class DNA:
    def __init__(self, **kwargs):
        self.data = {}

        for dna_field_name in Constants.fields:
            self.data[dna_field_name] = kwargs.get(dna_field_name, 0.5)

    def mutate(self) -> None:
        if random.random() < self.data['mutation_rate']:
            mutation_choice = random.choice(list(Constants.fields))

            shift = random.uniform(-0.02, 0.02)
            self.data[mutation_choice] += shift

    def generate_random(self) -> None:
        ''' Randomize DNA '''
        for dna_field_name in Constants.fields:
            self.data[dna_field_name] = random.uniform(0.2, 1)


class Life:
    check_occupied = None
    check_position = None
    private_func = None

    def __init__(self, family_idx):
        self.family_idx = family_idx
        self.color = Constants.BLACK

        self.direction = random.randint(1, 4)
        self.energy_level = 30
        self.dna = None

        self.age = 0
        self.lifelen = 20
    
    def execute(self) -> None:
        raise NotImplementedError
    
    # Grant Partial Parent Access

    @classmethod
    def set_private_function(cls, private_func):
        cls.private_func = private_func

    @classmethod
    def set_gridcheck_function(cls, check_occupied):
        cls.check_occupied = check_occupied

    @classmethod
    def set_gridpos_function(cls, check_position):
        cls.check_position = check_position


class Leaf(Life):
    def __init__(self, idx):
        super().__init__(idx)
        self.color = Constants.GREEN

    def execute(self):
        self.private_func()

class Root(Life):
    def __init__(self, idx):
        super().__init__(idx)
        self.color = Constants.BROWN
    
    def execute(self):
        self.private_func()

class Radio(Life):
    def __init__(self, idx):
        super().__init__(idx)
        self.color = Constants.BLUE
    
    def execute(self):
        self.private_func()

class Pipe(Life):
    def __init__(self, idx):
        super().__init__(idx)
        self.color = Constants.COLONIES_COLOR[self.family_idx]
    
    def execute(self):
        pass


class Newborn(Life):
    def __init__(self, idx, dna=None):
        super().__init__(idx)
        self.color = Constants.WHITE
        self.dna = dna

    def define_color(self) -> None:
        ''' On Board definition, Define Random Family Color '''

        Constants.COLONIES_COLOR[self.family_idx] = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

    def calc_life_prob(self) -> list:
        ''' Probailities of a Cetain Kind of Cell to be Born '''

        return [
            self.dna.data.get('leaf_rate', 0.5),
            self.dna.data.get('root_rate', 0.5),
            self.dna.data.get('radio_rate', 0.5),
            self.dna.data.get('newb_rate', 0.5)
        ]

    def create_life(self, new_cell, direction, energy_dist, idx, replace=False) -> None:
        ''' Propagates and Modifies Cell DNA and General Properties '''
        
        new_cell.energy_level = energy_dist
        new_cell.lifelen = math.exp(energy_dist) * 10
        new_cell.direction = direction
        new_cell.dna = self.dna
        new_cell.dna.mutate()

        if replace:
            direction = 0

        self.private_func(direction, new_cell, idx)

    def execute(self):
        curr_x, curr_y = self.check_position()
        left_dir = 4 if self.direction == 1 else self.direction - 1
        right_dir = 1 if self.direction == 4 else self.direction + 1

        # Options: Build LEFT, RIGHT, BOTH

        build_to = random.choices([1, 2, 3], [0.1, 0.1, 0.8])[0]

        CLASSES = [Leaf, Root, Radio, Newborn]
        probabilities = self.calc_life_prob()

        # How to split energy between new life cells

        if build_to == 3: energy_dist = self.energy_level / 2
        else:             energy_dist = self.energy_level

        # Build in possible directions given DNA props
        # We can build either LEFT, RIGHT, ot BOTH directions

        if not self.check_occupied(curr_x, curr_y, left_dir, self.family_idx):
            if build_to == 1 or build_to == 3:
                new_cell = random.choices(CLASSES, probabilities)[0](self.family_idx)
                self.create_life(new_cell, left_dir, energy_dist, self.family_idx)

        if not self.check_occupied(curr_x, curr_y, right_dir, self.family_idx):
            if build_to == 2 or build_to == 3:
                new_cell = random.choices(CLASSES, probabilities)[0](self.family_idx)
                self.create_life(new_cell, right_dir, energy_dist, self.family_idx)

        # Always move forward Newborn
                
        self.create_life(Newborn(self.family_idx), self.direction, energy_dist, self.family_idx)

        # Replace previous Newborn

        self.create_life(Pipe(self.family_idx), self.direction, energy_dist, -1, replace=True)