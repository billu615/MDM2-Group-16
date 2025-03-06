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


data = {
    "Bee Type": ["Honey Bee", "Honey Bee", "Bumble Bee", "Bumble Bee", "Solitary Bee", "Solitary Bee"],
    "Effect Type": ["Sub Lethal", "Lethal", "Sub Lethal", "Lethal", "Sub Lethal", "Lethal"],
    "x50 (ppb)": [4.8, 185, 2.87, 120, 3, 0.45],  # LC50 or threshold for 50% response
    "k (Steepness)": [3, 10, 2, 8, 4, 2]  # Steepness of response curve
}

# Neonicotinoid exposure data for different bees
data = {
    "honeybee" : {"lethal": 185, "sublethal": 4.8, "steepness" : [10, 3]},
    "bumblebee" : {"lethal": 120, "sublethal": 2.87, "steepness" : [8, 2]},
    "solitary" : {"lethal": 0.45, "sublethal": 3,  "steepness" : [2, 4]}
}

def hill_function(x, x50, k):
    """
    Hill function, return the proability of the effect
    x: exposure level (ppb)
    x50: concentration at which 50% of bees show the effect (LC50)
    k: steepness of the response curve (need to estimate)
    """
    try:
        return  (1+(x50/x)**k)**(-1)
    except ZeroDivisionError:
        return 0

class BumbleBees(Agent):
    def __init__(self, 
                 model,
                 bee_sensing_radius=2,
                 initial_health=5, 
                 contaminated=False):
        super().__init__(model)
        self.type = 'bee'
        self.health = initial_health
        self.energy = 50
        self.contaminated = contaminated

        # Foraging attributes
        self.nectar = 0
        self.max_nectar_capacity = 100
        self.exposure = 0
        
        # Basic Movement attributes
        self.bee_sensing_radius=bee_sensing_radius
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

    def forage(self):
        # Gets flower neighbours
        flower_neighbours = np.array(
            [agent for agent in self.model.space.get_neighbors(self.pos, self.bee_sensing_radius, True)
             if agent.type == 'flower']
        )
        for flower in flower_neighbours:
            self.nectar += flower.nectar_amount
            if flower.contaminated:
                self.contaminated = True
                self.health -= 1
    
    def return_to_hive(self):
        direction = self.hive_object.pos - self.pos
        distance = np.linalg.norm(direction)
        # Arrived at the hive
        if distance < 5:          
            self.pos = self.hive_object.pos
            self.model.space.move_agent(self, self.pos)
            print('returned to hive')

            # Reset parameter once return to hive
            self.hive_object.food_source += self.nectar
            self.nectar = 0
            self.energy = 50
            self.current_waypoint = 0

            # Contaminate hive
            if self.contaminated:
                self.hive_object.contaminated = True
        else:
            # 30% chance of flying in the wrong direction
            if self.contaminated and np.random.random() < 0.3:
                direction = np.random.uniform(-1, 1, 2)
            
            # Moving to hive
            direction /= distance  # Normalize
            self.pos += direction * 5  # Move towards hive
            self.model.space.move_agent(self, self.pos)
            self.energy -= 0.2

    def death(self):
        if self.health <= 0:
            self.remove()
            print('death by poison')
        elif self.energy <= 0:
            self.remove()
            print('death by energy')

    def step(self):
        self.death()
        if self.nectar < self.max_nectar_capacity or self.energy > 20.0:
            self.trapline()
            self.forage()
        else:
            self.return_to_hive()
