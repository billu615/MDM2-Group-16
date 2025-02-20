from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random


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

class PollinatorModel(Model):
    def __init__(self, width, height, num_pollinators, num_flowers, pesticide_ratio):
        self.grid = MultiGrid(width, height, True)
        
        pollinator_agents = Pollinator.create_agents(model=self, n=num_pollinators)
        flower_agents = Flower.create_agents(model=self, n=num_flowers)

        for i in flower_agents:
            x, y = self.random.randrange(width), self.random.randrange(height)
            contaminated = self.random.random() < pesticide_ratio
            self.grid.place_agent(i(contaminated), (x, y))
        
        for i in pollinator_agents:
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(i, (x, y))

    def step(self):
        self.agents.shuffle_do
        self.agents.shuffle_do()

# Running the model
if __name__ == "__main__":
    model = PollinatorModel(width=20, height=20, num_pollinators=10, num_flowers=30, pesticide_ratio=0.3)
    for _ in range(50):
        model.step()
