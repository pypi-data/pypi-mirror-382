"""A module for Bài cào — a Vietnamese basic card game

Classes: `Pack`, `BaiCao`"""

import random

class Pack:
    def create_pack(self):
        """Creates a Standard 52-card pack, resets the pack if it already exists"""
        self.pack = ["A♠","2♠","3♠","4♠","5♠","6♠","7♠","8♠","9♠","10♠","J♠","Q♠","K♠",
                     "A♣","2♣","3♣","4♣","5♣","6♣","7♣","8♣","9♣","10♣","J♣","Q♣","K♣",
                     "A♦","2♦","3♦","4♦","5♦","6♦","7♦","8♦","9♦","10♦","J♦","Q♦","K♦",
                     "A♥","2♥","3♥","4♥","5♥","6♥","7♥","8♥","9♥","10♥","J♥","Q♥","K♥"]
    def view_pack(self):
        """Returns all cards"""
        return self.pack
    def shuffle_pack(self):
        """Shuffles the pack"""
        random.shuffle(self.pack)

class BaiCao(Pack):
    def deal(self, amount_hands: int):
        """Creates an amount of hands based on the parameter `amount_hands`

        Note: If you have already created a list of hands,
        it's recommended to use the `create_pack()` method to reset the pack"""
        self.hands = []
        for x in range(0, amount_hands): self.hands.append([self.pack.pop(0), self.pack.pop(0), self.pack.pop(0)])
    def view_hand(self, hand_number: int):
        """Returns all cards on a hand based on the parameter `hand_number`"""
        return self.hands[hand_number]
    def calculate(self, hand_number: int):
        """Calculates the points of a created hand based on the parameter `hand_number`,
        returns "Ba cào!!!" or an integer from 0—9"""
        ranks = [card[:-1] for card in self.hands[hand_number]]
        if all(x in ["J", "Q", "K"] for x in ranks): return "Ba cào!!!"
        values = 0
        for x in ranks:
            if x in ["J", "Q", "K"]: values += 10
            elif x == "A": values += 1
            else: values += int(x)
        return values % 10

