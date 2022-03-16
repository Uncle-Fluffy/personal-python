# file for helpful system resources
# Created by Terry Carter 3/16/2022

import sys

if len(sys.argv) > 1:
    print(len(sys.argv))
    print(sys.argv[0])
    print(sys.argv[1])
    print(type(sys.argv[1]))
else:
    print("no arguments given")