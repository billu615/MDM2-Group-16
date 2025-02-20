from mesa import agent

import model

class Pollinator(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 10
        self.exposure = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def forage(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cellmates:
            if isinstance(obj, Flower):
                self.energy += 5
                if obj.contaminated:
                    self.exposure += 1

    def step(self):
        self.move()
        self.forage()
        self.energy -= 1
        if self.energy <= 0 or self.exposure > 5:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class Flower(Agent):
    def __init__(self, unique_id, model, contaminated=False):
        super().__init__(unique_id, model)
        self.contaminated = contaminated