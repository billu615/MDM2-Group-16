import pandas as pd
import numpy as np

# mesa + solara imports
import solara
from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component
from mesa.visualization.utils import update_counter

# matplotlib imports
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image 

from pollinator_model import PollinatorModel

zoom_size ={
    'bee': 0.3,
    'flower': 0.5,
    'hive': 1
}

def add_image(ax, image, x, y, zoom=1):
    img = np.array(Image.open(image))
    im = OffsetImage(img, zoom=zoom)  # Adjust zoom to control image size
    ab = AnnotationBbox(im, (x, y), frameon=False, xycoords='data')
    ax.add_artist(ab)

@solara.component
def agent_graph(model):
    update_counter.get()
    fig, ax = plt.subplots()
    ax.set_xlim(model.width)
    ax.set_ylim(model.height)
    ax.axis('off')
    for agent in model.agents:
        zoom = zoom_size[agent.type]
        add_image(ax, image=agent.image, x=agent.pos[0], y=agent.pos[1], zoom=zoom)
    solara.FigureMatplotlib(fig)
    
# Initiate the model
model = PollinatorModel()
population_plot = make_plot_component("Total Pollinators")
health_plot = make_plot_component("Average Bee Health")

page = SolaraViz(
    model, 
    components=[
        agent_graph,
        population_plot,
        health_plot
        ],
    model_params={},
    name="Pollinator Model",
)

page #noqa
