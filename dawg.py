#!venv/bin/python

"""
standalone program that reads input and outputs a regex that describes it
"""

from regroup import DAWG

if __name__ == '__main__':
    import sys
    lines = (line.rstrip('\r\n') for line in sys.stdin.readlines())
    print(DAWG.from_iter(lines).serialize())
