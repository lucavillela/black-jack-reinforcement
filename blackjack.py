import pygame
import random
import itertools
import argparse

from utils import calculate_hand_value
from dealer import DealerPlayer
from player import Player
from PlayerRL import RLAgent  # RL player


# Initialize Pygame
pygame.init()

# Game window settings
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Simple Blackjack')

# Load character portraits
portraits = [
    #pygame.image.load('portrait/1.png'),
    #pygame.image.load('portrait/2.png'),
]

dealer_portrait_img = pygame.image.load('portrait/dealer.png')

winner_image = pygame.transform.scale(
    pygame.image.load('symbols/winner.png'),
    (200, 200)
)

# Load card images (assuming we have basic card images named as '2_of_clubs.png', '3_of_hearts.png', etc.)
card_images = {}
suits = ['hearts', 'diamonds', 'clubs', 'spades']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

player_portrait = None
dealer_portrait = pygame.transform.scale(dealer_portrait_img, (80, 160))

for suit in suits:
    for value in values:
        image_scale = 0.5
        card_img = pygame.image.load(f'cards/{value}_of_{suit}.png')
        scaled_card = pygame.transform.scale(
            card_img,
            (int(200 * image_scale), int(300 * image_scale))
        )
        card_images[(suit, value)] = scaled_card


# Card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'jack': 10, 'queen': 10, 'king': 10,
    'ace': [1, 11]
}


# Draw card function
def draw_card(deck, hand):
    card = random.choice(deck)
    hand.append(card)
    deck.remove(card)
    return card


def render_card(card, pos):
    screen.blit(card_images[(card.suit, card.value)], pos)


def render_hand(hand, pos):
    for idx, c in enumerate(hand):
        screen.blit(card_images[(c.suit, c.value)], pos)
        pos = (pos[0] + 120, pos[1])


def render_portrait(portrait, pos):
    screen.blit(portrait, pos)


def render_winner(pos):
    screen.blit(winner_image, pos)


class Card:
    def __init__(self, suit, value):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f'[{self.value}-{self.suit}]'


# Main game loop
def play_blackjack(player):
    running = True
    player_turn = False  # True if it's player's turn, False for dealer's turn
    dealer_turn = True

    # reroll can be used once per match
    reroll_used = False

    # Create a deck of cards and deal initial hands
    deck = [Card(s, v) for s, v in itertools.product(suits, values)]
    player_hand = []
    dealer_hand = []
    hand_result = 0
    random.shuffle(deck)

    # (If you want initial dealing, add here)
    # draw_card(deck, player_hand)
    # draw_card(deck, player_hand)
    # draw_card(deck, dealer_hand)
    # draw_card(deck, dealer_hand)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear screen (black background)

        if dealer_turn:
            # Dealer's turn logic
            dealer_value = calculate_hand_value(dealer_hand)
            if dealer_value < 17:
                draw_card(deck, dealer_hand)
            else:
                dealer_turn = False
                player_turn = True

        elif player_turn:
            # Player's turn logic
            decision = player.decision(player_hand, dealer_hand[0])
            
            if decision == "hit":
                draw_card(deck, player_hand)

            elif decision == "reroll":
                # Use reroll only once per match
                if reroll_used:
                    player_turn = False 
                else:
                    current_cards = len(player_hand)
                    if current_cards > 0:
                        # Discard all current cards
                        player_hand.clear()
                    # Draw current_cards + 1 new cards
                    for _ in range(current_cards + 1):
                      draw_card(deck, player_hand)
                    # Mark reroll as used (even if hand was empty)
                    reroll_used = True
                # Player keeps their turn after reroll, so we do NOT set player_turn = False here

            else:
                # stand or any other non-handling decision
                player_turn = False

            if calculate_hand_value(player_hand) >= 21:
                player_turn = False

            

            if not player_turn:
                # Compare hands and decide winner
                player_value = calculate_hand_value(player_hand)
                if decision == "reroll" and reroll_used:
                    hand_result = -2
                elif player_value > 21:
                    hand_result = -1
                elif dealer_value > 21:
                    hand_result = +1
                elif player_value >= dealer_value:
                    hand_result = +1
                elif player_value == dealer_value:
                    hand_result = 0
                else:
                    hand_result = -1
                running = False

            print(f"Dealer hidden hand ({dealer_value}): {dealer_hand}")
            decision = player.result(player_hand, dealer_hand[0], decision, hand_result, player_turn)

        render_hand(player_hand, (150, 100))
        render_hand(dealer_hand, (150, 300))
        render_portrait(player_portrait, (50, 100))
        render_portrait(dealer_portrait, (50, 300))
        pygame.display.flip()  # Update the display
        pygame.time.wait(10)

    # Durante treinamento você deve 
    # remover esse delay para acelerar o treinamento
    pygame.time.wait(10)

    return hand_result


def play_n_rounds(player, n):
    results = []
    for _ in range(n):
        results.append(play_blackjack(player))
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Simple Blackjack with RL / baseline player")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed used for the run"
    )
    parser.add_argument(
        "--player",
        type=str,
        choices=["rl", "base"],
        default="rl",
        help="Which player to use: 'rl' for PlayerRL.RLAgent (default), 'base' for player.Player"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    global player_portrait
    # Seed control
    if args.seed is not None:
        random.seed(args.seed)

    # Player selection
    if args.player == "rl":
        player_portrait = pygame.transform.scale(pygame.image.load('portrait/rl.png'), (80, 160))
        player = RLAgent()
    else:
        player_portrait = pygame.transform.scale(pygame.image.load('portrait/random.png'), (80, 160))
        player = Player()

    # Training and evaluation
    training_score = play_n_rounds(player, 1000)
    real_score = play_n_rounds(player, 100)

    import statistics
    print(
        f"Player Expected Value was {statistics.fmean(real_score)} "
        f"({statistics.fmean(training_score)} on training)"
    )
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    main()

