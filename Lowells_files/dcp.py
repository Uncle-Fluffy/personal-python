# Good morning! Here's your coding interview problem for today.
# This problem was asked by Google.
# Given a sorted list of integers,
# square the elements and give the output in sorted order.
# For example, given [-9, -2, 0, 2, 3],
# return [0, 4, 4, 9, 81].

# Import standard items
import os
import sys

# Import shared stuff
sys.path.append(os.path.abspath('..'))  # Need .. to be in import path
from main        import main

#            Original Squaredmin
testData = [([-9, -2, 0, 2, 3], [0, 4, 4, 9, 81])
           ]

def SquareAndReorder(given):
  assert type(given) is list
  # Create new list
  squared = []
  # Loop through given list
  for value in given:
    # Add square of value to new list
    squared.append(value * value)
  # Return new list sorted
  return sorted(squared)

if __name__ == "__main__":
  main(SquareAndReorder, testData, '{0}: Given {1} => {2}')
