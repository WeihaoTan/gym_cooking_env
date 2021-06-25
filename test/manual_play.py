import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env.overcooked_env import Overcooked_env

import random
import time
import pygame
from pygame.locals import *


#0:space, 1: counter 2: agent, 3: tomato, 4: lettuce, 5: plate, 6: knife, 7: delivery

# grid_dim = [7, 7]
# map =  [[1, 1, 1, 1, 1, 3, 1],
#         [6, 0, 2, 0, 2, 0, 4],
#         [6, 0, 0, 0, 0, 0, 1],
#         [7, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 5],
#         [1, 1, 1, 1, 1, 5, 1]]


grid_dim = [6, 6]
map =  [[1, 1, 1, 1, 3, 1],
        [6, 0, 2, 0, 2, 4],
        [6, 0, 0, 0, 0, 1],
        [7, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 5],
        [1, 1, 1, 1, 5, 1]]

#task = "tomato-lettuce salad"
task = "tomato salad"
#task = "lettuce salad"

rewardList = {"subtask finished": 10, "correct delivery": 100, "wrong delivery": -100}

env = Overcooked_env(grid_dim, map, task, rewardList)

observation = env.reset()
while(True):
    env.render()

    a0 = 5
    a1 = 5
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                a0 = 2
            elif event.key == pygame.K_s:
                a0 = 1
            elif event.key == pygame.K_d:
                a0 = 0
            elif event.key == pygame.K_w:
                a0 = 3

            if event.key == pygame.K_LEFT:
                a1 = 2
            elif event.key == pygame.K_DOWN:
                a1 = 1
            elif event.key == pygame.K_RIGHT:
                a1 = 0
            elif event.key == pygame.K_UP:
                a1 = 3

    if a0 !=5 or a1 != 5:
        action = [a0, a1]
        observation, reward, done, info = env.step(action)
        print(reward)






