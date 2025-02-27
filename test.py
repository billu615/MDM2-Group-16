import numpy as np

num_flowers = np.random.poisson(0.01 * 500**2)
print(num_flowers)

print(np.random.randint(1, 3))

print(np.random.randint(10, 51))


list = [121313, 12131, 122222222, '1122']

di = {f'number{index}': value for index, value in enumerate(list) if isinstance(value, int)}
print(di)
