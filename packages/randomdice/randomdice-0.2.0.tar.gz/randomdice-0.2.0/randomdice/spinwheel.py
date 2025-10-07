'''
spin wheel simulation.
you can spin a wheel to get a random result.
and spin multiple wheels at once.
and you can customize the wheel segments!

by aiwonderland
Date: 2025-09-27


'''
from error import SpinWheelSizeNotNumberError
from error import SpinWheelTooSmallError
from error import SpinWheelDIYsegmentNoWeightError
from error import SpinWheelDIYsegmentSizeNotANumberError
from error import SpinWheelDIYsegmentWeightNotANumberError
from error import SpinWheelDIYsegmentWithWheelNotBooleanError
from error import SpinWheelDIYsegmentSizeNotListError
from error import SpinWheelDIYsegmentWeightIs0Error
from error import SpinWheelSpinNotNumberError


import random

class SpinWheel:
    def __init__(self, segments=None):
        '''Initialize a spin wheel with specified segments.
        If no segments are provided, defaults to a wheel with 6 numbered segments.
        '''
        if segments is None:
            self.segments = [str(i) for i in range(1, 7)]
        else:
            if not isinstance(segments, (list, tuple)):
                raise SpinWheelSizeNotNumberError("Segments must be a list or tuple of values.")
            if len(segments) < 2:
                raise SpinWheelTooSmallError("A wheel must have at least 2 segments.")
            self.segments = list(segments)
        self.num_segments = len(self.segments)


    def DIYwheel(self, segments):
        '''Customize the wheel with new segments.'''
        if not isinstance(segments, (list, tuple)):
            raise TypeError("Segments must be a list or tuple of values.")
        if len(segments) < 2:
            raise ValueError("A wheel must have at least 2 segments.")
        self.segments = list(segments)
        self.num_segments = len(self.segments)


    def DIYsegments(self, segments, with_wheel):
        '''Customize the wheel segments and return a new SpinWheel instance.'''
        if not isinstance(segments, (list, tuple)):
            raise TypeError("Segments must be a list or tuple of values.")
        if len(segments) < 2:
            raise ValueError("A wheel must have at least 2 segments.")
        if not isinstance(with_wheel, bool):
            raise TypeError("with_wheel must be a boolean value.")
        new_wheel = SpinWheel(segments)
        if with_wheel:
            return new_wheel
        else:
            return new_wheel.segments

    def DIYwheelsegments(self, segments, *, whith_wheel, segment_size, weights=None):
        '''We will use random.choices to create a wheel with weighted segments.'''
        if not isinstance(segments, (list, tuple)):
            raise SpinWheelDIYsegmentSizeNotListError("Segments must be a list or tuple of values.")
        if len(segments) < 2:
            raise ValueError("A wheel must have at least 2 segments.")
        if not isinstance(whith_wheel, bool):
            raise SpinWheelDIYsegmentWithWheelNotBooleanError("with_wheel must be a boolean value.")
        if not isinstance(segment_size, int) or segment_size <= 0:
            raise SpinWheelDIYsegmentSizeNotANumberError("segment_size must be a positive integer.")
        if weights is not None:
            if not isinstance(weights, (list, tuple)):
                raise SpinWheelDIYsegmentNoWeightError("Weights must be a list or tuple of values.")
            if len(weights) != len(segments):
                raise SpinWheelDIYsegmentWeightNotANumberError("Length of weights must match the number of segments.")
            if any(w < 0 for w in weights):
                raise SpinWheelDIYsegmentWeightNotANumberError("Weights must be non-negative.")
            total_weight = sum(weights)
            if total_weight == 0:
                raise SpinWheelDIYsegmentWeightIs0Error("At least one weight must be positive.")
            normalized_weights = [w / total_weight for w in weights]
            expanded_segments = random.choices(segments, weights=normalized_weights, k=segment_size)
        else:
            expanded_segments = random.choices(segments, k=segment_size)
        new_wheel = SpinWheel(expanded_segments)
        if whith_wheel:
            return new_wheel
        else:
            return new_wheel.segments



    def spin(self, spins=1):
        '''
        Spin the wheel a specified number of times and return the results.
        spins: int - number of times to spin the wheel (default is 1)
        '''
        if not isinstance(spins, int) or spins <= 0:
            raise SpinWheelSpinNotNumberError("Number of spins must be a positive integer.")
        
        results = [random.choice(self.segments) for _ in range(spins)]
        return results
    
    def __str__(self):
        '''
        Return a string representation of the spin wheel.
        '''
        return f"SpinWheel(segments={self.segments})"
    
    def __repr__(self):
        '''
        Return a formal string representation of the spin wheel.
        '''
        return f"SpinWheel(segments={self.segments})"
    
    def __eq__(self, value):
        if not isinstance(value, SpinWheel):
            return False
        return self.segments == value.segments
    


# ==========================================================================================
# Test the SpinWheel class

def test():
    wheel1 = SpinWheel()
    print(wheel1)
    print(wheel1.spin(5))

    wheel2 = SpinWheel(["Red", "Green", "Blue", "Yellow"])
    print(wheel2)
    print(wheel2.spin(3))

    wheel3 = SpinWheel()
    wheel3.DIYwheel(["A", "B", "C", "D", "E"])
    print(wheel3)
    print(wheel3.spin(4))

    wheel4 = SpinWheel()
    new_wheel = wheel4.DIYsegments(["X", "Y", "Z"], with_wheel=True)
    print(new_wheel)
    print(new_wheel.spin(6))

    wheel5 = SpinWheel()
    new_wheel2 = wheel5.DIYwheelsegments(["Gold", "Silver", "Bronze"], whith_wheel=True, segment_size=10, weights=[0.5, 0.3, 0.2])
    print(new_wheel2)
    print(new_wheel2.spin(7))

if __name__ == "__main__":
    test()