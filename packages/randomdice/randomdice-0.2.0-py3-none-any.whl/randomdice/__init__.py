'''
randomdice™ 
----------------------------------------
A Python package for generating random dice rolls.
And a few other things.
like a coin flip.
or a turntable.
and card and target!
Our module has many functions. 
So if you encounter any problems, please give me more advice,
 and I will hurry to correct them.
============================
Author: aiwonderland
Date: 2025-10-01
============================

'''

from .die import Die
from .coin import Coin
from .spinwheel import SpinWheel
from .card import Card
from .target import Target



__version__ = "0.2.0"
__author__ = "aiwonderland"
__license__ = "MIT"
__all__ = ["Die", "Coin", "SpinWheel", "Card", "Target"]