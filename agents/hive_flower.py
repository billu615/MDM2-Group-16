import numpy as np
from mesa import Agent

IMAGES = {
    "bee": "Images/bee.png",    
    "flower": "Images/flower.png",
    "hive": "Images/hive.png",
    'bee_contaminated': "Images/bee_contaminated.png",
    'flower_contaminated': "Images/flower_contaminated.png",
    'hive_contaminated': "Images/hive_contaminated.png"
}

reproduction_probs = {
    "honeybee": {"healthy": 0.98, "contaminated": 0.6},
    "bumblebee": {"healthy": 0.8, "contaminated": 0.4},
    "solitary": {"healthy": 0.6, "contaminated": 0.2}
}

class Flower(Agent):
    def __init__(self, model, contaminated=False):
        super().__init__(model)
        self.type = 'flower'
        self.contaminated = contaminated
        self.nectar_amount = self.model.random.randint(10, 51) # measured in micrograms
        self.ppb = self.model.random.uniform(1.9, 46.4)

        # Image Attributes
        self.image = IMAGES['flower']
        self.image_contaminated = IMAGES['flower_contaminated']

    def dosage(self):
        """ return dosage of pesticide in micrograms
        """
        return self.nectar_amount * self.ppb * 10**-6

class Hive(Agent):
    def __init__(self, model, contaminated=False):
        super().__init__(model)
        self.type = 'hive'
        self.contaminated = contaminated
        self.food_source = 0

        # Image Attributes
        self.image = IMAGES["hive"]
        self.image_contaminated = IMAGES['hive_contaminated']

    def step(self):
        if self.contaminated:
            probability = reproduction_probs[self.model.bee_type]['contaminated']
        else:
            probability = reproduction_probs[self.model.bee_type]['healthy']
        if self.model.random.random() < probability:
            new_agent = self.model.add_agent(hive=self.pos)
            new_agent.hive_object = self

            # Remove food source for reproduction
            #self.food_source -= 50
            #print('agents added')