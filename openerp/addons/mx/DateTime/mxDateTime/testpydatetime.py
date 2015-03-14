from mx.DateTime import *

# Check compatibility with Python's datetime
try:
    import datetime
except ImportError:
    pass
else:
    class GMT1(datetime.tzinfo):
        def utcoffset(self, dt):
             return datetime.timedelta(hours=1)

    # Test values
    pydt1 = datetime.datetime(2007, 1, 1, 12, 30, 13)
    pydt2 = datetime.datetime(2007, 1, 1, 12, 30, 13, tzinfo=GMT1())
    pyd1 = datetime.date(2007, 1, 1)
    pyt1 = datetime.time(12, 30, 13)
    pyt2 = datetime.time(12, 30, 13, tzinfo=GMT1())
    pytd1 = datetime.timedelta(0, 12*3600 + 30*60 + 13)
    mxdt1 = DateTime(2007, 1, 1, 12, 30, 13)
    mxdt2 = DateTime(2007, 1, 1)
    mxdt3 = DateTime(2007, 1, 1, 11, 30, 13)
    mxdtd1 = DateTimeDelta(0, 12, 30, 13)
    mxdtd2 = DateTimeDelta(0, 11, 30, 13)

    # Constructor methods
    assert mxdt1.pydate() == pyd1
    assert mxdt1.pydatetime() == pydt1
    assert mxdt1.pytime() == pyt1
    assert mxdtd1.pytime() == pyt1
    assert mxdtd1.pytimedelta() == pytd1
    
    # Comparisons
    assert pydt1 == mxdt1
    assert mxdt1 == pydt1, (mxdt1, pydt1)
    assert mxdt2 == pyd1
    # Doesn't work, since datetime.time always compares false
    # against non-datetime.time types
    #assert pyt1 == mxdtd1
    #assert mxdtd1 == pyt1

    # Subtract
    assert mxdt1 - pydt1 == 0.0
    assert mxdt2 - pyd1 == 0.0
    assert mxdt1 - pyd1 == mxdtd1

    # Add
    assert mxdt1 - pytd1 == mxdt2, (mxdt1 - pytd1, mxdt2)
    assert pydt1 - mxdt2 == mxdtd1, (pydt1 - mxdt2, -mxdtd1)
    assert mxdt2 + pytd1 == mxdt1
    # Not supported by datetime module:
    #assert pydt1 - pyd1 == mxdtd1
    # Not supported by datetime module:
    #assert pydt1 - mxdtd1 == mxdt2

    # Constructor compatibility
    assert mxdt1 == DateTimeFrom(pydt1), (mxdt1, DateTimeFrom(pydt1))
    assert mxdt2 == DateTimeFrom(pyd1)
    assert mxdt3 == DateTimeFrom(pydt2)
    assert mxdt2 == DateFrom(pyd1)
    assert mxdtd1 == TimeDeltaFrom(pytd1)
    assert mxdtd1 == TimeDeltaFrom(pyt1)
    assert mxdtd2 == TimeDeltaFrom(pyt2), (mxdtd2, TimeDeltaFrom(pyt2))

