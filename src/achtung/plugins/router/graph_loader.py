#cspell:disable

"""
This module is responsible for loading the map data. It performs the following:
1. Opens the JSON file containing the map data.
2. Reads the data inside it (streets and distances/weights).
3. Converts it into an Adjacency List 
   that will be passed to the routing algorithms (like Dijkstra && A*) to work on.
"""

import json
from pathlib import Path

def load_graph():
    base_dir = Path(__file__).parent.parent.parent  # router -> plugins -> achtung
    file_path = base_dir/"data"/"kfs_graph.json"
    
    
    if not file_path.exists():
        raise FileNotFoundError(f"Graph Data File not Found at {file_path}")

    with open(file_path , 'r' , encoding ='utf-8') as f: # for arabic support
        graph_data = json.load(f) #convert to json

    return graph_data