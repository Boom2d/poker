class Dealer:
    ALL_CARDS = ['2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♥', '2♦', '3♦', '4♦', '5♦',
                 '6♦',
                 '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦', '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠',
                 'J♠', 'Q♠', 'K♠', 'A♠', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣']
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

    def is_straight_with_ace(self, hand):
        ranks = [card[0:-1] for card in hand]
        rank_values = sorted(RANK_SCORE[rank] for rank in ranks)

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

    def calc_pairs(self, hand):
        count_dict = {element: hand.count(element) for element in set(hand)}
        return count_dict;

    def calc_score(self, hand):
        sorted_hand = sorted(hand, key=lambda card: Dealer.RANK_SCORE[card[0:-1]], reverse=True)
        score_list = self.convert_to_score(sorted_hand)
        count_map = self.calc_pairs(score_list);
        # Pair
        four = 0
        three = 0
        pair = 0
        for val in count_map.values():
            if val == 4:
                four += 1
            elif val == 3:
                three += 1
            elif val == 2:
                pair += 1
        if (four == 1):
            print('Four of a kind!')
            return sum(score_list) * 6
        if (three == 1 and pair == 0):
            print('Full house')
            return sum(score_list) * 5
        elif (three == 1):
            print('Set')
            return sum(score_list) * 4
        elif (pair == 2):
            print('Two pairs')
            return sum(score_list) * 3
        elif (pair == 1):
            print('One pair')
            return sum(score_list) * 2
        else:
            print(f'High card {sorted_hand[0]}')
            return sum(score_list)

    # Combination
    # COMBINATION = ['RF', 'FH', 'cherry', 'date']
    # Four of a Kind: 4 cards of one rank, 1 of another.
    # Full House: 3 cards of one rank, 2 of another.
    # Three of a Kind: 3 cards of one rank, 2 singletons.
    # Two Pair: 2 cards of one rank, 2 of another, 1 singleton.
    # One Pair: 2 cards of one rank, 3 singletons.
    # High Card: No pairs, no special hand.
