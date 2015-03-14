# -*- coding: latin-1 -*-

""" Date/Time string parsing module.

    Note about the Y2K problems:

       The parser can only handle years with at least 2 digits. 2
       digit year values get expanded by adding the century using
       DateTime.add_century(), while 3 digit year get converted
       literally. To have 2 digit years also be interpreted literally,
       add leading zeros, e.g. year 99 must be written as 099 or 0099.

    See http://en.wikipedia.org/wiki/Calendar_date for some
    information about various formats used around the world.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2011, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import types,re
import DateTime,ISO,ARPA,Timezone

### Globals

# Enable to produce debugging output
_debug = 0

### Helpers

def _invdict(mapping):
    d =  {}
    for name, code in mapping.iteritems():
        d[code] = name
    return d

### Parsers

# REs for matching date and time parts in a string; These REs
# parse a superset of ARPA, ISO, American and European style dates.
# Timezones are supported via the Timezone submodule.

_year = '(?P<year>-?\d\d+(?!:))'
_fullyear = '(?P<year>-?\d\d\d+(?!:))'
_epoch = '(?P<epoch> *[ABCDE\.]+)'
_year_epoch = '(?:' + _year + _epoch + '?)'
_fullyear_epoch = '(?:' + _fullyear + _epoch + '?)'
_relyear = '(?:\((?P<relyear>[-+]?\d+)\))'

_month = '(?P<month>\d?\d(?!:))'
_fullmonth = '(?P<month>\d\d(?!:))'
_litmonth = ('(?P<litmonth>'
             'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
             'mär|mae|mrz|mai|okt|dez|'
             'fev|avr|juin|juil|aou|aoû|déc|'
             'ene|abr|ago|dic|'
             'out'
             ')[a-z,\.;]*')
litmonthtable = {
    # English
    'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
    'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12,
    # German
    'mär':3, 'mae':3, 'mrz':3, 'mai':5, 'okt':10, 'dez':12,
    # French
    'fev':2, 'avr':4, 'juin':6, 'juil':7, 'aou':8, 'aoû':8,
    'déc':12,
    # Spanish
    'ene':1, 'abr':4, 'ago':8, 'dic':12,
    # Portuguese
    'out':10,
    }
_relmonth = '(?:\((?P<relmonth>[-+]?\d+)\))'

_day = '(?P<day>\d\d?(?!:))'
_usday = '(?:(?P<day>\d\d?(?!:))(?:st|nd|rd|th|[,.;])?)'
_fullday = '(?P<day>\d\d(?!:))'
_litday = ('(?P<litday>'
           'mon|tue|wed|thu|fri|sat|sun|'
           'die|mit|don|fre|sam|son|'
           'lun|mar|mer|jeu|ven|sam|dim|'
           'mie|jue|vie|sab|dom|'
           'pri|seg|ter|cua|qui'
           ')[a-z]*')
litdaytable = {
    # English
    'mon':0, 'tue':1, 'wed':2, 'thu':3, 'fri':4, 'sat':5, 'sun':6,
    # German
    'die':1, 'mit':2, 'don':3, 'fre':4, 'sam':5, 'son':6,
    # French
    'lun':0, 'mar':1, 'mer':2, 'jeu':3, 'ven':4, 'sam':5, 'dim':6,
    # Spanish
    'mie':2, 'jue':3, 'vie':4, 'sab':5, 'dom':6,
    # Portuguese
    'pri':0, 'seg':1, 'ter':2, 'cua':3, 'qui':4,
    }
_relday = '(?:\((?P<relday>[-+]?\d+)\))'

_hour = '(?P<hour>[012]?\d)'
_minute = '(?P<minute>[0-6]\d)'
_second = '(?P<second>[0-6]\d(?:[.,]\d+)?)'

_days = '(?P<days>\d+(?:[.,]\d+)?)'
_hours = '(?P<hours>\d+(?:[.,]\d+)?)'
_minutes = '(?P<minutes>\d+(?:[.,]\d+)?)'
_seconds = '(?P<seconds>\d+(?:[.,]\d+)?)'

_reldays = '(?:\((?P<reldays>[-+]?\d+(?:[.,]\d+)?)\))'
_relhours = '(?:\((?P<relhours>[-+]?\d+(?:[.,]\d+)?)\))'
_relminutes = '(?:\((?P<relminutes>[-+]?\d+(?:[.,]\d+)?)\))'
_relseconds = '(?:\((?P<relseconds>[-+]?\d+(?:[.,]\d+)?)\))'

_sign = '(?:(?P<sign>[-+]) *)'
_week = 'W(?P<week>\d?\d)'
_zone = Timezone.zone
_ampm = '(?P<ampm>am|pm|a.m.?|p.m.?)'

_time = (_hour + ':' + _minute + '(?::' + _second + ')? *'
         + _ampm + '? *' + _zone + '?')
_isotime = _hour + ':?' + _minute + ':?' + _second + '? *' + _zone + '?'

_weekdate = _year + '-?(?:' + _week + '-?' + _day + '?)?'
_eurodate = _day + '\.' + _month + '\.' + _year_epoch + '?'
_alteuro1date = _day + '/' + _month + '/' + _year_epoch + '?'
_alteuro2date = _day + '-' + _month + '-' + _year_epoch + '?'
_usdate = _month + '/' + _day + '(?:/' + _year_epoch + '|[^/]|$)'
_altusdate = _month + '-' + _day + '-' + _fullyear_epoch
_isodate = _year + '-' + _month + '-?' + _day + '?(?!:)'
_altisodate = _year + _fullmonth + _fullday + '(?!:)'
_usisodate = _fullyear + '/' + _fullmonth + '/' + _fullday
_litdate = ('(?:'+ _litday + '[,.; ]+)?' + 
            _usday + '[- ]+' + 
            _litmonth + '[- ,.a-z]*' +
            _year_epoch + '?')
_altlitdate = ('(?:'+ _litday + '[,.; ]+)? *' + 
               _litmonth + '[ ,.a-z]+' +
               _usday + 
               '(?:[ a-z]+' + _year_epoch + ')?')

_relany = '[*%?a-zA-Z]+'

_relisodate = ('(?:(?:' + _relany + '|' + _year + '|' + _relyear + ')-' +
               '(?:' + _relany + '|' + _month + '|' + _relmonth + ')-' +
               '(?:' + _relany + '|' + _day + '|' + _relday + '))')

_relisotime = ('(?:(?:' + _relany + '|' + _hour + '|' + _relhours + '):' +
               '(?:' + _relany + '|' + _minute + '|' + _relminutes + ')' +
               '(?::(?:' + _relany + '|' + _second + '|' + _relseconds + '))?)')

_isodelta1 = (_sign + '?' +
              _days + ':' + _hours + ':' + _minutes + ':' + _seconds)
_isodelta2 = (_sign + '?' + 
              _hours + ':' + _minutes + ':' + _seconds)
_isodelta3 = (_sign + '?' + 
              _hours + ':' + _minutes)
_litdelta = (_sign + '?' +
             '(?:' + _days + ' *d[a-z]*[,; ]*)?' + 
             '(?:' + _hours + ' *h[a-z]*[,; ]*)?' + 
             '(?:' + _minutes + ' *m[a-z]*[,; ]*)?' +
             '(?:' + _seconds + ' *s[a-z]*[,; ]*)?')
_litdelta2 = (_sign + '?' +
             '(?:' + _days + ' *d[a-z]*[,; ]*)?' + 
              _hours + ':' + _minutes + '(?::' + _seconds + ')?')

_timeRE = re.compile(_time, re.I)
_isotimeRE = re.compile(_isotime, re.I)
_isodateRE = re.compile(_isodate, re.I)
_altisodateRE = re.compile(_altisodate, re.I)
_usisodateRE = re.compile(_usisodate, re.I)
_eurodateRE = re.compile(_eurodate, re.I)
_alteuro1dateRE = re.compile(_alteuro1date, re.I)
_alteuro2dateRE = re.compile(_alteuro2date, re.I)
_usdateRE = re.compile(_usdate, re.I)
_altusdateRE = re.compile(_altusdate, re.I)
_litdateRE = re.compile(_litdate, re.I)
_altlitdateRE = re.compile(_altlitdate, re.I)
_relisodateRE = re.compile(_relisodate, re.I)
_isodelta1RE = re.compile(_isodelta1)
_isodelta2RE = re.compile(_isodelta2)
_isodelta3RE = re.compile(_isodelta3)
_litdeltaRE = re.compile(_litdelta)
_litdelta2RE = re.compile(_litdelta2)
_relisotimeRE = re.compile(_relisotime, re.I)

### Available date parsers

## Most common date order: day month year

# dd.mm.yyyy
DATE_PARSER_DMY1 = 'dmy1'
# dd/mm/yyyy
DATE_PARSER_DMY2 = 'dmy2'
# dd-mm-yyyy
DATE_PARSER_DMY3 = 'dmy3'

# DMY parser class
DATE_DMY_PARSERS = (
    DATE_PARSER_DMY1,
    DATE_PARSER_DMY2,
    DATE_PARSER_DMY3,
    )

## US date order: month day year

# mm/dd/yyyy
DATE_PARSER_MDY1 = 'mdy1'
# mm-dd-yyyy
DATE_PARSER_MDY2 = 'mdy2'

# MDY parser class
DATE_MDY_PARSERS = (
    DATE_PARSER_MDY1,
    DATE_PARSER_MDY2,
    )

## Literal date forms

# Monday, 2nd November 1998
DATE_PARSER_LITERAL1 = 'lit1'
# Monday, November 2nd 1998
DATE_PARSER_LITERAL2 = 'lit2'

# Literal parser class
DATE_LITERAL_PARSERS = (
    DATE_PARSER_LITERAL1,
    DATE_PARSER_LITERAL2,
    )

## ISO date forms

# yyyy-mm-dd
DATE_PARSER_YMD1 = 'ymd1'
# yyyymmdd
DATE_PARSER_YMD2 = 'ymd2'
# yyyy/mm/dd
DATE_PARSER_YMD3 = 'ymd3'

# YMD parser class
DATE_YMD_PARSERS = (
    DATE_PARSER_YMD1,
    DATE_PARSER_YMD2,
    DATE_PARSER_YMD3,
    )

## Unknown formats

DATE_PARSER_UNKNOWN = 'unknown'

### Date parser name mappings

# Mapping name to code
DATE_PARSERS = {
    # New names in mxDateTime 3.2
    'dmy1': DATE_PARSER_DMY1,
    'dmy2': DATE_PARSER_DMY2,
    'dmy3': DATE_PARSER_DMY3,
    'mdy1': DATE_PARSER_MDY1,
    'mdy2': DATE_PARSER_MDY2,
    'lit1': DATE_PARSER_LITERAL1,
    'lit2': DATE_PARSER_LITERAL2,
    'ymd1': DATE_PARSER_YMD1,
    'ymd2': DATE_PARSER_YMD2,
    'ymd3': DATE_PARSER_YMD3,
    'unknown': DATE_PARSER_UNKNOWN,

    # Aliases
    'dmy': DATE_PARSER_DMY1,
    'dmy-dot': DATE_PARSER_DMY1,
    'dmy-hyphen': DATE_PARSER_DMY2,
    'dmy-slash': DATE_PARSER_DMY3,
    'mdy': DATE_PARSER_MDY1,
    'mdy-slash': DATE_PARSER_MDY1,
    'mdy-hyphen': DATE_PARSER_MDY2,
    'iso': DATE_PARSER_YMD1,
    'iso-hyphen': DATE_PARSER_YMD1,
    'iso-compact': DATE_PARSER_YMD2,
    'iso-no-hyphen': DATE_PARSER_YMD2,
    'iso-slash': DATE_PARSER_YMD3,

    # Old names used in mxDateTime <3.1
    'euro': DATE_PARSER_DMY1,
    'alteuro1': DATE_PARSER_DMY2,
    'alteuro2': DATE_PARSER_DMY3,
    'us': DATE_PARSER_MDY1,
    'altus': DATE_PARSER_MDY2,
    'lit': DATE_PARSER_LITERAL1,
    'altlit': DATE_PARSER_LITERAL2,
    'eurlit': DATE_PARSER_LITERAL1, # eurlit was replaced by an extended lit
    'iso': DATE_PARSER_YMD1,
    'altiso': DATE_PARSER_YMD2,
    'usiso': DATE_PARSER_YMD3,
    }

DATE_PARSER_NAME = DATE_PARSERS

DATE_PARSER_RE = {
    # New names in mxDateTime 3.2
    DATE_PARSER_DMY1: _eurodateRE,
    DATE_PARSER_DMY2: _alteuro1dateRE,
    DATE_PARSER_DMY3: _alteuro2dateRE,
    DATE_PARSER_MDY1: _usdateRE,
    DATE_PARSER_MDY2: _altusdateRE,
    DATE_PARSER_LITERAL1: _litdateRE,
    DATE_PARSER_LITERAL2: _altlitdateRE,
    DATE_PARSER_YMD1: _isodateRE,
    DATE_PARSER_YMD2: _altisodateRE,
    DATE_PARSER_YMD3: _usisodateRE,
    DATE_PARSER_UNKNOWN: None,
    }

# Default value for the formats parameter (this also defines the
# order in which the parsers are tried)
DEFAULT_DATE_FORMATS = (
    DATE_PARSER_DMY1,
    DATE_PARSER_YMD3, # Placed here to avoid conflicts with MDY1
    DATE_PARSER_MDY1,
    DATE_PARSER_MDY2,
    DATE_PARSER_YMD1,
    DATE_PARSER_YMD2,
    DATE_PARSER_DMY2,
    DATE_PARSER_DMY3,
    DATE_PARSER_LITERAL1,
    DATE_PARSER_LITERAL2,
    DATE_PARSER_UNKNOWN,
    )

### Available time parsers

# HH:MM or HH:MM:SS or HH:MM:SS.SS
TIME_PARSER_STANDARD = 'standard'

# HHMM or HHMMSS or HHMMSS.SS
TIME_PARSER_ISO = 'iso'

# Unknown format
TIME_PARSER_UNKNOWN = 'unknown'

### Time parser name mapppings

# Map names to codes
TIME_PARSERS = {
    'standard': TIME_PARSER_STANDARD,
    'iso': TIME_PARSER_ISO,
    'unknown': TIME_PARSER_UNKNOWN,
    }

TIME_PARSER_NAME = TIME_PARSERS

# Default value for the time_formats parameter (this also defines the
# order in which the parsers are tried)
DEFAULT_TIME_FORMATS = (
    TIME_PARSER_STANDARD,
    TIME_PARSER_ISO,
    TIME_PARSER_UNKNOWN,
    )

###

def _parse_date(text, date_formats=DEFAULT_DATE_FORMATS, defaultdate=None,

                int=int,float=float,
                add_century=DateTime.add_century,
                now=DateTime.now):

    """ Parses the date part given in text and returns a tuple
        (text,day,month,year,style) with the following
        meanings:

        * text gives the original text without the date part

        * day,month,year give the parsed date

        * style gives information about which parser was successful
          in form of the parser code (see DATE_PARSERS)

        date_formats may be set to a tuple of style codes specifying
        which of the available parsers to use and in which order to
        try them. Default is to try all available formats.

        defaultdate provides the defaults to use in case no date part
        is found. Most other parsers default to the current year
        January 1 if some of these date parts are missing.

        If 'unknown' is not given in formats and the date cannot be
        parsed, a ValueError is raised.

    """
    match = None
    style = 0
    
    # Apply parsers in the order given in formats
    for format_code in date_formats:

        # Find parser
        try:
            parser_re = DATE_PARSER_RE[format_code]
        except KeyError:
            raise TypeError('unknown date format: %r' % format_code)
        
        # Handle DATE_PARSER_UNKNOWN: use defaultdate
        if parser_re is None:
            if defaultdate is None:
                defaultdate = now()
            year = defaultdate.year
            month = defaultdate.month
            day = defaultdate.day
            style = format_code
            break

        # Run parser
        match = parser_re.search(text)
        if match is None:
            continue
        if _debug:
            print 'parser groups: %r' % (match.groups(),)

        # Post-processing
        if format_code in DATE_DMY_PARSERS:

            day,month,year,epoch = match.groups()
            month = int(month)
            # Could have mistaken euro format for us style date
            # which uses month, day order
            if month > 12 or month == 0:
                match = None
                continue
            day = int(day)
            if year:
                if len(year) == 2:
                    # Y2K problem:
                    year = add_century(int(year))
                else:
                    year = int(year)
            else:
                if defaultdate is None:
                    defaultdate = now()
                year = defaultdate.year
            if epoch and 'B' in epoch:
                year = -year + 1
            break

        elif format_code in DATE_YMD_PARSERS:

            if format_code == DATE_PARSER_YMD2:
                # Avoid mistaking ISO time parts ('Thhmmss') for dates
                left, right = match.span()
                if left > 0 and \
                   text[left - 1] == 'T':
                    match = None
                    continue

            year,month,day = match.groups()
            if len(year) == 2:
                # Y2K problem:
                year = add_century(int(year))
            else:
                year = int(year)
            # Default to January 1st
            if not month:
                month = 1
            else:
                month = int(month)
            if not day:
                day = 1
            else:
                day = int(day)
            break

        elif format_code in DATE_MDY_PARSERS:

            month,day,year,epoch = match.groups()
            month = int(month)
            # Could have mistaken us format for euro style date
            # which uses day, month order
            if month > 12 or month == 0:
                match = None
                continue
            # Default to 1 if no day is given
            if day:
                day = int(day)
            else:
                day = 1
            if year:
                if len(year) == 2:
                    # Y2K problem:
                    year = add_century(int(year))
                else:
                    year = int(year)
            else:
                if defaultdate is None:
                    defaultdate = now()
                year = defaultdate.year
            if epoch and 'B' in epoch:
                year = -year + 1
            break

        elif format_code in DATE_LITERAL_PARSERS:

            if format_code == DATE_PARSER_LITERAL1:
                litday,day,litmonth,year,epoch = match.groups()
                month = ''
            elif format_code == DATE_PARSER_LITERAL2:
                litday,litmonth,day,year,epoch = match.groups()
                month = ''

            if litmonth:
                litmonth = litmonth.lower()
                try:
                    month = litmonthtable[litmonth]
                except KeyError:
                    # Unknown month name
                    match = None
                    continue
            elif month:
                month = int(month)
            else:
                month = 1
            # Could have mistaken us format for euro style date
            # which uses day, month order
            if month > 12 or month == 0:
                match = None
                continue

            if day:
                day = int(day)
            else:
                day = 1

            # Default to current year, January 1st
            if not year:
                if defaultdate is None:
                    defaultdate = now()
                year = defaultdate.year
            else:
                if len(year) == 2:
                    # Y2K problem:
                    year = add_century(int(year))
                else:
                    year = int(year)
            if epoch and 'B' in epoch:
                year = -year + 1
            break

    # Check success
    if match is not None:
        # Remove date from text
        left, right = match.span()
        if _debug:
            print 'parsed date:',repr(text[left:right]),\
                  'giving:',year,month,day
        text = text[:left] + text[right:]
        style = format_code
        
    elif not style:
        # Not recognized: raise an error
        raise ValueError('unknown date format: "%s"' % text)

    #print '_parse_date:',text,day,month,year,style
    return text,day,month,year,style

def _parse_time(text, time_formats=DEFAULT_TIME_FORMATS,

                int=int,float=float):

    """ Parses a time part given in text and returns a tuple
        (text,hour,minute,second,offset,style) with the following
        meanings:

        * text gives the original text without the time part

        * hour,minute,second give the parsed time

        * offset gives the time zone UTC offset

        * style gives information about which parser was successful:
          in form of the parser code (see TIME_PARSERS)

        time_formats may be set to a tuple of style codes specifying
        which of the available parsers to use and in which order to
        try them. Default is to try all available formats.

        If 'unknown' is not given in formats and the time cannot be
        parsed, a ValueError is raised.

    """
    match = None
    style = 0

    # Apply parsers in the order given in formats
    for format_code in time_formats:

        if format_code == TIME_PARSER_STANDARD:

            # Standard format
            match = _timeRE.search(text)
            if match is None:
                continue
            hour,minute,second,ampm,zone = match.groups()
            style = format_code
            break

        elif format_code == TIME_PARSER_ISO:

            # ISO format
            match =  _isotimeRE.search(text)
            if match is None:
                continue
            hour,minute,second,zone = match.groups()
            ampm = None
            style = format_code
            break

        elif format_code == TIME_PARSER_UNKNOWN:

            # Default handling
            hour,minute,second,offset = 0,0,0.0,0
            style = format_code
            break

        else:
            raise TypeError('unknown time format: %r' % format_code)

    # Check success
    if not style:
        # If no default handling should be applied, raise an error
        raise ValueError, 'unknown time format: "%s"' % text

    # Post-processing
    if match is not None:
        if zone:
            # Convert to UTC offset
            offset = Timezone.utc_offset(zone)
        else:
            offset = 0
        hour = int(hour)
        if ampm:
            if ampm[0] in ('p', 'P'):
                # 12pm = midday
                if hour < 12:
                    hour = hour + 12
            else:
                # 12am = midnight 
                if hour >= 12:
                    hour = hour - 12
        if minute:
            minute = int(minute)
        else:
            minute = 0
        if not second:
            second = 0.0
        else:
            if ',' in second:
                second = second.replace(',', '.')
            second = float(second)

        # Remove time from text
        left,right = match.span()
        if _debug: 
            print 'parsed time:',repr(text[left:right]),\
                  'giving:',hour,minute,second,offset
        text = text[:left] + text[right:]

    #print '_parse_time:',text,hour,minute,second,offset,style
    return text,hour,minute,second,offset,style

###

def DateTimeFromString(text, formats=DEFAULT_DATE_FORMATS, defaultdate=None,
                       time_formats=DEFAULT_TIME_FORMATS,

                       DateTime=DateTime):

    """ DateTimeFromString(text, [formats, defaultdate])
    
        Returns a DateTime instance reflecting the date and time given
        in text. In case a timezone is given, the returned instance
        will point to the corresponding UTC time value. Otherwise, the
        value is set as given in the string.

        formats may be set to a tuple of strings specifying which of
        the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'dmy1' - the European date parser (dd.mm.yyyy)
          'ymd3' - US style ISO date parser (yyyy/mm/dd)
          'mdy1' - the US date parser (mm/dd/yyyy)
          'mdy2' - the alternative US date parser (mm-dd-yyyy)
          'ymd1' - the ISO date parser (yyyy-mm-dd)
          'ymd2' - the alternative ISO date parser (yyyymmdd)
          'dmy2' - alternative European date parser 1 (dd/mm/yyyy)
          'dmy3' - alternative European date parser 2 (dd-mm-yyyy)
          'lit1' - the literal date parser (day, month order)
          'lit2' - the alternative literal date parser (month, day order)
          'unknown' - no date part was found, defaultdate was used

        defaultdate provides the defaults to use in case no date part
        is found. Most of the parsers default to the current year
        January 1 if some of these date parts are missing.

        If 'unknown' is not given in formats and the date cannot
        be parsed, a ValueError is raised.

        time_formats may be set to a tuple of strings specifying which
        of the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'standard' - standard time format HH:MM:SS
          'iso'      - ISO time format (superset of 'standard')
          'unknown'  - default to 00:00:00 in case the time format
                       cannot be parsed

        Defaults to 00:00:00.00 for time parts that are not included
        in the textual representation.

        If 'unknown' is not given in time_formats and the time cannot
        be parsed, a ValueError is raised.

    """
    origtext = text.strip()

    # Convert formats list to a list of parser codes
    if formats is not DEFAULT_DATE_FORMATS:
        formats = tuple([DATE_PARSERS[format]
                         for format in formats])
        if DATE_PARSER_UNKNOWN not in formats:
            formats_with_unknown = formats + (DATE_PARSER_UNKNOWN,)
        else:
            formats_with_unknown = formats
    else:
        formats_with_unknown = formats

    # Convert time_formats list to a list of parser codes
    if time_formats is not DEFAULT_TIME_FORMATS:
        time_formats = tuple([TIME_PARSERS[format]
                              for format in time_formats])
        if TIME_PARSER_UNKNOWN not in time_formats:
            time_formats_with_unknown = time_formats + (TIME_PARSER_UNKNOWN,)
        else:
            time_formats_with_unknown = time_formats
    else:
        time_formats_with_unknown = time_formats

    # First try: parse date, then time
    if _debug:
        print 'first try on %r using these formats: %r' % (
            origtext, formats_with_unknown)
    text,day,month,year,datestyle = _parse_date(
        origtext,
        formats_with_unknown,
        defaultdate)
    text,hour,minute,second,offset,timestyle = _parse_time(
        text,
        time_formats_with_unknown)
    text = text.strip()
    if _debug:
        print ('result of date/time parsing on %r: '
               'datestyle=%s, timestyle=%s, text=%r' % (
                   origtext,
                   DATE_PARSER_NAME[datestyle],
                   TIME_PARSER_NAME[timestyle],
                   text))
    try1 = (text,
            day,month,year,datestyle,
            hour,minute,second,offset,timestyle)
    try1_text_left = len(text)

    # If we have text left, run a second try, if the date style could
    # not be determined or we have found a literal format
    if (try1_text_left > 0 and
        (datestyle == DATE_PARSER_UNKNOWN or
         datestyle in DATE_LITERAL_PARSERS)):

        # Second try: parse time, then date
        if _debug:
            print 'second try on %r using these formats: %r' % (
                origtext, formats_with_unknown)
        text,hour,minute,second,offset,timestyle = _parse_time(
            origtext,
            time_formats_with_unknown)
        text,day,month,year,datestyle = _parse_date(
            text,
            formats_with_unknown,
            defaultdate)
        text = text.strip()
        if _debug:
            print ('result of time/date parsing on %r: '
                   'datestyle=%s, timestyle=%s, text=%r' % (
                       origtext,
                       DATE_PARSER_NAME[datestyle],
                       TIME_PARSER_NAME[timestyle],
                       text))

        # Decide based on the length of the remaining text and the
        # parsed styles
        try2_text_left = len(text)
        if try1_text_left < try2_text_left:
            try1_wins = 1
        elif try2_text_left > try1_text_left:
            try1_wins = 0
        else:
            # Equal length: use the try with the better parsing
            # characteristics, emphasizing the date part
            if datestyle == DATE_PARSER_UNKNOWN:
                try1_wins = 1
            elif (timestyle == TIME_PARSER_UNKNOWN and
                  try1[4] != DATE_PARSER_UNKNOWN):
                try1_wins = 1
            else:
                try1_wins = 0
        if try1_wins:
            # Try 1 wins
            (text,
             day,month,year,datestyle,
             hour,minute,second,offset,timestyle) = try1
            if _debug:
                print 'first try wins'
        else:
            # Try 2 wins
            if _debug:
                print 'second try wins'

    else:
        if _debug:
            print 'first try succeeds without second try'

    # Final check for unknowns
    if ((datestyle == DATE_PARSER_UNKNOWN and
         formats is not formats_with_unknown) or
        (timestyle == TIME_PARSER_UNKNOWN and
         time_formats is not time_formats_with_unknown)):
        raise ValueError(
            'Failed to parse "%s": found "%s" date, "%s" time' %
            (origtext,
             DATE_PARSER_NAME[datestyle],
             TIME_PARSER_NAME[timestyle]))

    # Convert to DateTime instance
    try:
        return DateTime.DateTime(year,month,day,hour,minute,second) - offset
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (origtext, why)

def DateFromString(text, formats=DEFAULT_DATE_FORMATS, defaultdate=None,

                   DateTime=DateTime):

    """ DateFromString(text, [formats, defaultdate])
    
        Returns a DateTime instance reflecting the date given in
        text. A possibly included time part is ignored.

        formats and defaultdate work just like for
        DateTimeFromString().

    """
    text = text.strip()

    # Convert formats list to a list of parser codes
    if formats is not DEFAULT_DATE_FORMATS:
        formats = tuple([DATE_PARSERS[format]
                         for format in formats])

    # Parse date
    _text,day,month,year,datestyle = _parse_date(text, formats, defaultdate)

    if (datestyle == DATE_PARSER_UNKNOWN and
        DATE_PARSER_UNKNOWN not in formats):
        raise ValueError(
            'Failed to parse "%s": found "%s" date' %
            (text, datestyle))

    try:
        return DateTime.DateTime(year,month,day)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)

def validateDateTimeString(text, formats=DEFAULT_DATE_FORMATS,
                           time_formats=DEFAULT_TIME_FORMATS):

    """ validateDateTimeString(text, [formats, defaultdate])

        Validates the given text and returns 1/0 depending on whether
        text includes parseable date and time values or not.

        formats works just like for DateTimeFromString() and defines
        the order of date/time parsers to apply. It defaults to the
        same list of parsers as for DateTimeFromString().

        XXX Undocumented !
    
    """
    formats = list(formats)
    if DATE_PARSER_UNKNOWN in formats:
        formats.remove(DATE_PARSER_UNKNOWN)
    time_formats = list(time_formats)
    if TIME_PARSER_UNKNOWN in time_formats:
        time_formats.remove(TIME_PARSER_UNKNOWN)
    try:
        DateTimeFromString(text, formats=formats, time_formats=time_formats)
    except (DateTime.RangeError, ValueError), why:
        return 0
    return 1

def validateDateString(text, formats=DEFAULT_DATE_FORMATS):

    """ validateDateString(text, [formats, defaultdate])

        Validates the given text and returns 1/0 depending on whether
        text includes a parseable date value or not.

        formats works just like for DateTimeFromString() and defines
        the order of date/time parsers to apply. It defaults to the
        same list of parsers as for DateTimeFromString().
    
        XXX Undocumented !
    
    """
    formats = list(formats)
    if DATE_PARSER_UNKNOWN in formats:
        formats.remove(DATE_PARSER_UNKNOWN)
    try:
        DateFromString(text, formats=formats)
    except (DateTime.RangeError, ValueError), why:
        return 0
    return 1

def TimeFromString(text, formats=DEFAULT_TIME_FORMATS,

                   DateTime=DateTime):

    """ TimeFromString(text, [formats])
    
        Returns a DateTimeDelta instance reflecting the time given in
        text. A possibly included date part is ignored.

        formats may be set to a tuple of strings specifying which of
        the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'standard' - standard time format HH:MM:SS
          'iso'      - ISO time format (superset of 'standard')
          'unknown'  - default to 00:00:00 in case the time format
                       cannot be parsed

        Defaults to 00:00:00.00 for parts that are not included in the
        textual representation.
        
    """
    text = text.strip()

    # Convert time_formats list to a list of parser codes
    if formats is not DEFAULT_TIME_FORMATS:
        formats = tuple([TIME_PARSERS[format]
                         for format in formats])

    # Parse time
    _text,hour,minute,second,offset,timestyle = _parse_time(
        text,
        formats)

    if (timestyle == TIME_PARSER_UNKNOWN and
        TIME_PARSER_UNKNOWN not in formats):
        raise ValueError(
            'Failed to parse "%s": found "%s" time' %
            (text, timestyle))

    try:
        dtd = DateTime.DateTimeDelta(0.0, hour, minute, second)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)
    else:
        # XXX What to do with offset ?
        return dtd

#
# XXX Still missing: validateTimeString(), validateDateTimeDeltaString()
#                    and validateTimeDeltaString()
#

def DateTimeDeltaFromString(text,

                            float=float,DateTime=DateTime):

    """ DateTimeDeltaFromString(text)
    
        Returns a DateTimeDelta instance reflecting the delta given in
        text. Defaults to 0:00:00:00.00 for parts that are not
        included in the textual representation or cannot be parsed.

    """
    match = _isodelta1RE.search(text)
    if match is not None:
        sign, days, hours, minutes, seconds = match.groups()
    else:
        match = _litdelta2RE.search(text)
        if match is not None:
            sign, days, hours, minutes, seconds = match.groups()
        else:
            match = _isodelta2RE.search(text)
            if match is not None:
                sign, hours, minutes, seconds = match.groups()
                days = None
            else:
                match = _isodelta3RE.search(text)
                if match is not None:
                    sign, hours, minutes = match.groups()
                    days = None
                    seconds = None
                else:
                    match = _litdeltaRE.search(text)
                    if match is not None:
                        sign, days, hours, minutes, seconds = match.groups()

                    else:
                        # Not matched:
                        return DateTime.DateTimeDelta(0.0)

    # Conversions
    if days:
        days = float(days)
    else:
        days = 0.0
    if hours:
        hours = float(hours)
    else:
        hours = 0.0
    if minutes:
        minutes = float(minutes)
    else:
        minutes = 0.0
    if seconds:
        seconds = float(seconds)
    else:
        seconds = 0.0
    if sign != '-':
        sign = 1
    else:
        sign = -1

    try:
        dtd = DateTime.DateTimeDelta(days,hours,minutes,seconds)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)
    else:
        if sign < 0:
            return -dtd
        else:
            return dtd

# Aliases
TimeDeltaFromString = DateTimeDeltaFromString

###

def _parse_reldate(text,

                   int=int,float=float):

    match = _relisodateRE.search(text)
    if match is not None:
        groups = match.groups()
        if _debug: print groups
        year,years,month,months,day,days = groups
        if year:
            year = int(year)
        if years:
            years = float(years)
        else:
            years = 0
        if month:
            month = int(month)
        if months:
            months = float(months)
        else:
            months = 0
        if day:
            day = int(day)
        if days:
            days = float(days)
        else:
            days = 0
        return year,years,month,months,day,days
    else:
        return None,0,None,0,None,0

def _parse_reltime(text,

                   int=int,float=float):

    match = _relisotimeRE.search(text)
    if match is not None:
        groups = match.groups()
        if _debug: print groups
        hour,hours,minute,minutes,second,seconds = groups
        if hour:
            hour = int(hour)
        if hours:
            hours = float(hours)
        else:
            hours = 0
        if minute:
            minute = int(minute)
        if minutes:
            minutes = float(minutes)
        else:
            minutes = 0
        if second:
            second = int(second)
        if seconds:
            seconds = float(seconds)
        else:
            seconds = 0
        return hour,hours,minute,minutes,second,seconds
    else:
        return None,0,None,0,None,0

def RelativeDateTimeFromString(text,

                               RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeDateTimeFromString(text)
    
        Returns a RelativeDateTime instance reflecting the relative
        date and time given in text.

        Defaults to wildcards for parts or values which are not
        included in the textual representation or cannot be parsed.

        The format used in text must adhere to the following syntax:

        		[YYYY-MM-DD] [HH:MM[:SS]]

        with the usual meanings. Values which should not be altered
        may be replaced with '*', '%', '?' or any combination of
        letters, e.g. 'YYYY'. Relative settings must be enclosed in
        parenthesis if given and should include a sign, e.g. '(+0001)'
        for the year part. All other settings are interpreted as
        absolute values.

        Date and time parts are both optional as a whole. Seconds in
        the time part are optional too. Everything else (including the
        hyphens and colons) is mandatory.

    """
    text = text.strip()

    year,years,month,months,day,days = _parse_reldate(text)
    hour,hours,minute,minutes,second,seconds = _parse_reltime(text)
    return RelativeDateTime(year=year,years=years,
                            month=month,months=months,
                            day=day,days=days,
                            hour=hour,hours=hours,
                            minute=minute,minutes=minutes,
                            second=second,seconds=seconds)

def RelativeDateFromString(text,

                           RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeDateFromString(text)
    
        Same as RelativeDateTimeFromString(text) except that only the
        date part of text is taken into account.

    """
    text = text.strip()

    year,years,month,months,day,days = _parse_reldate(text)
    return RelativeDateTime(year=year,years=years,
                            month=month,months=months,
                            day=day,days=days)

def RelativeTimeFromString(text,

                           RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeTimeFromString(text)
    
        Same as RelativeDateTimeFromString(text) except that only the
        time part of text is taken into account.

    """
    text = text.strip()

    hour,hours,minute,minutes,second,seconds = _parse_reltime(text)
    return RelativeDateTime(hour=hour,hours=hours,
                            minute=minute,minutes=minutes,
                            second=second,seconds=seconds)

### Tests

def _test():

    import sys

    now = DateTime.now()

    class T:
        def __init__(self, text, reference, **parser_kws):
            self.text = text
            self.reference = reference
            self.parser_kws = parser_kws

    print 'Testing DateTime Parser...'

    l = [

        # Literal formats
        T('Sun Nov  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        T('sun nov  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        T('sUN NOV  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        T('Sunday, 06-Nov-94 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        T('Sun, 06 Nov 1994 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        T('06-Nov-94 08:49:37', '1994-11-06 08:49:37.00'),
        T('06-Nov-94', '1994-11-06 00:00:00.00'),
        T('06-NOV-94', '1994-11-06 00:00:00.00'),
        T('November 19 08:49:37', '%s-11-19 08:49:37.00' % now.year),
        T('Nov. 9', '%s-11-09 00:00:00.00' % now.year),
        T('Sonntag, der 6. November 1994, 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        T('6. November 2001, 08:49:37', '2001-11-06 08:49:37.00'),
        T('sep 6', '%s-09-06 00:00:00.00' % now.year),
        T('sep 6 2000', '2000-09-06 00:00:00.00'),
        T('September 29', '%s-09-29 00:00:00.00' % now.year),
        T('Sep. 29', '%s-09-29 00:00:00.00' % now.year),
        T('6 sep', '%s-09-06 00:00:00.00' % now.year),
        T('29 September', '%s-09-29 00:00:00.00' % now.year),
        T('29 Sep.', '%s-09-29 00:00:00.00' % now.year),
        T('sep 6 2001', '2001-09-06 00:00:00.00'),
        T('Sep 6, 2001', '2001-09-06 00:00:00.00'),
        T('September 6, 2001', '2001-09-06 00:00:00.00'),
        T('sep 6 01', '2001-09-06 00:00:00.00'),
        T('Sep 6, 01', '2001-09-06 00:00:00.00'),
        T('September 6, 01', '2001-09-06 00:00:00.00'),
        T('Thursday, Sept 6 01', '2001-09-06 00:00:00.00'),
        T('Thursday, 6 Sept 01', '2001-09-06 00:00:00.00'),
        T('Thursday, 2001-09-06', '2001-09-06 00:00:00.00'),
        T('Thursday, 6-09-2001', '2001-09-06 00:00:00.00', formats=['dmy3']),
        T('Thursday, 6-09-2001', '2001-06-09 00:00:00.00'),
        T('Thursday, 6/9/2001', '2001-06-09 00:00:00.00'),
        T('30 Apr 2006 20:19:00', '2006-04-30 20:19:00.00'),
        
        # ISO formats
        T('1994-11-06 08:49:37', '1994-11-06 08:49:37.00'),
        T('010203', '2001-02-03 00:00:00.00'),
        T('2001-02-03 00:00:00.00', '2001-02-03 00:00:00.00'),
        T('2001-02 00:00:00.00', '2001-02-01 00:00:00.00'),
        T('2001-02-03', '2001-02-03 00:00:00.00'),
        T('2001-02', '2001-02-01 00:00:00.00'),
        T('20000824/2300', '2000-08-24 23:00:00.00'),
        T('20000824/0102', '2000-08-24 01:02:00.00'),
        T('20000824', '2000-08-24 00:00:00.00'),
        T('20000824/020301', '2000-08-24 02:03:01.00'),
        T('20000824 020301', '2000-08-24 02:03:01.00'),
        T('-20000824 020301', '-2000-08-24 02:03:01.00'),
        T('20000824T020301', '2000-08-24 02:03:01.00'),
        T('20000824 020301', '2000-08-24 02:03:01.00'),
        T('2000-08-24 02:03:01.00', '2000-08-24 02:03:01.00'),
        T('T020311', '%s 02:03:11.00' % now.date),
        T('2003-12-9', '2003-12-09 00:00:00.00'),
        T('03-12-9', '2003-12-09 00:00:00.00'),
        T('003-12-9', '0003-12-09 00:00:00.00'),
        T('0003-12-9', '0003-12-09 00:00:00.00'),
        T('2003-1-9', '2003-01-09 00:00:00.00'),
        T('03-1-9', '2003-01-09 00:00:00.00'),
        T('003-1-9', '0003-01-09 00:00:00.00'),
        T('0003-1-9', '0003-01-09 00:00:00.00'),
        T('2008-05-06 19:30:09.57', '2008-05-06 19:30:09.57'),
        T('2008-05-06 19:30:09.58', '2008-05-06 19:30:09.58'),
        T('2008-05-06 19:30:09.59', '2008-05-06 19:30:09.59'),
        T('2008-05-06 19:30:09.60', '2008-05-06 19:30:09.60'),
        T('2008-05-06 19:30:09.61', '2008-05-06 19:30:09.61'),
        T('2008-05-06 19:30:09.62', '2008-05-06 19:30:09.62'),
        T('2008-05-06 19:30:09.570', '2008-05-06 19:30:09.57'),
        T('2008-05-06 19:30:09.580', '2008-05-06 19:30:09.58'),
        T('2008-05-06 19:30:09.590', '2008-05-06 19:30:09.59'),
        T('2008-05-06 19:30:09.600', '2008-05-06 19:30:09.60'),
        T('2008-05-06 19:30:09.610', '2008-05-06 19:30:09.61'),
        T('2008-05-06 19:30:09.620', '2008-05-06 19:30:09.62'),
        T('2008-05-06 19:30:09.571', '2008-05-06 19:30:09.57'),
        T('2008-05-06 19:30:09.581', '2008-05-06 19:30:09.58'),
        T('2008-05-06 19:30:09.591', '2008-05-06 19:30:09.59'),
        T('2008-05-06 19:30:09.601', '2008-05-06 19:30:09.60'),
        T('2008-05-06 19:30:09.611', '2008-05-06 19:30:09.61'),
        T('2008-05-06 19:30:09.621', '2008-05-06 19:30:09.62'),
        T('2008-05-06 19:30:09.575', '2008-05-06 19:30:09.58'),
        T('2008-05-06 19:30:09.585', '2008-05-06 19:30:09.59'),
        T('2008-05-06 19:30:09.595', '2008-05-06 19:30:09.60'),
        T('2008-05-06 19:30:09.605', '2008-05-06 19:30:09.61'),
        T('2008-05-06 19:30:09.615', '2008-05-06 19:30:09.62'),
        T('2008-05-06 19:30:09.625', '2008-05-06 19:30:09.63'),
        T('2008-05-06 19:30:09.579', '2008-05-06 19:30:09.58'),
        T('2008-05-06 19:30:09.589', '2008-05-06 19:30:09.59'),
        T('2008-05-06 19:30:09.599', '2008-05-06 19:30:09.60'),
        T('2008-05-06 19:30:09.609', '2008-05-06 19:30:09.61'),
        T('2008-05-06 19:30:09.619', '2008-05-06 19:30:09.62'),
        T('2008-05-06 19:30:09.629', '2008-05-06 19:30:09.63'),

        # US formats
        T('06/11/94 08:49:37', '1994-06-11 08:49:37.00'),
        T('11/06/94 08:49:37', '1994-11-06 08:49:37.00'),
        T('9/23/2001', '2001-09-23 00:00:00.00'),
        T('9-23-2001', '2001-09-23 00:00:00.00'),
        T('9/6', '%s-09-06 00:00:00.00' % now.year),
        T('09/6', '%s-09-06 00:00:00.00' % now.year),
        T('9/06', '%s-09-06 00:00:00.00' % now.year),
        T('09/06', '%s-09-06 00:00:00.00' % now.year),
        T('9/6/2001', '2001-09-06 00:00:00.00'),
        T('09/6/2001', '2001-09-06 00:00:00.00'),
        T('9/06/2001', '2001-09-06 00:00:00.00'),
        T('09/06/2001', '2001-09-06 00:00:00.00'),
        T('9-6-2001', '2001-09-06 00:00:00.00'),
        T('09-6-2001', '2001-09-06 00:00:00.00'),
        T('9-06-2001', '2001-09-06 00:00:00.00'),
        T('09-06-2001', '2001-09-06 00:00:00.00'),
        T('2002/05/28 13:10:56.1147 GMT+2', '2002-05-28 13:10:56.11'),
        T('1970/01/01', '1970-01-01 00:00:00.00'),
        T('20021025 12:00 PM', '2002-10-25 12:00:00.00'),
        T('20021025 12:30 PM', '2002-10-25 12:30:00.00'),
        T('20021025 12:00 AM', '2002-10-25 00:00:00.00'),
        T('20021025 12:30 AM', '2002-10-25 00:30:00.00'),
        T('20021025 1:00 PM', '2002-10-25 13:00:00.00'),
        T('20021025 2:00 AM', '2002-10-25 02:00:00.00'),
        T('Thursday, February 06, 2003 12:40 PM', '2003-02-06 12:40:00.00'),
        T('Mon, 18 Sep 2006 23:03:00', '2006-09-18 23:03:00.00'),
        T('6/12/08 5:08pm', '2008-06-12 17:08:00.00'),
        T('6/12/08 5:08p.m.', '2008-06-12 17:08:00.00'),
        T('6/12/08 5:08 pm', '2008-06-12 17:08:00.00'),
        T('6/12/08 5:08 p.m.', '2008-06-12 17:08:00.00'),
        T('January 12th 2008 at 5:08pm', '2008-01-12 17:08:00.00'),
        T('January 12th 2008 at 5:08 pm', '2008-01-12 17:08:00.00'),

        # European formats
        T('6.11.2001, 08:49:37', '2001-11-06 08:49:37.00'),
        T('06.11.2001, 08:49:37', '2001-11-06 08:49:37.00'),
        T('06.11. 08:49:37', '%s-11-06 08:49:37.00' % now.year),
        T('10/12/2004', '2004-12-10 00:00:00.00', formats=['dmy2']),
        T('13/02/2009', '2009-02-13 00:00:00.00', formats=['dmy2']),
        T('21/12/2002', '2002-12-21 00:00:00.00'),
        T('21/08/2002', '2002-08-21 00:00:00.00'),
        T('21-08-2002', '2002-08-21 00:00:00.00', formats=['dmy3']),
        T('13/01/03', '2003-01-13 00:00:00.00'),
        #T('13/1/03', '2003-01-13 00:00:00.00', formats=['dmy2']),
        #T('13/1/3', '2003-01-13 00:00:00.00', formats=['dmy2']),
        #T('13/01/3', '2003-01-13 00:00:00.00'),

        # Time only formats
        T('01:03', '%s 01:03:00.00' % now.date),
        T('01:03:11', '%s 01:03:11.00' % now.date),
        T('01:03:11.50', '%s 01:03:11.50' % now.date),
        T('01:03:11.50 AM', '%s 01:03:11.50' % now.date),
        T('01:03:11.50 PM', '%s 13:03:11.50' % now.date),
        T('01:03:11.50 a.m.', '%s 01:03:11.50' % now.date),
        T('01:03:11.50 p.m.', '%s 13:03:11.50' % now.date),

        # Invalid formats
        T('6..2001, 08:49:37', '%s 08:49:37.00' % now.date),
        T('9//2001', 'ignore'),
        T('06--94 08:49:37', 'ignore'),
        T('20000824020301', 'ignore'),
        T('20-03 00:00:00.00', 'ignore'),
        T('9/2001', 'ignore'),
        T('9-6', 'ignore'),
        T('09-6', 'ignore'),
        T('9-06', 'ignore'),
        T('09-06', 'ignore'),
        T('20000824/23', 'ignore'),
        T('November 1994 08:49:37', 'ignore'),
        T('Nov. 94', 'ignore'),
        T('Mon, 18 Sep 2006 23:03:00 +1234567890', 'ignore'),

        ]

    # Add Unicode versions
    try:
        unicode
    except NameError:
        pass
    else:
        k = []
        for test_case in l:
            k.append(T(unicode(test_case.text),
                       test_case.reference,
                       **test_case.parser_kws))
        l.extend(k)

    t = DateTime.now()

    for test_case in l:
        text = test_case.text
        reference = test_case.reference
        parser_kws = test_case.parser_kws
        try:
            value = DateTimeFromString(text, **parser_kws)
        except Exception, reason:
            if reference is None:
                continue
            else:
                value = str(reason)
        valid_datetime = validateDateTimeString(text)
        valid_date = validateDateString(text)
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
            print '  %r' % (_parse_date(
                text,
                date_formats=tuple(parser_kws.get('formats',
                                                  DEFAULT_DATE_FORMATS))
                             + (DATE_PARSER_UNKNOWN,)),)
        elif _debug:
            print 'Parsed "%s" successfully' % text
        if _debug:
            if not valid_datetime:
                print '  "%s" failed date/time validation' % text
            if not valid_date:
                print '  "%s" failed date validation' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

    ###

    print 'Testing DateTimeDelta Parser...'

    l = [

        # Literal formats
        ('Sun Nov  6 08:49:37 1994', '08:49:37.00'),
        ('1 day, 8 hours, 49 minutes, 37 seconds', '1:08:49:37.00'),
        ('10 days, 8 hours, 49 minutes, 37 seconds', '10:08:49:37.00'),
        ('8 hours, 49 minutes, 37 seconds', '08:49:37.00'),
        ('49 minutes, 37 seconds', '00:49:37.00'),
        ('37 seconds', '00:00:37.00'),
        ('37.5 seconds', '00:00:37.50'),
        ('8 hours later', '08:00:00.00'),
        ('2 days', '2:00:00:00.00'),
        ('2 days 23h', '2:23:00:00.00'),
        ('2 days 23:57', '2:23:57:00.00'),
        ('2 days 23:57:13', '2:23:57:13.00'),
        ('', '00:00:00.00'),
        
        # ISO formats
        ('1994-11-06 08:49:37', '08:49:37.00'),
        ('10:08:49:37', '10:08:49:37.00'),
        ('08:49:37', '08:49:37.00'),
        ('08:49', '08:49:00.00'),
        ('-10:08:49:37', '-10:08:49:37.00'),
        ('-08:49:37', '-08:49:37.00'),
        ('-08:49', '-08:49:00.00'),
        ('- 10:08:49:37', '-10:08:49:37.00'),
        ('- 08:49:37', '-08:49:37.00'),
        ('- 08:49', '-08:49:00.00'),
        ('10:08:49:37.5', '10:08:49:37.50'),
        ('08:49:37.5', '08:49:37.50'),
        ('10:8:49:37', '10:08:49:37.00'),
        ('8:9:37', '08:09:37.00'),
        ('8:9', '08:09:00.00'),
        ('8', '00:00:00.00'),

        # Invalid formats
        #('', None),
        #('8', None),

        ]

    t = DateTime.now()

    for text, reference in l:
        try:
            value = DateTimeDeltaFromString(text)
        except:
            if reference is None:
                continue
            else:
                value = str(sys.exc_info()[1])
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
        elif _debug:
            print 'Parsed "%s" successfully' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

    ###

    print 'Testing Time Parser...'

    l = [

        # Standard formats
        ('08:49:37 AM', '08:49:37.00'),
        ('08:49:37 PM', '20:49:37.00'),
        ('12:00:00 AM', '00:00:00.00'),
        ('12:00:00 PM', '12:00:00.00'),
        ('8:09:37', '08:09:37.00'),
        ('8:09', '08:09:00.00'),
        
        # ISO formats
        ('08:49:37', '08:49:37.00'),
        ('08:49', '08:49:00.00'),
        ('08:49:37.5', '08:49:37.50'),
        ('08:49:37,5', '08:49:37.50'),
        ('08:09', '08:09:00.00'),

        # Invalid formats
        ('', None),
        ('8:9:37', 'XXX Should give an exception'),
        ('08:9:37', 'XXX Should give an exception'),
        ('8:9', None),
        ('8', None),

        ]

    t = DateTime.now()

    for text, reference in l:
        try:
            value = TimeFromString(text, formats=('standard', 'iso'))
        except:
            if reference is None:
                continue
            else:
                value = str(sys.exc_info()[1])
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
        elif _debug:
            print 'Parsed "%s" successfully' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

if __name__ == '__main__':
    _test()
