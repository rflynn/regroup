#!venv/bin/python

"""
standalone program that reads input and outputs a regex that describes it
"""

from regroup import DAWG, DAWGRelaxer

if __name__ == '__main__':

    # ./regroup.py --relax --cluster-prefix-len=2

    import argparse
    import sys

    # commandline options
    parser = argparse.ArgumentParser()
    parser.add_argument('--relax', action='store_true',
                        help='attempt to simplify pattern where possible')
    parser.add_argument('--cluster-prefix-len', type=int,
                        help='split by prefix of a given length')
    args = parser.parse_args()

    # run
    lines = (line.rstrip('\r\n') for line in sys.stdin.readlines())
    dawg = DAWG.from_iter(lines)

    if args.relax:
        dawg = DAWGRelaxer(dawg).relax()

    # output
    if args.cluster_prefix_len:
        clusters = dawg.cluster_by_prefixlen(args.cluster_prefix_len)
        for prefix, suffix_tree in clusters:
            d = DAWG.from_dawg(suffix_tree)
            print(prefix + DAWGRelaxer(d).relax().serialize())
    else:
        print(dawg.serialize())
