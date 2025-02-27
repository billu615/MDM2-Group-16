import numpy as np
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

from agents import Bees, Flower, Hive

class PollinatorModel(Model):
    def __init__(self, 
                 width=150, 
                 height=150, 
                 num_pollinators=100, 
                 avg_flowers_per_unit=0.01, 
                 num_hive=2,
                 pesticide_ratio=0.7,
                 bee_sensing_radius=2):
        super().__init__()

        self.width = width
        self.height = height
        self.num_hive = num_hive

        self.space = ContinuousSpace(width, height, True)
        
        # Initiate number of flower with poisson distribution
        num_flowers = np.random.poisson(avg_flowers_per_unit * (width*height)**2)
        num_flowers = 100

        # Create Agents
        pollinator_agents = Bees.create_agents(model=self,
                                                n=num_pollinators,
                                                bee_sensing_radius=bee_sensing_radius)
        flower_agents = Flower.create_agents(model=self, n=num_flowers)
        hive_agents = Hive.create_agents(model=self, n=num_hive)

        # place flower agent
        for i in flower_agents:
            x, y = self.random.uniform(0, width), self.random.uniform(0, height)
            contaminated = self.random.random() < pesticide_ratio
            i.contaminated = contaminated
            self.space.place_agent(i, (x, y))
        
        # place initial hive and bee agent (hives are not comtaminated)
        for index, hive in enumerate(hive_agents):
            x, y = self.random.uniform(0, width), self.random.uniform(0, height)
            self.space.place_agent(hive, (x, y))
            for bee in pollinator_agents:
                if bee.hive == index + 1:
                    self.space.place_agent(bee, (x, y))
                    bee.hive_object = hive

        #print([agent.hive_object for agent in self.agents_by_type[Bees]])

        self.datacollector = DataCollector(
            model_reporters={
                "Total Pollinators": lambda m: len(m.agents_by_type[Bees]),
                "Average Bee Health": lambda m: np.mean([bee.health for bee in m.agents_by_type[Bees]]),
                "Contaminated Bees": lambda m: len([bee.contaminated for bee in m.agents_by_type[Bees] if bee.contaminated])
            }
        )

    def step(self):
        # Pollinator do step
        self.agents.select(agent_type=Bees).shuffle_do('step')

        # Collect model data
        self.datacollector.collect(self)

