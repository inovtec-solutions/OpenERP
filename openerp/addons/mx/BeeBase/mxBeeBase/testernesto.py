#!/usr/local/bin/python

from mx.BeeBase import BeeStorage, BeeDict

BeeStorage._debug = 1
BeeDict._debug = 1

def part1():

    # Fill initial version of the dictionary
    d = BeeDict.BeeDict('testernesto', autocommit=1)
    for i in range(1000):
        d[i] = "A"*i
    d.commit()
    #d.free_cache()
    d.close()


def part2():

    # Update a few values
    d = BeeDict.BeeDict('testernesto', autocommit=1)
    for i in range(100,300):
        d[i] = "C" * i
    d.commit()

import sys
if sys.argv[1] == 'init':
    import os
    for filename in ('testernesto.dat',
                     'testernesto.idx',
                     ):
      try:
        os.remove(filename)
      except:
        pass
    part1()

else:
    part2()
                
