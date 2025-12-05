import random
from collections import defaultdict
import numpy as np
from utils import calculate_hand_value

class RLAgent:
  def __init__(self):
  
    # Learning rate - 
    self.alpha = 0.1
    # Discount factor - Balanço entre priorizar recompensas futuras e atuais
    self.gamma = 0.9
    # Exploration rate - epsilon greedy
    self.epsilon = 1
    self.epsilon_min = 0.01
    self.epsilon_decay = 0.9995 # decai exploracao com cada rodada
    # Lembrando a ultima acao
    self.last_opponent_action = None
    # Flag indicando se essa seria a ultima rodada
    self.last_round = False   
    # Q table
    self.Q = defaultdict(lambda: [0.0, 0.0, 0.0])
    self.action_list = ["hit", "stop", "reroll"]
    
    self.current_input = None
    self.current_output = None    
    
  def extract_rl_state(self, your_hand, dealer_hand):
    
    player_val = calculate_hand_value(your_hand)
    
    dealer_val = calculate_hand_value(dealer_hand)
    
    reroll_status = self.has_rerolled 

    return (player_val, dealer_val, reroll_status)
 
  def choose_action(self, state):
     
    #
    # Pode ser melhorado!
    #
    if np.random.uniform(0, 1) < self.epsilon:
      # Explore: Choose a random action
      action = np.random.choice(self.action_list)
    else:
      # Exploit: Choose the action with the maximum Q-value
      action = self.action_list[np.argmax(self.Q[state])]
    return action
    
    
  def update_qtable(self, state, action, reward, next_state):
    alp = self.alpha
    gam = self.gamma
    action_index = self.action_list.index(action)
    self.Q[state][action_index] = (1 - alp) * self.Q[state][action_index] + alp * (reward + gam * np.max(self.Q[next_state]))
    if self.epsilon > self.epsilon_min:
        self.epsilon *= self.epsilon_decay  
    
  # Essa função toma a decisão após observar
  # o estado observável do campo
  def decision(self, your_hand, dealer_hand):
    player_hand = [d for d in your_hand]
    if len(player_hand) == 0:
        self.has_rerolled = 0
        
    print("======== Start of turn =======")
    print(f"Player hand: {player_hand} vs dealer {dealer_hand}, ...", ) 
    state = self.extract_rl_state(your_hand=your_hand, dealer_hand=dealer_hand)
    choice = self.choose_action(state)
    print(f"You made the decision '{choice}'")
    return choice

  # Essa função deveria atualiza QTable
  def result(self, your_hand, dealer_hand, decision, reward, is_not_done):
    player_hand = [d for d in your_hand]
    game_status = "still going" if is_not_done else "is done"
    print(f"{your_hand=}")
    state = self.extract_rl_state(your_hand=your_hand[:-1], dealer_hand=dealer_hand)
    next_state = self.extract_rl_state(your_hand=your_hand, dealer_hand=dealer_hand)
    self.update_qtable(state, decision, reward, next_state)
    self.print_q_table(self.Q)
    print(f"Your hand ({calculate_hand_value(your_hand)}) after decision '{decision}' with {reward=} and game {game_status}")

    
    # Apenas retorne ao estado "no rerol" após atualizar a Q-Table
    if decision == "reroll":
      self.has_rerolled = 1
   
    rerolled_status = "rerolled" if self.has_rerolled else "not rerolled" 
    print(f"You have {rerolled_status}")
    print("======== End of turn =======")        
  
  def print_q_table(self, Q):
    for k,v in Q.items():
      print(f"For state={k}")
      for idx, a in enumerate(self.action_list):
        print(f"  Q for {a}", Q[k][idx])
    
  # Nome de seu agente deve ser colocado aqui  
  def get_name(self):
    return "SimpleRL"


