'''
the die module contains the Die class, which represents a die in the game.
you can make a D6,D8 or D12 and so on!
you also can make a die with any number of sides.
and any number of dice's sidesnumber!
it's very easy to use.

Author: aiwonderland
Date: 2025-09-26


'''
from error import InvalidDiceSideNotEvenNumberError
from error import InvalidDieTypeError
from error import InvalidSideValueError
from error import InvalidNumberOfSidesError
from error import InvalidDiceRollNotNumberError




import random

class Die:
    def __init__(self, dietype="D6"):
        '''Initialize a die with a specified type (e.g., "D6", "D8", "D12").
        If no type is specified, defaults to "D6".
        '''
        if not isinstance(dietype, str):
            raise InvalidDieTypeError("Die type must be a string like 'D6', 'D8', 'D12', etc.")
        dt = dietype.upper()
        if not dt.startswith("D"):
            raise InvalidDieTypeError("Invalid die type. Please use format 'D6', 'D8', 'D12', etc.")
        num_str = dt[1:]
        try:
            num = int(num_str)
        except ValueError:
            raise InvalidDieTypeError("Invalid die type number. Use format 'D6', 'D8', etc.")
        if num <= 1:
            raise InvalidNumberOfSidesError("Die must have at least 2 sides (use coin module for 2).")
        self.dietype = f"D{num}"
        self.sides = num
        # sidevalue is optional; only set when DIYdie is used


    def DIYdie(self, sides, sidevalue=None):
        '''
        Create a custom die with a specified number of sides and optional side values.
        sides: int - number of sides on the die
        sidevalue: list or None - optional list of values for each side
        '''
        if not isinstance(sides, int) or sides <= 1:
            raise InvalidNumberOfSidesError("Number of sides must be an integer greater than 1.")
        if sides == 2:
            raise InvalidNumberOfSidesError("You can use the coin module to flip a coin (2-sided).")
        if sidevalue is None:
            self.sidevalue = list(range(1, sides + 1))
        else:
            if not isinstance(sidevalue, (list, tuple)):
                raise TypeError("sidevalue must be a list or tuple of values.")
            if len(sidevalue) != sides:
                raise InvalidSideValueError("Length of sidevalue list must match the number of sides.")
            self.sidevalue = list(sidevalue)

        self.sides = sides
        self.dietype = f"D{self.sides}"

    def require_even_sides(self):
        """Decorator: only allow the wrapped call when this die has an even number of sides."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.sides % 2 != 0:
                    raise InvalidDiceSideNotEvenNumberError("This die must have an even number of sides.")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def roll(self, rolls=1):
        '''
        Roll the die a specified number of times and return the results.
        rolls: int - number of times to roll the die (default is 1)
        '''
        if not isinstance(rolls, int) or rolls <= 0:
            raise InvalidDiceRollNotNumberError("Number of rolls must be a positive integer.")
        
        results = []
        for _ in range(rolls):
            if hasattr(self, 'sidevalue'):
                result = random.choice(self.sidevalue)
            else:
                result = random.randint(1, self.sides)
            results.append(result)
        
        return results if rolls > 1 else results[0]
    
    def __str__(self):
        '''
        Return a string representation of the die.
        '''
        return f"Die(type={self.dietype}, sides={self.sides})"
    
    def __repr__(self):
        '''
        Return a formal string representation of the die.
        '''
        if hasattr(self, 'sidevalue'):
            return f"Die(dietype='{self.dietype}', sidevalue={self.sidevalue})"
        return f"Die(dietype='{self.dietype}')"
    
    def __eq__(self, value):
        if not isinstance(value, Die):
            return False
        return self.dietype == value.dietype and self.sides == value.sides

# ==========================================================================================
# Test the Die class

def test():
    die1 = Die("D6")
    print(die1)
    print(die1.roll(5))

    die2 = Die("D8")
    print(die2)
    print(die2.roll(3))

    die3 = Die()
    print(die3)
    print(die3.roll())

    die4 = Die()
    die4.DIYdie(5, sidevalue=['A', 'B', 'C', 'D', 'E'])
    print(die4)
    print(die4.roll(4))

    def even_roll_test(die):
        @die.require_even_sides()
        def roll_even():
            return die.roll()
        return roll_even()
    
    die5 = Die()
    die5.DIYdie(6)   
    print(die5)
    print(die5.roll(6))

    # call with positional argument (function expects a single parameter named `die`)
    print(even_roll_test(Die("D6")))

if __name__ == "__main__":
    test()

