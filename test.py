import numpy as np

num_flowers = np.random.poisson(0.01 * 500**2)
print(num_flowers)

print(np.random.pareto(1.5) * 5)
