""" Tests for mxDateTime type DateTime and DateTimeDelta:
    comparisons, arithmetic and mixed type operations.

"""
import sys
from mx.DateTime import *
from datetime import *

# DateTime
t1 = Date(2011,3,5)
t1_ticks = t1.ticks()
t2 = Date(2011,3,6)
t2_ticks = t2.ticks()

# DateTimeDelta
td1 = t2 - t1
td1_seconds = td1.seconds
td2 = 2 * td1
td2_seconds = td2.seconds
td3 = Time(12,0,0)
td4 = Time(13,0,0)

# PyDate
d1 = date(2011,3,5)
d2 = date(2011,3,6)
# PyTime
pt1 = time(12,0,0)
pt2 = time(13,0,0)
# PyDateTime
dt1 = datetime(2011,3,5)
dt2 = datetime(2011,3,6)
# PyDelta
dtd1 = d2 - d1
dtd2 = 2 * dtd1

def run_tests():

    ### DateTime comparison

    # DateTime
    assert t1 == t1
    assert t2 == t2
    assert t1 < t2
    assert t1 <= t2
    assert not (t1 > t2)
    assert not (t1 >= t2)

    # None
    assert not (t1 == None)
    assert not (None == t1)
    assert not (t2 == None)
    assert not (None == t2)

    # DateTime op DateTimeDelta
    assert t1 != td1
    assert t2 != td1
    assert t1 < td1
    assert t2 < td1
    assert not (t1 > td1)
    assert not (t2 > td1)

    # DateTime op floats
    assert t1 == t1_ticks
    assert t2 == t2_ticks
    assert t1 <= t1_ticks
    assert t2 <= t2_ticks
    assert t1 >= t1_ticks
    assert t2 >= t2_ticks
    assert t1 != t1_ticks + 1
    assert t2 != t2_ticks + 1
    assert t1 < t1_ticks + 1
    assert t2 < t2_ticks + 1
    assert t1 > t1_ticks - 1
    assert t2 > t2_ticks - 1
    assert t1_ticks == t1
    assert t1_ticks >= t1
    assert t2_ticks > t1
    assert t1_ticks < t2
    assert t2_ticks <= t2_ticks

    # DateTime op date
    assert t1 == d1
    assert t2 == d2
    assert t1 < d2
    assert t1 <= d2
    assert not (t1 > d2)
    assert not (t1 >= d2)
    assert t2 > d1
    assert t2 >= d1
    assert not (t2 < d1)
    assert not (t2 <= d1)
    assert d1 < t2
    assert d1 <= t2
    assert not (d1 > t2)
    assert not (d1 >= t2)

    # DateTime op datetime
    assert t1 == dt1
    assert t2 == dt2
    assert t1 < dt2
    assert t1 <= dt2
    assert not (t1 > dt2)
    assert not (t1 >= dt2)
    assert dt1 < t2
    assert dt1 <= t2
    assert not (dt1 > t2)
    assert not (dt1 >= t2)

    ### DateTime addition

    # DateTime + DateTimeDelta
    assert t1 + td1 == t2
    assert td1 + t1 == t2

    # DateTime + DateTime
    try:
        t1 + t2
    except TypeError:
        pass
    else:
        raise TypeError('DateTime + DateTime should raise TypeError')

    # DateTime + None
    try:
        t1 + None
    except TypeError:
        pass
    else:
        raise TypeError('DateTime + None should raise TypeError')

    # DateTime + number
    assert t1 + 1 == t2
    assert t1 + 1.0 == t2
    assert 1 + t1 == t2
    assert 1.0 + t1 == t2

    # DateTime + PyDelta
    assert t1 + dtd1 == t2
    assert dtd1 + t1 == t2

    ### DateTime subtraction

    # DateTime - DateTime
    assert t2 - t1 == td1

    # DateTime - DateTimeDelta
    assert t2 - td1 == t1

    # DateTime - number
    assert t2 - 1 == t1

    # DateTime - PyDelta
    assert t2 - dtd1 == t1

    # DateTime - PyDate
    assert t2 - d1 == td1

    # DateTime - PyDateTime
    assert t2 - dt1 == td1

    # DateTimeDelta - DateTime
    try:
        td1 - t2
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta - DateTime should raise TypeError')

    # DateTime - None
    try:
        t1 - None
    except TypeError:
        pass
    else:
        raise TypeError('DateTime - None should raise TypeError')

    # number - DateTime
    try:
        10 - t2
    except TypeError:
        pass
    else:
        raise TypeError('number - DateTime should raise TypeError')

    # PyDate - DateTime
    assert d2 - t1 == td1, repr(d2 - t1)

    # PyDateTime - DateTime
    assert dt2 - t1 == td1, repr(dt2 - t1)

    ### DateTime multiplication

    # DateTime * DateTimeDelta
    try:
        t1 * td2
    except TypeError:
        pass
    else:
        raise TypeError('DateTime * DateTimeDelta should raise TypeError')

    # DateTime * None
    try:
        t1 * None
    except TypeError:
        pass
    else:
        raise TypeError('DateTime * None should raise TypeError')

    # DateTime * number
    try:
        t1 * 10
    except TypeError:
        pass
    else:
        raise TypeError('DateTime * number should raise TypeError')

    ### DateTime division

    # DateTime / DateTimeDelta
    try:
        t1 / td2
    except TypeError:
        pass
    else:
        raise TypeError('DateTime / DateTimeDelta should raise TypeError')

    # DateTime / None
    try:
        t1 / None
    except TypeError:
        pass
    else:
        raise TypeError('DateTime / None should raise TypeError')

    # DateTime / number
    try:
        t1 / 10
    except TypeError:
        pass
    else:
        raise TypeError('DateTime / number should raise TypeError')

    ### DateTimeDelta comparison

    # DateTimeDelta
    assert td1 == td1
    assert td2 == td2
    assert td1 < td2
    assert td1 <= td2
    assert not (td1 > td2)
    assert not (td1 >= td2)

    # None
    assert not (td1 == None)
    assert not (None == td1)
    assert not (td2 == None)
    assert not (None == td2)

    # DateTimeDelta op DateTime
    assert td1 != t1
    assert td2 != t1
    assert td1 > t1
    assert td2 > t1
    assert not (td1 < t1)
    assert not (td2 < t1)

    # DateTimeDelta op floats
    assert td1 == td1_seconds
    assert td2 == td2_seconds
    assert td1 <= td1_seconds
    assert td2 <= td2_seconds
    assert td1 >= td1_seconds
    assert td2 >= td2_seconds
    assert td1 != td1_seconds + 1
    assert td2 != td2_seconds + 1
    assert td1 < td1_seconds + 1
    assert td2 < td2_seconds + 1
    assert td1 > td1_seconds - 1
    assert td2 > td2_seconds - 1

    # DateTimeDelta op PyDelta
    assert td1 == dtd1
    assert td2 == dtd2
    assert td1 < dtd2
    assert td1 <= dtd2
    assert not (td1 > dtd2)
    assert not (td1 >= dtd2)
    assert td2 > dtd1
    assert td2 >= dtd1
    assert not (td2 < dtd1)
    assert not (td2 <= dtd1)
    # XXX These don't work, due to the Python timedelta object's
    #     broken rich comparisons slot method (it doesn't interoperate
    #     with other types); using a coercion slot method in DateTimeDelta
    #     doesn't help either, since this is not called at all.
    #assert dtd1 < td2
    #assert dtd1 <= td2
    #assert not (dtd1 > td2)
    #assert not (dtd1 >= td2)

    # DateTimeDelta op PyTime
    assert td3 == pt1
    assert td4 == pt2
    assert td3 < pt2
    assert td4 > pt1
    assert td3 >= pt1
    assert td4 >= pt2

    ### DateTimeDelta addition

    # DateTimeDelta + DateTimeDelta
    assert td1 + td2 == td1_seconds + td2_seconds

    # DateTimeDelta + DateTime
    assert td1 + t1 == t2
    assert t1 + td1 == t2

    # DateTimeDelta + None
    try:
        td1 + None
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta + None should raise TypeError')

    # DateTimeDelta + number
    assert td1 + 1 == td1_seconds + 1
    assert td1 + 1.0 == td1_seconds + 1
    assert 1 + td1 == td1_seconds + 1
    assert 1.0 + td1 == td1_seconds + 1

    # DateTimeDelta + PyDelta
    assert td1 + dtd1 == 2 * td1
    assert dtd1 + td1 == 2 * td1

    # DateTimeDelta + PyTime
    assert td1 + pt1 == td1 + td3
    assert pt1 + td1 == td1 + td3

    ### DateTimeDelta subtraction

    # DateTimeDelta - DateTimeDelta
    assert td2 - td1 == td1

    # DateTimeDelta - DateTime
    try:
        td1 - t2
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta - DateTime should raise TypeError')

    # DateTimeDelta - None
    try:
        td1 - None
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta - None should raise TypeError')

    # DateTimeDelta - number
    assert td2 - 86400 == td1

    # DateTimeDelta - PyDelta
    assert td2 - dtd1 == td1

    # DateTimeDelta - PyTime
    assert td4 - pt1 == td4 - td3

    # DateTimeDelta - PyDateTime
    try:
        td1 - dt1
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta - PyDateTime should raise TypeError')

    # DateTimeDelta - PyDate
    try:
        td1 - d1
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta - PyDate should raise TypeError')

    # DateTime - DateTimeDelta
    assert t2 - td1 == t1

    # number - DateTimeDelta
    try:
        10 - td1
    except TypeError:
        pass
    else:
        raise TypeError('number - DateTimeDelta should raise TypeError')

    # PyDelta - DateTimeDelta
    assert dtd2 - td1 == td1

    # PyTime - DateTimeDelta
    assert pt2 - td3 == td4 - td3

    # PyDateTime - DateTimeDelta
    try:
        dt1 - td1
    except TypeError:
        pass
    else:
        raise TypeError('PyDateTime - DateTimeDelta should raise TypeError')

    # PyDate - DateTimeDelta
    try:
        d1 - td1
    except TypeError:
        pass
    else:
        raise TypeError('PyDate - DateTimeDelta should raise TypeError')

    ### DateTimeDelta multiplication

    # DateTimeDelta * DateTimeDelta
    try:
        td1 * td1
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta * DateTimeDelta should raise TypeError')

    # DateTimeDelta * DateTime
    try:
        td1 * t1
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta * DateTime should raise TypeError')

    # DateTimeDelta * None
    try:
        td1 * None
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta * None should raise TypeError')

    # DateTimeDelta * number
    assert td1 * 2 == td2
    assert td1 * 2.0 == td2

    # DateTime * DateTimeDelta
    try:
        t1 * td1
    except TypeError:
        pass
    else:
        raise TypeError('DateTime * DateTimeDelta should raise TypeError')

    # number * DateTimeDelta
    assert 2 * td1 == td2
    assert 2.0 * td1 == td2

    ### DateTimeDelta division

    # DateTimeDelta / DateTimeDelta
    assert td2 / td1 == 2.0

    # DateTimeDelta / DateTime
    try:
        td1 / t1
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta / DateTime should raise TypeError')

    # DateTimeDelta * None
    try:
        td1 / None
    except TypeError:
        pass
    else:
        raise TypeError('DateTimeDelta / None should raise TypeError')

    # DateTimeDelta / PyDelta
    assert td2 / dtd1 == 2.0

    # DateTimeDelta / PyDelta
    assert td1 / pt1 == 2.0

    # DateTimeDelta / number
    assert td2 / 2 == td1
    assert td2 / 2.0 == td1

    # DateTime / DateTimeDelta
    try:
        t1 / td1
    except TypeError:
        pass
    else:
        raise TypeError('DateTime / DateTimeDelta should raise TypeError')

    # PyDelta / DateTimeDelta
    assert dtd2 / td1 == 2.0

    # PyTime / DateTimeDelta
    assert pt1 / td1 == 0.5

    # number / DateTimeDelta
    try:
        1.0 / td1
    except TypeError:
        pass
    else:
        raise TypeError('number / DateTimeDelta should raise TypeError')

### Default run

run_tests()

### Memory leak test

if '--memory-leaks' in sys.argv:
    while 1:
        run_tests()
    
