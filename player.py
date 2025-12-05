import random 
from utils import calculate_hand_value

 ######################################
 #
 # Seu agente deve ser colocado nessa região
 # Lembre-se que a regra do blackjack foi modificada
 # nesse versão o dealer joga primeiro que você
 # e você joga vendo a primeira carta dele
 #
 #
class Player:
  # Essa função toma a decisão após observar
  # o estado observável do campo
  def decision(self, your_hand, dealer_first_card):
    player_hand = [d for d in your_hand]
    print("======== Start of turn =======")
    print(f"Player hand: {player_hand} vs dealer {dealer_first_card}, ...", ) 
    choice = random.choice(["hit", "stop", "reroll"])
    print(f"You made the decision '{choice}'")
    return choice

  # Essa função deveria utilizar o resultado para 
  # atualizar a QTable
  def result(self, your_hand, dealer_first_card, decision, reward, is_not_done):
    player_hand = [d for d in your_hand]
    game_status = "still going" if is_not_done else "is done" 
    print(f"Your hand ({calculate_hand_value(your_hand)}) after decision '{decision}' with {reward=} and game {game_status}")
    if not is_not_done:
      print("======== End of turn =======")
