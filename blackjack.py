import pygame
import random
import itertools
import argparse

from utils import calculate_hand_value
from dealer import DealerPlayer
from player import Player
from PlayerRL import RLAgent 

# Initialize Pygame
pygame.init()

# Game window settings
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Simple Blackjack')

# Load images (Manteve-se o carregamento, mas só será usado se render_mode=True)
dealer_portrait_img = pygame.image.load('portrait/dealer.png')
winner_image = pygame.transform.scale(
    pygame.image.load('symbols/winner.png'),
    (200, 200)
)

card_images = {}
suits = ['hearts', 'diamonds', 'clubs', 'spades']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

player_portrait = None
dealer_portrait = pygame.transform.scale(dealer_portrait_img, (80, 160))

# Carregamento das cartas
for suit in suits:
    for value in values:
        image_scale = 0.5
        # Certifique-se que o caminho das imagens existe
        try:
            card_img = pygame.image.load(f'cards/{value}_of_{suit}.png')
            scaled_card = pygame.transform.scale(
                card_img,
                (int(200 * image_scale), int(300 * image_scale))
            )
            card_images[(suit, value)] = scaled_card
        except FileNotFoundError:
            pass # Ignora se não tiver as imagens para testar lógica

# Draw card function
def draw_card(deck, hand):
    card = random.choice(deck)
    hand.append(card)
    deck.remove(card)
    return card

def render_card(card, pos):
    if (card.suit, card.value) in card_images:
        screen.blit(card_images[(card.suit, card.value)], pos)

def render_hand(hand, pos):
    for idx, c in enumerate(hand):
        if (c.suit, c.value) in card_images:
            screen.blit(card_images[(c.suit, c.value)], pos)
        pos = (pos[0] + 120, pos[1])

def render_portrait(portrait, pos):
    if portrait:
        screen.blit(portrait, pos)

class Card:
    def __init__(self, suit, value):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f'[{self.value}-{self.suit}]'

# --- ALTERAÇÃO AQUI: Adicionado parametro render_mode ---
def play_blackjack(player, render_mode=True):
    running = True
    player_turn = False  
    dealer_turn = True

    reroll_used = False

    deck = [Card(s, v) for s, v in itertools.product(suits, values)]
    player_hand = []
    dealer_hand = []
    hand_result = 0

    player_wins = 0
    player_busts = 0
    draws = 0

    random.shuffle(deck)

    # Loop principal do jogo
    while running:
        # Eventos do Pygame (Necessário mesmo em headless para o sistema não travar se o user tentar fechar)
        if render_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return 0 # Sai forçado

        # Lógica do Jogo (Mantida intacta)
        if dealer_turn:
            dealer_value = calculate_hand_value(dealer_hand)
            if dealer_value < 17:
                draw_card(deck, dealer_hand)
            else:
                dealer_turn = False
                player_turn = True

        elif player_turn:
            decision = player.decision(player_hand, dealer_hand if dealer_hand else None)
            
            if decision == "hit":
                draw_card(deck, player_hand)

            elif decision == "reroll":
                if reroll_used:
                    player_turn = False 
                else:
                    current_cards = len(player_hand)
                    if current_cards > 0:
                        player_hand.clear()
                    for _ in range(current_cards + 1):
                      draw_card(deck, player_hand)
                    reroll_used = True

            else:
                player_turn = False

            if calculate_hand_value(player_hand) >= 21:
                player_turn = False

            if not player_turn:
                player_value = calculate_hand_value(player_hand)
                dealer_value = calculate_hand_value(dealer_hand) # Recalcula pois dealer já jogou
                
                if decision == "reroll" and reroll_used:
                    hand_result = -1
                elif player_value > 21:
                    hand_result = -1
                    player_busts = 1
                elif dealer_value > 21:
                    hand_result = +1
                    player_wins = 1
                elif player_value >= dealer_value:
                    hand_result = +1
                    player_wins = 1
                elif player_value == dealer_value:
                    hand_result = 0
                    draws = 1
                else:
                    hand_result = -1
                running = False

            # O print pode ser mantido ou removido, mas para headless puro geralmente removemos
            # print(f"Dealer hidden hand ({dealer_value}): {dealer_hand}")
            rerolls = 1 if reroll_used else 0
            # Chama o result do agente
            #alteracao inserir dealer hand na análise
            dealer_sum = dealer_hand if dealer_hand else None
            player.result(player_hand, dealer_sum, decision, hand_result, player_turn)

        # --- ALTERAÇÃO AQUI: Renderização Condicional ---
        if render_mode:
            screen.fill((0, 0, 0))
            render_hand(player_hand, (150, 100))
            render_hand(dealer_hand, (150, 300))
            render_portrait(player_portrait, (50, 100))
            render_portrait(dealer_portrait, (50, 300))
            pygame.display.flip() 
            pygame.time.wait(10) # Delay visual
        else:
            # Em modo headless, não esperamos, o loop roda o mais rápido possível
            pass

    if render_mode:
        pygame.time.wait(10)

    return hand_result, player_wins, player_busts, rerolls, draws

def play_n_rounds(player, n, render_mode=False):
    results = []
    total_wins = 0
    total_busts = 0
    total_rerolls = 0
    total_draws = 0

    for i in range(n):
        # Opcional: imprimir progresso a cada X rodadas para não parecer travado
        if not render_mode and i % 1000 == 0:
            print(f"Treinando... rodada {i}/{n}")

        # CHAMA O JOGO E COLETA O RESULTADO EM TODAS AS RODADAS (CORREÇÃO DE INDENTAÇÃO)
        hand_result, player_wins, player_busts, rerolls, draws = play_blackjack(player, render_mode=render_mode)
        
        # AGREGAÇÃO EM TODAS AS RODADAS
        results.append(hand_result)
        total_wins += player_wins
        total_busts += player_busts
        total_rerolls += rerolls
        total_draws += draws

    if not results:
        # Garante que não haverá erro se o loop for interrompido muito cedo (embora não deva acontecer)
        return {
            "EV": 0.0, "Std_Dev": 0.0, "Win_Rate": 0.0,
            "Draw_Rate": 0.0, "Bust_Rate": 0.0, "Reroll_Usage": 0.0
        }

    import numpy as np
    import statistics
    
    ev = statistics.fmean(results)
    
    # Métricas de Taxa
    win_rate = total_wins / n
    bust_rate = total_busts / n
    reroll_usage = total_rerolls / n
    draw_rate = total_draws / n
    
    # Métrica de Volatilidade
    std_dev = np.std(results)
    
    return {
        "EV": ev,
        "Std_Dev": std_dev,
        "Win_Rate": win_rate,
        "Draw_Rate": draw_rate,
        "Bust_Rate": bust_rate,
        "Reroll_Usage": reroll_usage
    }
def parse_args():
    parser = argparse.ArgumentParser(description="Simple Blackjack with RL / baseline player")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--player", type=str, choices=["rl", "base"], default="rl")
    return parser.parse_args()

def main():
    args = parse_args()
    global player_portrait
    
    if args.seed is not None:
        random.seed(args.seed)

    if args.player == "rl":
        try:
            player_portrait = pygame.transform.scale(pygame.image.load('portrait/rl.png'), (80, 160))
        except: pass
        player = RLAgent()
    else:
        try:
            player_portrait = pygame.transform.scale(pygame.image.load('portrait/random.png'), (80, 160))
        except: pass
        player = Player()

    # Treinamento
    training_metrics = play_n_rounds(player, 1000, render_mode=False) 

    # Validação
    real_metrics = play_n_rounds(player, 100, render_mode=True) 

    print("\n--- Resultados do Treinamento ---")
    print(f"EV: {training_metrics['EV']:.4f}, Desv. Padrão: {training_metrics['Std_Dev']:.4f}")
    print(f"Taxa de Vitórias: {training_metrics['Win_Rate']:.2%}")
    print(f"Taxa de Bust: {training_metrics['Bust_Rate']:.2%}")
    print(f"Uso do Reroll: {training_metrics['Reroll_Usage']:.2%}")
    
    print("\n--- Resultados da Validação ---")
    print(f"EV: {real_metrics['EV']:.4f}, Desv. Padrão: {real_metrics['Std_Dev']:.4f}")
    print(f"Taxa de Vitórias: {real_metrics['Win_Rate']:.2%}")
    print(f"Taxa de Bust: {real_metrics['Bust_Rate']:.2%}")
    print(f"Uso do Reroll: {real_metrics['Reroll_Usage']:.2%}")
    
    # Mantém a janela aberta um pouco no final
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()