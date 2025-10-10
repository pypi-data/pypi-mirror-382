'''
A target selection system in Python
You can make a target like:
[[2,2,2],
[2,1,2],
[2,2,2]]
or
[[3,3,3,3,3,3],
[3,2,2,2,2,3],
[3,2,1,1,2,3],
[3,2,1,1,2,3],
[3,2,2,2,2,3],
[3,3,3,3,3,3]]
You can also make a target with any size you want.
It's very easy to use.
============================
Author: aiwonderland
Date: 2025-09-29
============================
'''
from error import TargetSizeNotNumberError
from error import TargetShootNotNumberError
from error import TargetRandomShotNotBooleanError
from error import TargetOutOfBoundsError



from random import randint



class Target:
    def __init__(self, size=3):
        '''Initialize a target with a specified size (default is 3).
        The target will be a square matrix with concentric layers.
        size: int - size of the target (must be a positive integer)
        '''
        if not isinstance(size, int) or size <= 0:
            raise TargetSizeNotNumberError("Size must be a positive integer.")
        self.size = size
        self.target = self._create_target(size)


    def _create_target(self, size):
        '''Create a target matrix of given size.'''
        target = [[0] * size for _ in range(size)]
        layers = (size + 1) // 2
        for layer in range(layers):
            value = layers - layer
            for i in range(layer, size - layer):
                for j in range(layer, size - layer):
                    target[i][j] = value
        return target
    
    def copy_target(self):
        '''Return a copy of the target matrix.'''
        return 


    def get_target(self):
        '''Return the target matrix.'''
        return self.target


    def shoot(self, x, y,*,random_shot=False):
        '''Simulate a shot at the target at coordinates (x, y).
        You can also set random_shot to True to shoot at a random position.
        Returns the score based on the target value at that position.
        '''
        # validate random_shot type first
        if not isinstance(random_shot, bool):
            raise TargetRandomShotNotBooleanError("random_shot must be a boolean.")
        if random_shot:
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)

        # validate coordinate types
        if not isinstance(x, int) or not isinstance(y, int):
            raise TargetShootNotNumberError("x and y must be integers.")

        if not (0 <= x < self.size and 0 <= y < self.size):
            raise TargetOutOfBoundsError("Coordinates out of bounds.")
        return self.target[y][x]  # Note: y is row index, x is column index
    

    def __repr__(self):
        '''Return a formal string representation of the target.'''
        return f"Target(size={self.size})"


    def __str__(self):
        '''Return a string representation of the target matrix.'''
        return '\n'.join([' '.join(map(str, row)) for row in self.target])
    
    def __eq__(self, value):
        if not isinstance(value, Target):
            return False
        return self.size == value.size and self.target == value.target
    

# ==========================================================================================
# Test the Target class

def test():
    target3 = Target(3)
    print(target3)
    print("Shooting at (1,1):", target3.shoot(1, 1))  # Center shot

    target6 = Target(6)
    print(target6)
    print("Shooting at (0,0):", target6.shoot(0, 0))  # Corner shot
    print("Shooting at (2,2):", target6.shoot(2, 2))  # Inner layer shot

    target5 = Target(5)
    print(target5)

    print("Shooting at (4,4):", target5.shoot(4, 4))  # Edge shot
    print("Shooting at (2,2):", target5.shoot(2, 2))  # Center shot
    print("Shooting at (1,3):", target5.shoot(1,3))  # Middle layer shot

if __name__ == "__main__":
    test()

'''
output:A card deck system in Python
You can create different types of card decks like standard, uno, and tarot.
You can shuffle the deck and draw cards from it.
2 2 2
2 1 2
2 2 2
Shooting at (1,1): 1
3 3 3 3 3 3
3 2 2 2 2 3
3 2 1 1 2 3
3 2 1 1 2 3
3 2 2 2 2 3
3 3 3 3 3 3
Shooting at (0,0): 3
Shooting at (2,2): 1
3 3 3 3 3
3 2 2 2 3
3 2 1 2 3
3 2 2 2 3
3 3 3 3 3
Shooting at (4,4): 3
Shooting at (2,2): 1
Shooting at (1,3): 2
'''