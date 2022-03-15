# Checks for expected result
# result:   actual result
# expected: expected result
# returns 'Passed' if actual and expected are the same, 'Failed' otherwise
def CheckResult(actual, expected):
  # Make sure expected and actual are the same type
  typ = type(expected)
  if type(actual) is typ:
    # Handle case where expected result is a list
    if typ is list:
      # Actual must have the same number of list elements
      items = len(expected)
      if items == len(actual):
        # Elements must also be the same (and in same order)
        for i in range(0, items):
          if not expected[i] == actual[i]: break
        # Lists are the same
        else:
          return 'Passed'
    else:
      # Not a list, so actual must be the same as expected
      if expected == actual:
        return 'Passed'
  # At least one of the tests above failed, so actual is not the same as expected
  return 'Failed'
