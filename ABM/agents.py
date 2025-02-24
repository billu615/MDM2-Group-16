from mesa import Agent

IMAGES = {
    "bee": "Images/bee.png",    
    "flower": "Images/flower.png",  # Replace with actual URL or local path
    "hive": "Images/hive.png"       # Replace with actual URL or local path
}

class Bees(Agent):
    def __init__(self, model, initial_health=5):
        super().__init__(model)
        self.type = 'bee'
        self.health = initial_health
        self.pollen = 0
        self.max_pollen_capacity = 50
        self.image = IMAGES['bee']

    def random_move(self):
        # pollinator randomly moves
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def forage(self):
        # sense if there's flower in its neighbours
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cellmates:
            if isinstance(obj, Flower):
                self.pollen += 5
                if obj.contaminated:
                    self.health -= 1

    def death(self):
        if self.health <= 0:
            self.remove()

    '''
    def hive_move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        hive_positions = self.model.agents_by_type[Hive].pos
    '''

    def step(self):
        self.death()
        if self.pollen < self.max_pollen_capacity:
            self.random_move()
            self.forage()
        else:
            self.random_move()
            self.forage()

class Flower(Agent):
    def __init__(self, model, contaminated=False):
        super().__init__(model)
        self.type = 'flower'
        self.contaminated = contaminated
        self.image = IMAGES['flower']

class Hive(Agent):
    def __init__(self, model, contaminated=False):
        super().__init__(model)
        self.type = 'hive'
        self.contaminated = contaminated
        self.image = IMAGES["hive"]
