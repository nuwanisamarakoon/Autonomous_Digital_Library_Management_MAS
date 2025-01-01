import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.digital_library_model import DigitalLibraryModel, LibraryAgent, BookAgent, UserAgent
import mesa
import numpy as np

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5  # Default radius
    }

    if isinstance(agent, LibraryAgent):
        portrayal["Color"] = "green"
        portrayal["r"] = 1.0
    elif isinstance(agent, BookAgent):
        portrayal["Color"] = "red"
        portrayal["r"] = 0.3
    elif isinstance(agent, UserAgent):
        portrayal["Color"] = "yellow"
        portrayal["r"] = 0.5

    return portrayal


# Create a grid visualization
grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Performance charts
charts = [
    mesa.visualization.ChartModule([{"Label": "Book Allocation Efficiency", "Color": "blue"}])
]
# Model parameters for interactive simulation
model_params = {
    "num_libraries": mesa.visualization.Slider("Number of Libraries", 1, 1, 1000, 1),
    "num_books": mesa.visualization.Slider("Number of Books", 10, 5, 2500, 1),
    "num_users": mesa.visualization.Slider("Number of Users", 5, 1, 2500, 1)
}



# Create Modular Server
server = mesa.visualization.ModularServer(
    DigitalLibraryModel,
    [grid] + charts,
    "Digital Library Management System",
    model_params
)
server.port = 8521

if __name__ == "__main__":
    server.launch()
