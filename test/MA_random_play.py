import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gym
import env
from env.macActEnvWrapper import MacEnvWrapper

import random
from gym.wrappers.monitoring.video_recorder import VideoRecorder


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

env = gym.make("Overcooked-MA-v0", **env_params)
env = MacEnvWrapper(env)

#                     0       1       2       3     4          5             6               7              8               9              10              11       12
MACROACTIONNAME = ["right", "down", "left", "up", "stay", "get tomato", "get lettuce", "get plate 1", "get plate 2", "go to knife 1", "go to knife 2", "deliver", "chop"]

# video_recorder = None
# video_recorder = VideoRecorder(env, "video.mp4", enabled=True)

observation = env.reset()                         

while(True):
    env.render()
    #video_recorder.capture_frame_10_times() 

    action = [random.randint(0, 12), random.randint(0, 12)]
    observation, reward, done, info = env.step(action)
    if done:
        break


#video_recorder.close()
#video_recorder.enabled = False


