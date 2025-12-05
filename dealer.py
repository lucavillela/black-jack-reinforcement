import pygame
import random
import itertools
from utils import calculate_hand_value

class DealerPlayer:
  def decision(self, your_hand, dealer_hand):
    dealer_value = calculate_hand_value(dealer_hand)
    if dealer_value < 17:
      return "hit"
    else:
      return "stop"

  def result(self, your_hand, dealer_hand, decision, reward, is_not_done):
    dealer_hand = [d for d in your_hand]
    print(f"Dealer hidden hand: {dealer_hand}")
