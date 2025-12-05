
# Card values
card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
               'jack': 10, 'queen': 10, 'king': 10, 'ace': [1, 11]}

# Function to calculate hand value
def calculate_hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        if card.value == 'ace':
            ace_count += 1
        else:
            value += card_values[card.value]

    for _ in range(ace_count):
        if value + 11 <= 21:
            value += 11
        else:
            value += 1

    return value

