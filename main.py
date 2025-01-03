from player import Player
from dealer import Dealer

def play_texas_holdem():
    dealer = Dealer()
    dealer.shuffle_deck()

    player1 = Player('Bot1')
    player2 = Player('Bot2')
    player3 = Player('Bot3')

    player1.set_hand(dealer.deal_cards(2))
    player2.set_hand(dealer.deal_cards(2))
    player3.set_hand(dealer.deal_cards(2))

    # Deal five community cards
    table_cards = dealer.deal_cards(5)

    # Show hands and community cards
    print(f"{player1.name}'s hand:", player1.hand)
    print(f"{player2.name}'s hand:", player2.hand)
    print(f"{player3.name}'s hand:", player3.hand)
    print("Community cards:", table_cards)

    print(f"{player1.name}'s full hand:", player1.hand + table_cards)
    print(f"{player2.name}'s full hand:", player2.hand + table_cards)
    print(f"{player3.name}'s full hand:", player3.hand + table_cards)

    player1.score, player1.combination = dealer.calc_score(player1.hand + table_cards);
    player2.score, player2.combination = dealer.calc_score(player2.hand + table_cards);
    player3.score, player3.combination = dealer.calc_score(player3.hand + table_cards);

    player_list = [player1, player2, player3]
    winner = max(player_list , key=lambda player: player.score)
    print(f"{winner.name} wins! combination: {winner.combination} score: {winner.score}")


if __name__ == "__main__":
    play_texas_holdem()
