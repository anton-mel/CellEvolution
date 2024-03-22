#!/bin/bash

screen -S evolution_bg -d -m
screen -S evolution_bg -X stuff 'python ./EvolutionGame.py\n'

# Close the screen session
# screen -S evolution_bg -X quit