# snowdrop-tangled-game-package
This repo contains base classes for the Tangled game and agents. It is also where the
game graphs I use repeatedly are stored. While Tangled can be played on any connected
graph, I selected some specific graphs to demonstrate certain aspects of the game. The game
graphs exposed on the tangled-game.com website are a subset of the graphs here that I analyzed
for the [X-Prize Phase 1 Submission document](https://fqodzpifyovgmqjlluin.supabase.co/storage/v1/object/public/pdfs/XPRIZE_Phase_I_Submission_Snowdrop.pdf).

## Game Graphs
The `game_graph_ground_truth.py` file contains a set of game graphs and game parameters for those
graphs. The numbering on these is historical and doesn't make much sense, but I got used to it. 
To define a game graph, define the graph itself in the `GRAPH_DATABASE` dict, the vertex ownership 
choice in `VERTEX_OWNERSHIP`, the draw boundary for your graph in `EPSILON_VALUES`, and the anneal time 
for the quantum hardware in `ANNEAL_TIMES`. `ALLOWED_GRAPHS` is a filter to return only a subset of 
all the graphs. The current filter only returns the graphs in the X-Prize submission.

## Game Base Classes
Most of the other stuff here are base classes that you will subclass to build game playing agents and
adjudicators in the snowdrop-tangled-agents and snowdrop-adjudicators repos respectively. In those repos
I'll describe how this works. The two most important base classes are the `Game` class in game.py and the
`GameAgentBase` class in `base_agent.py`. 
