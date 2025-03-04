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

'''
========================================================================
                        Solitarybees Class
========================================================================
'''
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
        self.max_nectar_capacity = 60
        
        # Movement attributes
        self.bee_sensing_radius=bee_sensing_radius
        self.speed = 1
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
        step_length = 10 * (0.5 if self.contaminated else 1)  # Slower movement

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
        if distance < 5:          # Arrived at the hive
            self.pos = self.hive_object.pos
            self.model.space.move_agent(self, self.pos)
            print('returned to hive')
            self.hive_object.food_source += self.nectar
            self.nectar = 0
            self.energy = 50
            if self.contaminated:
                self.hive_object.contaminated = True
        else:
            if self.contaminated and np.random.random() < 0.3:  # 30% chance of flying in the wrong direction
                direction = np.random.uniform(-1, 1, 2)
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

'''
========================================================================
                        Bumblebees Class
========================================================================
'''

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
        self.max_nectar_capacity = 60
        
        # Basic Movement attributes
        self.bee_sensing_radius=bee_sensing_radius
        self.speed = 1

        # Trapline Movement attributes
        self.flowers_memory = []

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

       

    def levy_flight_step(self):
        # Generate angle
        angle = np.random.uniform(0, 2 * np.pi)
        # Generate step length based on pareto distribution
        step_length = np.random.pareto(1.5) * 5  # Power-law distribution
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
            self.levy_flight_step()
            self.forage()
        else:
            self.return_to_hive()

'''
========================================================================
                        Honeybees Class
========================================================================
'''

class HoneyBees(Agent):
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
        self.max_nectar_capacity = 60
        
        # Movement attributes
        self.bee_sensing_radius=bee_sensing_radius
        self.speed = 5
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
        angle = np.random.uniform(0, 2 * np.pi)
        # Generate step length based on pareto distribution (Speed)
        step_length = np.random.pareto(1.5) * 5  # Power-law distribution
        # Move based on angle and direction
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
        if self.nectar < self.max_nectar_capacity or self.energy > 20:
            self.levy_flight()
            self.forage()
        else:
            self.return_to_hive()

class Flower(Agent):
    def __init__(self, model, contaminated=False):
        super().__init__(model)
        self.type = 'flower'
        self.contaminated = contaminated
        self.nectar_amount = self.model.random.randint(10, 51)

        # Image Attributes
        self.image = IMAGES['flower']
        self.image_contaminated = IMAGES['flower_contaminated']

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
        if self.model.random.random() < 0.5 and self.food_source > 100:
            new_agent = self.model.add_agent(hive=self.pos)
            new_agent.hive_object = self

            # Remove food source for reproduction
            self.food_source -= 50
            print('agents added')
