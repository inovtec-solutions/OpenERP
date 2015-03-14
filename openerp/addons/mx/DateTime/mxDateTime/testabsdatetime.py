import sys
from mx.DateTime import *

# Test for ticket #526
if sys.maxint > 2**32:
    print DateTimeFromAbsDateTime(-9580000000)

# Test DateTimeFromAbsDateTime() for a whole range of values
    
#RANGE = range(-5, 5)
RANGE = range(-1000000, 1000000)
INTERVAL = max(len(RANGE) / 1000, 1)

print 'Gregorian calendar:'
print
for absdate in RANGE:
    d = DateTimeFromAbsDateTime(absdate)
    assert d.absdate == absdate
    if absdate % INTERVAL == 0:
        print '%-10s: %s' % (absdate, d)
print
        
print 'Julian calendar:'
print
for absdate in RANGE:
    d = DateTimeFromAbsDateTime(absdate,0,Julian)
    assert d.absdate == absdate
    if absdate % INTERVAL == 0:
        print '%-10s: %s' % (absdate, d)
        
print


