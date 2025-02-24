from mesa import agent

from pollinator_model import PollinatorModel

class Bees(Agent):
    def __init__(self, model, initial_health=100):
        super().__init__(model)
        self.health = initial_health
        self.pollen = 0
        self.max_pollen_capacity = 50

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
    def __init__(self, unique_id, model, contaminated=False):
        super().__init__(unique_id, model)
        self.contaminated = contaminated

class Hive(Agent):
    def __init__(self, unique_id, model, contaminated=False):
        super().__init__(unique_id, model)
        self.contaminated = contaminated
