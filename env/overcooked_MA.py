from PIL.Image import new
import gym
from gym.core import ActionWrapper
import numpy as np
from queue import PriorityQueue

from gym import spaces
from numpy.core.fromnumeric import _squeeze_dispatcher
from env.items import Tomato, Lettuce, Plate, Knife, Delivery, Agent, Food
from env.render.game import Game
from env.overcooked import Overcooked
from env.mac_agent import MacAgent
from gym import Wrapper
import random



DIRECTION = [(0,1), (1,0), (0,-1), (-1,0)]
ITEMNAME = ["space", "counter", "agent", "tomato", "lettuce", "plate", "knife", "delivery"]
ITEMIDX= {"space": 0, "counter": 1, "agent": 2, "tomato": 3, "lettuce": 4, "plate": 5, "knife": 6, "delivery": 7}
AGENTCOLOR = ["blue", "magenta", "green", "yellow"]
TASKLIST = ["tomato salad", "lettuce salad", "tomato-lettuce salad"]
MACROACTIONNAME = ["right", "down", "left", "up", "stay", "get tomato", "get lettuce", "get plate 1", "get plate 2", "go to knife 1", "go to knife 2", "deliver", "chop"]
#MACROACTIONNAME = ["get tomato", "get lettuce", "get plate 1", "get plate 2", "go to knife 1", "go to knife 2", "deliver", "chop"]
ACTIONIDX = {"stay": 4}

#macro action space
#get tomato: 0
#get lettuce: 1
#get plate 1/2: 2 3
#go to knife 1/2: 4 5
#chop: 6
#deliver: 7

class AStarAgent(object):
    def __init__(self, x, y, g, dis, action, history_action):
        self.x = x
        self.y = y
        self.g = g
        self.dis = dis
        self.action = action
        self.history_action = history_action

    def __lt__(self, other):
        return self.dis <= other.dis

class Overcooked_MA(Overcooked):
        
    def __init__(self, grid_dim, map, task, rewardList, debug):
        super().__init__(grid_dim, map, task, rewardList, debug)
        self.macroAgent = []
        self._createMacroAgents()
        self.macroActionItemList = []
        self._createMacroActionItemList()

    def _createMacroAgents(self):
        for agent in self.agent:
            self.macroAgent.append(MacAgent())

    def _createMacroActionItemList(self):
        self.macroActionItemList = []
        for key in self.itemDic:
            if key != "agent":
                self.macroActionItemList += self.itemDic[key]

    def macro_action_sample(self):
        macro_actions = []
        for agent in self.agent:
            macro_actions.append(random.randint(0, 7))
        return macro_actions     

    def build_agents(self):
        raise

    def build_macro_actions(self):
        raise

    def reset(self):
        super().reset()
        for agent in self.macroAgent:
            agent.reset()

    def run(self, macro_actions):
        actions = self._computeLowLevelActions(macro_actions)
        
        obs, rewards, terminate, info = self.step(actions)
        cur_mac = self._collectCurMacroActions()
        mac_done = self._computeMacroActionDone()

        if self.debug:
            print("primitive action:", MACROACTIONNAME[actions[0]], MACROACTIONNAME[actions[1]])
            print("cur_mac", cur_mac)
            print("cur_mac name", MACROACTIONNAME[cur_mac[0]], MACROACTIONNAME[cur_mac[1]])
            print("mac_done", mac_done)
            print("map", self.map)
        print("-----------------------------------")


        self._createMacroActionItemList()

        self._get_macro_obs(obs)
        
        info = {'cur_mac': cur_mac, 'mac_done': mac_done}
        return  obs, rewards, terminate, info

    def _computeLowLevelActions(self, macro_actions):

        primitive_actions = []
        # loop each agent
        for idx, agent in enumerate(self.agent):
            if self.macroAgent[idx].cur_macro_action_done:
                self.macroAgent[idx].cur_macro_action = macro_actions[idx]
                macro_action = macro_actions[idx]
                self.macroAgent[idx].cur_macro_action_done = False
            else:
                macro_action = self.macroAgent[idx].cur_macro_action
            
            # print("agent-{color} ".format(color = agent.color))    
            # print(self.macroAgent[idx].cur_macro_action_done, MACROACTIONNAME[macro_actions[idx]], MACROACTIONNAME[self.macroAgent[idx].cur_macro_action])
            

            primitive_action = ACTIONIDX["stay"]

            if macro_action <= ACTIONIDX["stay"]:
                primitive_action = macro_action
                self.macroAgent[idx].cur_macro_action_done = True
            elif MACROACTIONNAME[macro_action] == "chop":
                for action in range(4):
                    new_x = agent.x + DIRECTION[action][0]
                    new_y = agent.y + DIRECTION[action][1]
                    new_name = ITEMNAME[self.map[new_x][new_y]] 
                    if new_name == "knife":
                        knife = self._findItem(new_x, new_y, new_name)
                        if isinstance(knife.holding, Food):
                            if not knife.holding.chopped:
                                primitive_action = action
                                self.macroAgent[idx].cur_chop_times += 1
                                if self.macroAgent[idx].cur_chop_times >= 3:
                                    self.macroAgent[idx].cur_macro_action_done = True
                                    self.macroAgent[idx].cur_chop_times = 0
                                break
                if primitive_action == ACTIONIDX["stay"]:
                    self.macroAgent[idx].cur_macro_action_done = True
            else:
                target = self.macroActionItemList[macro_action - 5]
                if ITEMNAME[self.map[target.x][target.y]] == "agent":
                    self.macroAgent[idx].cur_macro_action_done = True
                else:
                    primitive_action = self._navigate(agent, target.x, target.y)
                    if primitive_action == ACTIONIDX["stay"]:
                        self.macroAgent[idx].cur_macro_action_done = True
                    if self._calItemDistance(agent, target) == 1:
                        self.macroAgent[idx].cur_macro_action_done = True
                        if (MACROACTIONNAME[macro_action] == "get plate 1"\
                        or MACROACTIONNAME[macro_action] == "get plate 1") and agent.holding:
                            if isinstance(agent.holding, Food):
                                if agent.holding.chopped:
                                    self.macroAgent[idx].cur_macro_action_done = False
                        
                        if (MACROACTIONNAME[macro_action] == "go to knife 1"\
                        or MACROACTIONNAME[macro_action] == "go to knife 2") and not agent.holding:
                            primitive_action = ACTIONIDX["stay"]

            primitive_actions.append(primitive_action)
        return primitive_actions
           
    # A star
    def _navigate(self, agent, target_x, target_y):
        q = PriorityQueue()
        q.put(AStarAgent(agent.x, agent.y, 0, self._calDistance(agent.x, agent.y, target_x, target_y), None, []))
        isVisited = [[False for col in range(self.ylen)] for row in range(self.xlen)]
        isVisited[agent.x][agent.y] = True

        while not q.empty():
            agent = q.get()
            for action in range(4):
                new_x = agent.x + DIRECTION[action][0]
                new_y = agent.y + DIRECTION[action][1]
                new_name = ITEMNAME[self.map[new_x][new_y]] 

                if not isVisited[new_x][new_y]:
                    init_action = None
                    if agent.action is not None:
                        init_action = agent.action
                    else:
                        init_action = action

                    if new_name == "space" or new_name == "agent":
                        g = agent.g + 1
                        f = g + self._calDistance(new_x, new_y, target_x, target_y)
                        q.put(AStarAgent(new_x, new_y, g, f, init_action, agent.history_action + [action]))
                        isVisited[new_x][new_y] = True
                    elif new_x == target_x and new_y == target_y:
                        if self.debug:
                            print("agent.history_action", agent.history_action)
                        return init_action
        #self.macroAgent[idx].cur_macro_action_done = True
        #if no path is found, stay
        return ACTIONIDX["stay"]


                    
    def _calDistance(self, x, y, target_x, target_y):
        return abs(target_x - x) + abs(target_y - y)
    
    def _calItemDistance(self, agent, item):
        return abs(item.x - agent.x) + abs(item.y - agent.y)

    def _collectCurMacroActions(self):
        # loop each agent
        cur_mac = []
        for agent in self.macroAgent:
            cur_mac.append(agent.cur_macro_action)
        return cur_mac


    def _computeMacroActionDone(self):
        # loop each agent
        mac_done = []
        for agent in self.macroAgent:
            mac_done.append(agent.cur_macro_action_done)
        return mac_done

    def _get_macro_obs(self, cur_obs):
        for agent in self.macroAgent:
            if agent.cur_macro_action_done == None:
                agent.reset()
                agent.cur_macro_obs = cur_obs 
                


    def get_avail_actions(self):
        # return list[1….]
        return [True for i in self.agent]





class MacEnvWrapper(Wrapper):
    def __init__(self, env):
        super(MacEnvWrapper, self).__init__(env)

    @property
    def n_agent(self): return 2

    @property
    def obs_size(self): return

    @property
    def n_action(self): return

    def reset(self): self.env.reset()

    def step(self, macro_actions):
    
        obs, reward, done, info = self.env.run(macro_actions)
          
        return obs, reward, done, info

    def action_space_sample(self):
        return self.env.macro_action_sample() 

    def get_avail_actions(self):
        return self.env.get_avail_actions()

