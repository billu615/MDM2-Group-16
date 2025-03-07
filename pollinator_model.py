import numpy as np
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

from agents.honeybee import HoneyBees
from agents.bumblebee import BumbleBees
from agents.solitarybee import SolitaryBees
from agents.hive_flower import Hive, Flower

bee_types = {
    'honeybee' : HoneyBees,
    'bumblebee' : BumbleBees,
    'solitary' : SolitaryBees
}

class PollinatorModel(Model):
    def __init__(self, 
                 bee_type='honeybee',
                 sensitivity='moderate',
                 width=150, 
                 height=150, 
                 num_pollinators=100, 
                 avg_flowers_per_unit=0.01, 
                 num_hive=2,
                 pesticide_ratio=0.7,):
        super().__init__()

        self.width = width
        self.height = height
        self.num_hive = num_hive
        self.sensitivity = sensitivity

        # Create Continuous space
        self.space = ContinuousSpace(width, height, True)
        
        # Initiate number of flower with poisson distribution
        num_flowers = np.random.poisson(avg_flowers_per_unit * (width*height)**2)
        num_flowers = 200

        # Differentiate bee types
        self.bee_type = bee_type
        Bees = bee_types[self.bee_type]

        # Create Agents
        flower_agents = Flower.create_agents(model=self, n=num_flowers)
        hive_agents = Hive.create_agents(model=self, n=num_hive)
        pollinator_agents = Bees.create_agents(model=self,
                                                n=num_pollinators,
                                                sensitivity=sensitivity)

        # place flower agent
        for i in flower_agents:
            x, y = self.random.uniform(0, width), self.random.uniform(0, height)
            contaminated = self.random.random() < pesticide_ratio
            i.contaminated = contaminated
            self.space.place_agent(i, (x, y))

        # Add flower memory to bumblebee
        if self.bee_type == 'bumblebee':
            flowers_pos = [agent.pos for agent in self.agents_by_type[Flower]]
            for bee in pollinator_agents:
                bee.waypoints = self.random.choices(flowers_pos, k=6)
        
        # place initial hive and bee agent (hives are not comtaminated)
        for index, hive in enumerate(hive_agents):
            x, y = self.random.uniform(0, width), self.random.uniform(0, height)
            self.space.place_agent(hive, (x, y))
            for bee in pollinator_agents:
                if bee.hive == index + 1:
                    self.space.place_agent(bee, (x, y))
                    bee.hive_object = hive

        # Specify data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Pollinators": lambda m: len(m.agents_by_type[Bees]),
                "Average dosage": lambda m: np.mean([bee.pesticide_exposure for bee in m.agents_by_type[Bees]]),
                "Contaminated Bees": lambda m: len([bee.contaminated for bee in m.agents_by_type[Bees] if bee.contaminated]),
                "Average nectar": lambda m: np.mean([bee.nectar for bee in m.agents_by_type[Bees]])
            }
        )

    def step(self):
        # Pollinator do step
        self.agents.select(agent_type=bee_types[self.bee_type]).shuffle_do('step')

        self.agents.select(agent_type=Hive).do('step')

        # Collect model data
        self.datacollector.collect(self)
    
    def add_agent(self, hive):
        # Initiate bee type
        Bees = bee_types[self.bee_type]

        # Create agent
        new_agent = Bees(model=self, sensitivity=self.sensitivity)
        self.agents_by_type[Bees].add(new_agent)

        if self.bee_type == 'bumblebee':
            flowers_pos = [agent.pos for agent in self.agents_by_type[Flower]]
            new_agent.waypoints = self.random.choices(flowers_pos, k=6)

        self.space.place_agent(new_agent, hive)
        return new_agent

