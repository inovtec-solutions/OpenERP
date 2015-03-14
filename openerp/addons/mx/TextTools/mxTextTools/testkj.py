#!/usr/bin/env python

""" Run a few tests using the King James Bible plain text version as
    available from:

    http://www.gutenberg.org/etext/10

"""
import re, time
from mx import TextTools, Tools

# Location of the text file
KJB = '/tmp/kjv10.txt'

# Iterations to use for benchmarking
COUNT = 100


def search_bench(word, text):

    iterations = Tools.trange(COUNT)
    print ('Searching for all occurences of %r using ...' % word)

    t0 = time.time()
    so = TextTools.TextSearch(word)
    for i in iterations:
        l = so.findall(text)
    t1 = time.time()
    count = len(l)

    print (' - mx.TextSearch.TextSearch().findall(): %5.3f ms (%i)' %
           ((t1 - t0) / COUNT * 1000.0, count))

    t0 = time.time()
    so = re.compile(word)
    for i in iterations:
        l = so.findall(text)
    t1 = time.time()
    count = len(l)
    
    print (' - re.compile().findall(): %5.3f ms (%i)' %
           ((t1 - t0) / COUNT * 1000.0, count))

    t0 = time.time()
    for i in iterations:
        count = text.count(word)
    t1 = time.time()
    
    print (' - text.count(): %5.3f ms (%i)' %
           ((t1 - t0) / COUNT * 1000.0, count))


if __name__ == '__main__':

    text = open(KJB).read()
    search_bench('God', text)
    search_bench('Jesus', text)
    search_bench('devil', text)
    search_bench('love', text)
    search_bench('hate', text)
    
