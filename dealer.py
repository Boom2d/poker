class Dealer:
    ALL_CARDS = ['2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♥',
                 '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦',
                 '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♠',
                 '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣']
    SUITS = ['♥', '♦', '♠', '♣']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    RANK_SCORE = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                  '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self):
        self.deck = Dealer.ALL_CARDS.copy()

    def create_deck(self):
        return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

    def shuffle_deck(self):
        import random
        random.shuffle(self.deck)
        return self.deck

    def deal_cards(self, num_cards):
        return [self.deck.pop() for _ in range(num_cards)]

    def is_flush(self, hand):
        suits = [card[-1] for card in hand]

        # Check if all suits are the same
        return len(set(suits)) == 1

    def is_straight(self, hand):
        ranks = [card[0:-1] for card in hand]
        rank_values = sorted(Dealer.RANK_SCORE[rank] for rank in ranks)

        # Check for regular straight
        if all(rank_values[i] + 1 == rank_values[i + 1] for i in range(len(rank_values) - 1)):
            return True

        # Check for Ace-low straight (Ace, 2, 3, 4, 5)
        if set(rank_values) == {2, 3, 4, 5, 14}:
            return True
        return False

    def convert_to_score(self, hand):
        score_hand = list(map(lambda x: Dealer.RANK_SCORE[x[0:-1]], hand))
        print(f'Hand {hand} converted to {score_hand}')
        return score_hand

    def find_key_by_val(self, val):
        return next((k for k, v in Dealer.RANK_SCORE.items() if v == val), None)

    def calc_pairs(self, hand):
        count_dict = {element: hand.count(element) for element in set(hand)}
        return count_dict;

    def calc_score(self, hand):
        sorted_hand = sorted(hand, key=lambda card: Dealer.RANK_SCORE[card[0:-1]], reverse=True)
        score_list = self.convert_to_score(sorted_hand)
        count_map = self.calc_pairs(score_list);
        sorted_count_map = sorted(count_map.items(), key=lambda item: item[1], reverse=True)

        if (self.is_flush(hand) and sum(score_list) == 60):
            combination = 'Royal flush'
            return 60 * 100, combination
        elif (self.is_flush(hand) and self.is_straight(hand)):
            combination = 'Straight flush'
            return sum(score_list) * 90, combination
        elif (sorted_count_map[0][1] == 4):
            print(f'Four of a kind! {self.find_key_by_val(sorted_count_map[0][0])}')
            return sum(score_list) * 80
        elif (sorted_count_map[0][1] == 3 and sorted_count_map[1][1] == 2):
            combination = f'Full house {self.find_key_by_val(sorted_count_map[0][0])} and {self.find_key_by_val(sorted_count_map[1][0])}'
            return sum(score_list) * 70, combination
        elif (self.is_flush(hand)):
            combination = f'Flush {sorted_hand[0]}'
            return sum(score_list) * 60, combination
        elif (self.is_straight(hand)):
            combination = f'Straight {sorted_hand[0]}'
            return sum(score_list) * 50, combination
        elif (sorted_count_map[0][1]  == 3):
            combination = f'Set {self.find_key_by_val(sorted_count_map[0][0])}'
            return sum(score_list) * 40, combination
        elif (sorted_count_map[0][1] == 2 and sorted_count_map[1][1] == 2):
            combination = f'Two pairs {self.find_key_by_val(sorted_count_map[0][0])} and {self.find_key_by_val(sorted_count_map[1][0])}'
            return sum(score_list) * 30, combination
        elif (sorted_count_map[0] == 1):
            combination = f'One pair {self.find_key_by_val(sorted_count_map[0])}'
            return sum(score_list) * 20, combination
        else:
            combination = f'High card {sorted_hand[0]}'
            return sum(score_list), combination
