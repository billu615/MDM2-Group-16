import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Load the image (ensure the path is correct)
img = plt.imread("Images/hive.png")  # Replace with your image path

# Sample scatter data
x = np.random.rand(10) * 10  # Random x-coordinates
y = np.random.rand(10) * 10  # Random y-coordinates

# Create the plot
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Function to create an image scatter point
def add_image(ax, image, x, y, zoom=0.1):
    im = OffsetImage(image, zoom=zoom)  # Adjust zoom to control image size
    ab = AnnotationBbox(im, (x, y), frameon=False, xycoords='data')
    ax.add_artist(ab)

# Plot images at scatter points
for i in range(len(x)):
    add_image(ax, img, x[i], y[i], zoom=0.2)  # Adjust zoom for size

plt.show()
