import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from pollinator_agents import Bees, Flower, Hive

class PollinatorModel(Model):
    def __init__(self, width=100, height=100, num_pollinators=100, num_flowers=20, num_hive=2,
                 pesticide_ratio=0.2):
        
        self.grid = MultiGrid(width, height, True)
        
        pollinator_agents = Bees.create_agents(model=self, n=num_pollinators)
        flower_agents = Flower.create_agents(model=self, n=num_flowers)
        hive_agents = Hive.create_agents(model=self, n=num_hive)

        # place flower agent
        for i in flower_agents:
            x, y = self.random.randrange(width), self.random.randrange(height)
            contaminated = self.random.random() < pesticide_ratio
            self.grid.place_agent(i(contaminated=contaminated), (x, y))
        
        # place pollinator agent
        for i in pollinator_agents:
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(i, (x, y))
        
        # place hive agent (hives are not comtaminated)
        for i in hive_agents:
            x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(i, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "Total Pollinators": lambda m: len(m.agents_by_type[Bees])
            }
        )

    def step(self):

        # Pollinator do step
        self.agents.select(agent_type=Bees).do('step')

        # Collect model data
        self.datacollector.collect(self)

model = PollinatorModel()
for _ in range(100):
    model.step()

data = model.datacollector.get_model_vars_dataframe()
print(data)
