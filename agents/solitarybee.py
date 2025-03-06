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

class SolitaryBees(Agent):
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
        self.max_nectar_capacity = 50
        
        # Basic Movement attributes
        self.bee_sensing_radius=bee_sensing_radius
        self.speed = 2.5

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

    def random_walk(self):
        # Generate angle and length
        angle = self.model.random.uniform(0, 2 * np.pi) + (np.random.normal(0, np.pi / 2) if self.contaminated else 0)
        step_length = self.speed * (0.5 if self.contaminated else 1)  # Slower movement

        # Moving agent
        self.pos += step_length * np.array([np.cos(angle), np.sin(angle)])
        self.model.space.move_agent(self, self.pos)
        self.energy -= 0.2

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

            # Contaminate hive
            if self.contaminated:
                self.hive_object.contaminated = True
        else:
            # 30% chance of flying in the wrong direction
            if self.contaminated and self.random.random() < 0.3:
                direction = self.random.uniform(-1, 1, 2)
            
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
            self.random_walk()
            self.forage()
        else:
            self.return_to_hive()