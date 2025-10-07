'''
all the error classes

by:aiwonderland
Date: 2025-10-06
'''
# =========================================================================================
# die.py
class InvalidDieTypeError(Exception):
    '''Exception raised for invalid die types.'''
    pass

class InvalidSideValueError(Exception):
    '''Exception raised for invalid side values.'''
    pass

class InvalidNumberOfSidesError(Exception):
    '''Exception raised for invalid number of sides.'''
    pass

class InvalidDiceSideNotEvenNumberError(Exception):
    '''Exception raised for dice that do not have an even number of sides.'''
    pass

class InvalidDiceRollNotNumberError(Exception):
    '''Exception raised for invalid dice roll values that are not numbers.'''
    pass

# ========================================================================================
# coin.py
class CoinSideNotTwoError(Exception):
    '''Exception raised when a coin does not have exactly two sides.'''
    pass

class CoinFlipNotNumberError(Exception):
    '''Exception raised when the number of coin flips is not a number.'''
    pass

class CoinFlipTooManyError(Exception):
    '''Exception raised when the number of coin flips exceeds a reasonable limit.'''
    pass

# ========================================================================================
# spinwheel.py
class SpinWheelSizeNotNumberError(Exception):
    '''Exception raised when a spin wheel does not have at least two sectors.'''
    pass

class SpinWheelTooSmallError(Exception):
    '''Exception raised when a spin wheel has fewer than two segments.'''
    pass

class SpinWheelDIYsegmentNoWeightError(Exception):
    '''Exception raised when a DIY segment wheel is created without weights.'''
    pass

class SpinWheelDIYsegmentWeightNotANumberError(Exception):
    
    '''Exception raised when a DIY segment wheel is created with non-numeric weights.'''
    pass

class SpinWheelDIYsegmentSizeNotANumberError(Exception):
    '''Exception raised when a DIY segment wheel is created with a non-numeric segment size.'''
    pass

class SpinWheelDIYsegmentWithWheelNotBooleanError(Exception):
    '''Exception raised when a DIY segment wheel is created with a non-boolean with_wheel value.'''
    pass

class SpinWheelDIYsegmentSizeNotListError(Exception):
    '''Exception raised when a DIY segment wheel is created with a non-list segment size.'''
    pass

class SpinWheelDIYsegmentWeightIs0Error(Exception):
    '''Exception raised when a DIY segment wheel is created with all zero weights.'''
    pass

class SpinWheelSpinNotNumberError(Exception):
    '''Exception raised when the number of spins is not a number.'''
    pass

# ========================================================================================
# card.py
class CardDrawNotNumberError(Exception):
    '''Exception raised when the number of draws is not a number.'''
    pass

class CardDeckTooSmallError(Exception):
    '''Exception raised when the number of decks is less than 1.'''
    pass

class CardDeckInvalidCardError(Exception):
    '''Exception raised when an invalid card is added to the deck.'''
    pass

# ========================================================================================
# target.py
class TargetSizeNotNumberError(Exception):
    '''Exception raised when the target size is not a number.'''
    pass

class TargetRandomShotNotBooleanError(Exception):
    '''Exception raised when the random_shot parameter is not a boolean.'''
    pass

class TargetShootNotNumberError(Exception):
    '''Exception raised when the shoot coordinates are not numbers.'''
    pass

class TargetOutOfBoundsError(Exception):
    '''Exception raised when the shoot coordinates are out of bounds.'''
    pass