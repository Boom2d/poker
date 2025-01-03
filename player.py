class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0
        self.bank = 0
        self.combination = ''

    def add_card_to_hand(self, card):
        self.hand.append(card)

    def set_hand(self, hand):
        self.hand = hand

    def reset_hand(self):
        self.score = 0

    def set_score(self, score):
        self.score = score

    def reset_score(self):
        self.score = 0

    def set_bank(self, bank):
        self.bank = bank

    def __str__(self):
        return (f"Player: {self.name}\n"
                f"Hand: {self.hand}\n"
                f"Score: {self.score}\n"
                f"Bank: ${self.bank}")