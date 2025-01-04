from player import Player
from dealer import Dealer

def play_texas_holdem():
    dealer = Dealer()
    dealer.shuffle_deck()

    player_list = []
    player_list.append(Player('Bot1'))
    player_list.append(Player('Bot2'))
    player_list.append(Player('Bot3'))

    for player in player_list:
        player.set_hand(dealer.deal_cards(2))

    table_cards = dealer.deal_cards(5)
    print("Table cards:", table_cards)

    for player in player_list:
        print(f"{player.name}'s full hand:", player.hand + table_cards)
        player.score, player.combination = dealer.calc_score(player.hand + table_cards);
        print(f"{player.name}'s has combination: {player.combination} score: {player.score}")

    max_score = max(player_list , key=lambda player: player.score).score
    win_list = [player for player in player_list if player.score == max_score]
    for player in win_list:
        print(f"{player.name} wins! combination: {player.combination} score: {player.score}")

if __name__ == "__main__":
    play_texas_holdem()
