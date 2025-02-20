from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from agent import Pollinator, Flower

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