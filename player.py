from enum import Enum

class Player:
    def __init__(self, name):
        self.id = ''
        self.name = name
        self.hand = []
        self.score = 0
        self.bank = 1000
        self.bid = 0
        self.pos = 0
        self.combination = ''
        self.action = Action.NONE

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

    def set_action(self, action):
        self.action = action

    def set_id(self, id):
        self.id = id

    def __str__(self):
        return (f"Player: {self.name}\n"
                f"Hand: {self.hand}\n"
                f"Action: {self.action}\n"
                f"Bid: {self.bid}\n"
                f"Score: {self.score}\n"
                f"Bank: ${self.bank}")

class Action(Enum):
    NONE = 'None'
    CHECK = 'Check'
    CALL = 'Call'
    RAISE = 'Raise'
    FOLD = 'Fold'
    ALL_IN = 'All_In'