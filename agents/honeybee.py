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

# Use acute data only for short term effect (microgram)
ld50_data = {
    "honeybee": 0.0102,
    "bumblebee": 0.014,
    "solitary": 0.00386
}

# Controls how quickly the probability of lethality increases around the LD50 value
steepness_dict = {
    "honeybee": {"low": 1, "moderate": 2, "high": 4},
    "bumblebee": {"low": 1.5, "moderate": 3, "high": 5},
    "solitary": {"low": 1, "moderate": 2.5, "high": 4.5}
}

def hill_mortality(x, x50, n):
    """
    Hill function, return the proability of the effect
    x: exposure level (ppb)
    x50: concentration at which 50% of bees show the effect (LC50)
    k: steepness of the response curve (need to estimate)
    """
    return (x ** n) / (x ** n + x50 ** n)

class HoneyBees(Agent):
    def __init__(self, 
                 model,
                 sensitivity, 
                 contaminated=False):
        super().__init__(model)
        self.type = 'bee'

        # Health attributes
        self.pesticide_exposure = 0
        self.contaminated = contaminated
        self.sensitivity = sensitivity
        self.energy = 200
        self.energy_cost = 0.5

        # Foraging attributes
        self.nectar = 0
        self.max_nectar_capacity = 60
        
        # Basic Movement attributes
        self.bee_sensing_radius = 2
        self.speed = 5
        self.max_speed = 7.5

        # Hive attributes
        self.hive = self.model.random.randint(1, self.model.num_hive)
        self.hive_object = None
        self.time_not_return_hive = 0

        # Image attribute
        self.image = IMAGES['bee']
        self.image_contaminated = IMAGES['bee_contaminated']
        
    '''
    =================================
            Flight Pattern
    =================================
    '''

    def levy_flight(self):
        # Generate angle
        angle = self.random.uniform(0, 2 * np.pi)
        # Generate step length based on pareto distribution => speed
        if self.contaminated:
            step_length = self.model.rng.pareto(2.5) * 2.1 # Mean is approxiamately 3.51
        else:
            step_length = self.model.rng.pareto(2.5) * 3  # Mean is approxiamately 5.02
        #if step_length > self.max_speed:
        #    step_length = self.max_speed

        # Move based on angle and direction
        self.pos += step_length * np.array([np.cos(angle), np.sin(angle)])
        self.model.space.move_agent(self, self.pos)
        self.energy -= self.energy_cost

    def forage(self):
        # Gets flower neighbours
        flower_neighbours = np.array(
            [agent for agent in self.model.space.get_neighbors(self.pos, self.bee_sensing_radius, True)
             if agent.type == 'flower']
        )
        for flower in flower_neighbours:
            self.nectar += flower.nectar_amount
            self.energy += self.model.random.randint(4,10)
            if flower.contaminated:
                pesticide_dosage = flower.dosage()
                self.pesticide_exposure += pesticide_dosage
                self.contaminated = True
    
    def return_to_hive(self):
        direction = self.hive_object.pos - self.pos
        distance = np.linalg.norm(direction)
        # Arrived at the hive
        if distance < 5:          
            self.pos = self.hive_object.pos
            self.model.space.move_agent(self, self.pos)
            #print('returned to hive')

            # Reset parameter once return to hive
            self.hive_object.food_source += self.nectar
            self.nectar = 0
            self.energy = 200

            # Contaminate hive
            if self.contaminated:
                self.hive_object.contaminated = True
        else:
            # 30% chance of flying in the wrong direction
            if self.contaminated and self.model.random.random() < 0.3:
                direction = self.model.rng.uniform(-1, 1, 2)
            
            # Moving to hive
            direction /= distance  # Normalize
            self.pos += direction * 5  # Move towards hive
            self.model.space.move_agent(self, self.pos)
            self.energy -= self.energy_cost

    def death(self):
        probability = hill_mortality(x=self.pesticide_exposure, 
                                                    x50=ld50_data[self.model.bee_type],
                                                    n=steepness_dict[self.model.bee_type][self.sensitivity])
        r = self.model.random.random()
        if r < probability:
            #print('random', r)
            #print('exposure', self.pesticide_exposure)
            #print('prob', probability)
            self.remove()
            #print('death by poison')
            #print('\n')
        elif self.energy <= 0:
            self.remove()
            #print('death by energy')

    def step(self):
        self.death()
        if self.nectar < self.max_nectar_capacity or self.energy > 20.0:
            self.levy_flight()
            self.forage()
        else:
            self.return_to_hive()