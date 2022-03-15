#!/usr/bin/env python3

from CheckResult import CheckResult

# Main program
# fcn: Function being tested
# fmt: Format string for printing results
# returns nothing
def main(fcn, data, fmt):
  # Loop through test data
  for given, expected in data:
    # Get actual results for level traversal of tree
    actual = fcn(given)
    # Are actual results as expected for doubly-linked list?
    passed = CheckResult(actual, expected)
    # Show information for this method
    print(fmt.format(passed, given, actual))
