#ifndef MXDATETIME_H
#define MXDATETIME_H
/* 
  mxDateTime -- A generic date/time type

  Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
  Copyright (c) 2000-2011, eGenix.com Software GmbH; mailto:info@egenix.com
  See the documentation for further copyright information or contact
  the author (mailto:mal@lemburg.com).
  
*/

/* The extension's name; must be the same as the init function's suffix */
#define MXDATETIME_MODULE "mxDateTime"

/* Name of the package or module that provides the extensions C API.
   If the extension is used inside a package, provide the complete
   import path. */
#define MXDATETIME_API_MODULE "mx.DateTime"

/* Name of the mxDateTime C API object; this includes a version number
   to prevent use of incompatible C APIs */
#define MXDATETIME_CAPI_OBJECT MXDATETIME_MODULE"API2"

/* --- No servicable parts below this line ----------------------*/

/* Include generic mx extension header file */
#include "mxh.h"

#ifdef MX_BUILDING_MXDATETIME
# define MXDATETIME_EXTERNALIZE MX_EXPORT
#else
# define MXDATETIME_EXTERNALIZE MX_IMPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Flags for the calendar ID: */
#define MXDATETIME_GREGORIAN_CALENDAR	0
#define MXDATETIME_JULIAN_CALENDAR	1

/* Strings for the calendars */
#define MXDATETIME_GREGORIAN_CALENDAR_STRING	"Gregorian"
#define MXDATETIME_JULIAN_CALENDAR_STRING	"Julian"


/* --- DateTime Object ------------------------------------------*/

/* Note: The objects internal values are only calculated once and
   are thereafter considered immutable ! */

typedef struct {
    PyObject_HEAD

    /* Representation used to do calculations */
    long absdate;		/* number of days since 31.12. in the year 1 BC
				   calculated in the Gregorian calendar. */
    double abstime;		/* seconds since 0:00:00.00 (midnight)
				   on the day pointed to by absdate */

    /* COM Date representation */
    double comdate;
    
    /* Broken down values (set at creation time and using the calendar
       specified in the calendar flag); depend on the calendar used. */
    long year;			/* starting from year 1 */
    signed char month;		/* 1-12 */
    signed char day;		/* 1-31 */
    signed char hour;		/* 0-24 */
    signed char minute;		/* 0-59 */
    double second;		/* 0-60.999... */

    signed char day_of_week;	/* 0 (Monday) - 6 (Sunday) */
    short day_of_year;		/* 1-366 */

    unsigned char calendar;	/* Calendar ID; for possible values see
				   above. */
} mxDateTimeObject;

/* Type checking macro */

#define mxDateTime_Check(v) \
        (((mxDateTimeObject *)(v))->ob_type == mxDateTime.DateTime_Type)

/* --- DateTimeDelta Object ----------------------------------*/

/* Note: The objects internal values are only calculated once and
   are thereafter considered immutable ! */

typedef struct {
    PyObject_HEAD
    double seconds;		/* number of delta seconds */

    /* Broken down values (set at creation time); the sign can be
       deduced from seconds' sign. */
    long day;			/* >=0 */
    signed char hour;		/* 0-23 */
    signed char minute;		/* 0-59 */
    double second;		/* 0-60.999 */
    
} mxDateTimeDeltaObject;

/* Type checking macro */

#define mxDateTimeDelta_Check(v) \
        (((mxDateTimeDeltaObject *)(v))->ob_type == \
	 mxDateTime.DateTimeDelta_Type)

/* --- C API ----------------------------------------------------*/

/* C API for usage by other Python modules */
typedef struct {

    /* Type object for DateTime()

    */
    PyTypeObject *DateTime_Type;

    /* Construct a new object from the given absolute date and time.

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTime_FromAbsDateAndTime)(long absdate,
					     double abstime);

    /* Construct new object from Python 6-tuple
       (year,month,day,hour,minute,second) 

       Returns NULL in case of an error.

    */
    PyObject *(*DateTime_FromTuple)(PyObject *v);

    /* Construct new object from year,month,day,hour,minute,second 

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTime_FromDateAndTime)(long year,
					  int month,
					  int day,
					  int hour,
					  int minute,
					  double second);

    /* Construct new object from a given struct tm. DST, weekday and
       day of year are ignored. 

       Returns NULL in case of an error.

    */
    PyObject *(*DateTime_FromTmStruct)(struct tm *tm);

    /* Construct new object from the given ticks; these are first
       converted to a gmtime struct and this is then used as basis for
       the object value.

       Note that you have to pass in the ticks value as double and not
       as time_t value (see the note below on this).

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTime_FromTicks)(double ticks);

    /* Construct new object from a given COM date double

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTime_FromCOMDate)(double comdate);

    /* Fill the given struct tm with the object's value.

       Seconds are truncated before assigning them to the struct tm
       seconds integer slot (previous version rounded the seconds part
       which sometimes resulted in the value being 60).

       Returns a pointer to the changed struct or NULL in case of an
       error.

    */
    struct tm *(*DateTime_AsTmStruct)(mxDateTimeObject *datetime,
				      struct tm *tm);

    /* Return the objects value as time_t value.

       It is assumed that
       the object contains local time information, so
       time.localtime(object.as_ticks()) == object.tuple().

       Note that this functions returns a double and not a time_t
       value -- this is because some systems define time_t to be a
       long which would cause the conversion to lose the fraction
       part. 

       Returns -1.0 and sets an error in case of failure. 
    
    */
    double (*DateTime_AsTicks)(mxDateTimeObject *datetime);

    /* Return the objects value as COM date double 

       Returns -1.0 and sets an error in case of failure. 
    
    */
    double (*DateTime_AsCOMDate)(mxDateTimeObject *datetime);

    /* Type object for DateTimeDelta()

    */
    PyTypeObject *DateTimeDelta_Type;

    /* Construct a new object from the given days and seconds deltas.

       The internal value is calculated using a 86400.0 seconds/day
       basis.

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTimeDelta_FromDaysAndSeconds)(long days,
						  double seconds);

    /* Construct a new object from the given values repesenting time.

       The parameters are used to calculate a number-of-seconds since
       midnight value.

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTimeDelta_FromTime)(int hours,
					int minutes,
					double seconds);
    
    /* Same as DateTimeDelta_FromDaysAndSeconds() except that you pass
       the two arguments in a Python tuple.

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTimeDelta_FromTuple)(PyObject *v);

    /* Same as DateTimeDelta_FromTime() except that you pass the three
       arguments in a Python tuple.

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTimeDelta_FromTimeTuple)(PyObject *v);

    /* Using 86400.0 seconds/day a seconds value is calculated from
       the days and seconds part of the passed object.

       Returns -1.0 and sets an error in case of failure. 

    */
    double (*DateTimeDelta_AsDouble)(mxDateTimeDeltaObject *delta);

    /* Construct a new DateTime object from the given days value which
       represents absolute days and the absolute time as fraction of a
       day.

       The internal value is calculated using a 86400.0 seconds/day
       basis. 

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTime_FromAbsDays)(double days);

    /* Using 86400.0 seconds/day a days value is calculated from the
       internal value of the passed object. 

       Returns -1.0 and sets an error in case of failure. 
    
    */
    double (*DateTime_AsAbsDays)(mxDateTimeObject *datetime);

    /* Construct a new DateTimeDelta object from the given days value.
    
       The internal value is calculated using a 86400.0 seconds/day
       basis. 

       Returns NULL in case of an error.
    
    */
    PyObject *(*DateTimeDelta_FromDays)(double days);
    
    /* Using 86400.0 seconds/day a days value is calculated from
       the internal value of the passed object.

       Returns NULL in case of an error.
    
    */
    double (*DateTimeDelta_AsDays)(mxDateTimeDeltaObject *delta);

    /* Sets the given variables to values corresponding to the given
       DateTime object.
       
       You can pass a NULL pointer if you don't want
       that variable to be set.

       Returns -1 and sets an error in case of failure. 

    */
    int (*DateTime_BrokenDown)(mxDateTimeObject *datetime,
				long *year,
				int *month,
				int *day,
				int *hour,
				int *minute,
				double *second);

    /* Sets the given variables to values corresponding to the given
       DateTimeDelta object.

       You can pass a NULL pointer if you don't want that variable to
       be set.
       
       Returns -1 and sets an error in case of failure.
    
    */
    int (*DateTimeDelta_BrokenDown)(mxDateTimeDeltaObject *delta,
				     long *day,
				     int *hour,
				     int *minute,
				     double *second);

    /* Construct a new object from the given absolute date, time and
       calendar.

       Returns NULL in case of an error.

       New in mxDateTime 3.2.
    
    */
    PyObject *(*DateTime_FromAbsDateTime)(long absdate,
					  double abstime,
					  int calendar);

} mxDateTimeModule_APIObject;

#ifndef MX_BUILDING_MXDATETIME

/* --- C API ----------------------------------------------------*/

/* Interfacestructure to C API for other modules.
   Call mxDateTime_ImportModuleAPI() to initialize this
   structure. After that usage is simple:

   PyObject *v;
	
   v = mxDateTime.DateTime_FromAbsDateAndTime(1,1);
   if (!v)
       goto onError;
   ...

*/

static 
mxDateTimeModule_APIObject mxDateTime;

/* You *must* call this before using any of the functions in
   mxDateTime and check its outcome; otherwise all accesses will
   result in a segfault. Returns 0 on success. */

#ifndef DPRINTF
# define DPRINTF if (0) printf
#endif

static
int mxDateTime_ImportModuleAndAPI(void)
{
    PyObject *mod = 0, *v = 0;
    char *apimodule = MXDATETIME_API_MODULE;
    char *apiname = MXDATETIME_CAPI_OBJECT;
    void *api;
    
    DPRINTF("Importing the %s C API...\n",apimodule);
    mod = PyImport_ImportModule(apimodule);
    if (mod == NULL) {
	/* Fallback solution to remain backward compatible */
	PyErr_Clear();
	apimodule = "DateTime";
	DPRINTF(" package not found, trying %s instead\n",apimodule);
	mod = PyImport_ImportModule(apimodule);
	if (mod == NULL)
	    goto onError;
    }
    DPRINTF(" %s package found\n",apimodule);
    v = PyObject_GetAttrString(mod,apiname);
    if (v == NULL)
	goto onError;
    Py_DECREF(mod);
    DPRINTF(" API object %s found\n",apiname);
    api = PyCObject_AsVoidPtr(v);
    if (api == NULL)
	goto onError;
    Py_DECREF(v);
    memcpy(&mxDateTime,api,sizeof(mxDateTime));
    DPRINTF(" API object loaded and initialized.\n");
    return 0;
    
 onError:
    DPRINTF(" not found.\n");
    Py_XDECREF(mod);
    Py_XDECREF(v);
    return -1;
}

#endif

/* EOF */
#ifdef __cplusplus
}
#endif
#endif
