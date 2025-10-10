'''
Coin flip simulation.
you can flip a coin to get heads or tails.
and flip multiple coins at once.

by aiwonderland
Date: 2025-09-27



'''

from error import CoinSideNotTwoError
from error import CoinFlipNotNumberError
from error import CoinFlipTooManyError




import random

class Coin:
    def __init__(self, coinnumber):
        '''Initialize a coin with two sides: "Heads" and "Tails".'''
        self.sides = ["Heads", "Tails"]
        self.coin_number = coinnumber
        if not isinstance(coinnumber, int) or coinnumber <= 0:
            raise CoinSideNotTwoError("Number of coins must be a positive integer.")
        
    
    def flip(self, times=1):
        '''
        Flip the coin a specified number of times.
        times: int - number of flips (default is 1)
        Returns a list of results.
        '''
        if not isinstance(times, int) or times <= 0:
            raise CoinFlipNotNumberError("Number of flips must be a positive integer.")
        elif times > 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:
            raise CoinFlipTooManyError("Number of flips is too large.")

        results = []
        for _ in range(self.coin_number):
            results.append([random.choice(self.sides) for _ in range(times)])
        return results
    
    def __repr__(self):
        '''
        Return a formal string representation of the coin.
        '''
        return f"Coin(coin_number={self.coin_number})"

    def __str__(self):
        '''
        Return a string representation of the coin.
        '''
        return f"Coin with {self.coin_number} sides: {self.sides}"
    
    def __eq__(self, value):
        if not isinstance(value, Coin):
            return False
        return self.coin_number == value.coin_number and self.sides == value.sides


# ==========================================================================================
# Test the Coin class

def test():
    coin1 = Coin(1)
    print(coin1.flip(5))  # Flip one coin 5 times

    coin2 = Coin(3)
    print(coin2.flip(4))  # Flip three coins 4 times each

if __name__ == "__main__":
    test()
