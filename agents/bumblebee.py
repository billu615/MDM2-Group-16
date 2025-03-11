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
    x: exposure level (ug)
    x50: dosage at which 50% of bees show the effect (LD50)
    k: steepness of the response curve (need to estimate)
    """
    return (x ** n) / (x ** n + x50 ** n)

class BumbleBees(Agent):
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
        self.energy = 400
        self.energy_cost = 1

        # Foraging attributes
        self.nectar = 0
        self.max_nectar_capacity = 100
        
        # Basic Movement attributes
        self.bee_sensing_radius = 1
        self.speed = 3

        # Trapline Movement attributes
        self.waypoints = None
        self.current_waypoint = 0

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

    def trapline(self):
        # Limit waypoints if contaminated
        if self.contaminated and self.random.random() < 0.3:  # 30% chance to revisit or skip waypoints
            self.current_waypoint = (self.current_waypoint + self.random.choice([-1, 1])) % len(self.waypoints)

        # Find direction
        target = np.array(self.waypoints[self.current_waypoint])
        direction = target - self.pos
        direction /= np.linalg.norm(direction)  # Normalize direction vector

        # Moving agent
        noise = self.rng.normal(0, 2, 2) # add noise to movement
        speed_factor = 0.7 if self.contaminated else 1  # Reduced speed due to pesticide exposure
        self.pos += (direction * self.speed * speed_factor) + noise
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
            self.energy += self.random.randint(4,10)
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
            self.energy = 400
            self.current_waypoint = 0

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
        r = self.random.random()
        if r < probability:
            #print('random', r)
            #print('exposure', self.pesticide_exposure)
            #print('prob', probability)
            self.remove()
            #print('death by poison')
        elif self.energy <= 0:
            self.remove()
            #print('death by energy')

    def step(self):
        self.death()
        if self.nectar < self.max_nectar_capacity or self.energy > 20.0:
            self.trapline()
            self.forage()
        else:
            self.return_to_hive()
