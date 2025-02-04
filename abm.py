import numpy as np
from dataclasses import dataclass
import random
import matplotlib.pyplot as plt
from typing import List, Tuple

@dataclass
class Environment:
    """Represents the environment where pollinators interact with plants."""
    width: int
    height: int
    neonicotinoid_levels: np.ndarray  # 2D array representing pesticide concentration
    flower_locations: List[Tuple[int, int]]  # List of (x,y) coordinates for flowers
    
    def __init__(self, width: int, height: int, initial_pesticide_concentration: float):
        self.width = width
        self.height = height
        self.neonicotinoid_levels = np.full((width, height), initial_pesticide_concentration)
        self.flower_locations = []
        
    def add_flowers(self, num_flowers: int):
        """Add random flower locations."""
        for _ in range(num_flowers):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            self.flower_locations.append((x, y))
            
    def update(self):
        """Update environment conditions (e.g., pesticide degradation)."""
        degradation_rate = 0.01  # Example rate
        self.neonicotinoid_levels *= (1 - degradation_rate)

class Pollinator:
    """Represents a pollinator agent (e.g., bee)."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.health = 100.0  # Initial health
        self.pesticide_exposure = 0.0
        self.alive = True
        
    def move(self, environment: Environment):
        """Move the pollinator."""
        if not self.alive:
            return
            
        # Simple random movement
        self.x = (self.x + random.choice([-1, 0, 1])) % environment.width
        self.y = (self.y + random.choice([-1, 0, 1])) % environment.height
        
    def update(self, environment: Environment):
        """Update pollinator state based on environment interactions."""
        if not self.alive:
            return
            
        # Calculate pesticide exposure
        current_exposure = environment.neonicotinoid_levels[self.x, self.y]
        self.pesticide_exposure += current_exposure
        
        # Update health based on exposure
        exposure_impact = 0.1 * self.pesticide_exposure
        self.health -= exposure_impact
        
        # Check if pollinator dies
        if self.health <= 0:
            self.alive = False

class Simulation:
    """Main simulation class."""
    def __init__(self, 
                 width: int = 50, 
                 height: int = 50, 
                 num_pollinators: int = 100,
                 initial_pesticide: float = 0.1,
                 num_flowers: int = 50):
        
        # Initialize environment
        self.environment = Environment(width, height, initial_pesticide)
        self.environment.add_flowers(num_flowers)
        
        # Initialize pollinators
        self.pollinators = []
        for _ in range(num_pollinators):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            self.pollinators.append(Pollinator(x, y))
        
        # Statistics tracking
        self.alive_pollinators = []
        self.average_health = []
        
    def step(self):
        """Perform one simulation step."""
        # Update environment
        self.environment.update()
        
        # Update each pollinator
        for pollinator in self.pollinators:
            pollinator.move(self.environment)
            pollinator.update(self.environment)
        
        # Collect statistics
        alive_count = sum(1 for p in self.pollinators if p.alive)
        avg_health = np.mean([p.health for p in self.pollinators if p.alive]) if alive_count > 0 else 0
        
        self.alive_pollinators.append(alive_count)
        self.average_health.append(avg_health)
    
    def run(self, num_steps: int):
        """Run simulation for specified number of steps."""
        for _ in range(num_steps):
            self.step()
    
    def plot_results(self):
        """Plot simulation results."""
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.alive_pollinators)
        plt.title('Surviving Pollinators Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Number of Pollinators')
        
        plt.subplot(1, 2, 2)
        plt.plot(self.average_health)
        plt.title('Average Pollinator Health Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Average Health')
        
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize and run simulation
    sim = Simulation(
        width=50,
        height=50,
        num_pollinators=100,
        initial_pesticide=0.1,
        num_flowers=50
    )
    
    sim.run(num_steps=100)
    sim.plot_results()