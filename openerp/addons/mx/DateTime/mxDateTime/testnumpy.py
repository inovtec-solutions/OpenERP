""" Tests for #823: mxDateTime 3.2 coercion no longer works with numpy

"""
import numpy
from mx.DateTime import *

print 'Testing mxDateTime with numpy...'
print
delta_t = numpy.arange(5) * oneHour
t0 = now()

t1 = delta_t + t0
print t1

t2 = t0 + delta_t
print t2

for i in xrange(1000):
    t1 = delta_t + t0
    t2 = t0 + delta_t

print
print 'Works.'
