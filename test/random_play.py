import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import env
import gym

import random
import time


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
debug = True

env_params = {'grid_dim': grid_dim,
                'map': map,
                'task': task,
                'rewardList': rewardList,
                'debug': debug
                }

env = gym.make("Overcooked-v0", **env_params)


observation = env.reset()
while(True):
    env.render()

    a0 = random.randint(0, 5)
    a1 = random.randint(0, 5)

    action = [a0, a1]
    observation, reward, done, info = env.step(action)
    time.sleep(0.1)






