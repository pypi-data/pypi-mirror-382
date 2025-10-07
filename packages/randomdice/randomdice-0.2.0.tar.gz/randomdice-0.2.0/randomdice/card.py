'''
a card desk in python
You can use it to draw cards
and shuffle cards
Like UNO,numbers,poker,tarot and so on.

Author: aiwonderland
Date: 2025-9-29

'''
from error import CardDrawNotNumberError
from error import CardDeckInvalidCardError
from error import CardDeckTooSmallError




import random

class Card:
    def __init__(self, deck_type="standard"):
        '''Initialize a card deck.
        deck_type: str - type of deck ("standard", "uno", "tarot")
        '''
        self.deck_type = deck_type.lower()
        if self.deck_type == "standard":
            self.cards = [f"{rank} of {suit}" for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]
                          for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]]
        elif self.deck_type == "uno":
            colors = ["Red", "Yellow", "Green", "Blue"]
            numbers = [str(n) for n in range(0, 10)] + ["Skip", "Reverse", "Draw Two"]
            self.cards = [f"{color} {number}" for color in colors for number in numbers] * 2 + ["Wild", "Wild Draw Four"] * 4
        elif self.deck_type == "tarot":
            major_arcana = [f"Major Arcana {i}" for i in range(22)]
            suits = ["Wands", "Cups", "Swords", "Pentacles"]
            minor_arcana = [f"{rank} of {suit}" for suit in suits
                            for rank in ["Ace"] + [str(n) for n in range(2, 11)] + ["Page", "Knight", "Queen", "King"]]
            self.cards = major_arcana + minor_arcana
        else:
            raise CardDeckInvalidCardError("Unsupported deck type. Use 'standard', 'uno', or 'tarot'.")
        self.shuffle()

    def shuffle(self):
        '''Shuffle the card deck.'''
        random.shuffle(self.cards)

    def draw(self, num=1):
        '''Draw a specified number of cards from the deck.
        num: int - number of cards to draw (default is 1)
        Returns a list of drawn cards.
        '''
        if not isinstance(num, int) or num <= 0:
            raise CardDrawNotNumberError("Number of cards to draw must be a positive integer.")
        if num > len(self.cards):
            raise CardDeckTooSmallError("Not enough cards in the deck to draw the requested number.")

        drawn_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return drawn_cards
    

    def __str__(self):
        '''Return a string representation of the card deck.'''
        return f"Card(deck_type={self.deck_type}, remaining_cards={len(self.cards)})"
    
    def __repr__(self):
        '''Return a formal string representation of the card deck.'''
        return f"Card(deck_type={self.deck_type}, remaining_cards={len(self.cards)})"
    
    def __eq__(self, value):
        if not isinstance(value, Card):
            return False
        return self.deck_type == value.deck_type and self.cards == value.cards
    
# ==========================================================================================
# Test the Card class
def test():
    deck1 = Card("standard")
    print(deck1)
    print(deck1.draw(5))
    print(deck1)

    deck2 = Card("uno")
    print(deck2)
    print(deck2.draw(7))
    print(deck2)

    deck3 = Card("tarot")
    print(deck3)
    print(deck3.draw(3))
    print(deck3)

if __name__ == "__main__":
    test()