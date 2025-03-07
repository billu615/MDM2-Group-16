import numpy as np

num_flowers = np.random.poisson(0.01 * 500**2)
print(num_flowers)

print(np.random.pareto(1.5) * 5)

def logistic_function(x, x50, k):
    """
    Hill function, return the proability of the effect
    x: exposure level (ppb)
    x50: concentration at which 50% of bees show the effect (LC50)
    k: steepness of the response curve (need to estimate)
    """
    try:
        return 1 / (1 + np.exp(-k * (x - x50)))
    except ZeroDivisionError:
        return 0
    

def hill_mortality(x, x50, n):
    """
    Hill function, return the proability of the effect
    x: exposure level (ppb)
    x50: concentration at which 50% of bees show the effect (LC50)
    k: steepness of the response curve (need to estimate)
    """
    return (x ** n) / (x ** n + x50 ** n)

prob = hill_mortality(0, 0.014, 15)
print(prob)
