import solara
from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component

from model import PollinatorModel

def agent_draw(agent):
    """Display the human agents as black dots and zombies as red dots."""
    if agent.infected == False:
        return {"color": "black", "size": 5}
    else:
        return {"color": "red", "size": 5}
    

# Initiate the model
model = PollinatorModel()

page = SolaraViz(
    model, 
    components=[
        make_space_component(agent_portrayal=agent_draw, backend="matplotlib"),
        ],
    model_params={},
    name="Pollinator Model",
)

page #noqa