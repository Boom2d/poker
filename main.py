from player import Player
from dealer import Dealer

def evaluate_hand(player_hand, table_cards):
    return player_hand + table_cards

# Game setup
def play_texas_holdem():
    dealer = Dealer()
    dealer.shuffle_deck()

    # Deal two hole cards to each player
    player1 = Player('Bot1')
    player2 = Player('Bot2')

    player1.set_hand(dealer.deal_cards(2))
    player2.set_hand(dealer.deal_cards(2))

    # Deal five community cards
    table_cards = dealer.deal_cards(5)

    # Show hands and community cards
    print(f"{player1.name}'s hand:", player1.hand)
    print(f"{player2.name}'s hand:", player2.hand)
    print("Community cards:", table_cards)

    print(f"{player1.name}'s full hand:", player1.hand + table_cards)
    print(f"{player2.name}'s full hand:", player2.hand + table_cards)

    player1.set_score(dealer.calc_score(player1.hand + table_cards))
    player2.set_score(dealer.calc_score(player2.hand + table_cards))

    # Compare hands (placeholder logic)
    # In real poker, you'd rank hands properly
    if player1.score > player2.score:
        print(f"{player1.name} win! score: {player1.score}")
    else:
        print(f"{player2.name} win! score: {player2.score}")


if __name__ == "__main__":
    play_texas_holdem()
