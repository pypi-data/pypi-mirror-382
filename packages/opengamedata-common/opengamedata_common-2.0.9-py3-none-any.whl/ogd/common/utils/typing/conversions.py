"""Utility class with simple, "common-sense" parsing and warning logs for converting between types.

In particular, this is intended for use by config/schema classes,
where incoming values may be strings that must be parsed into the proper type internally.
"""

## import standard libraries
import builtins
import datetime
import json
import logging
import pathlib
import re
import typing
from typing import Any, Dict, List, LiteralString, Optional, Type

from json.decoder import JSONDecodeError
## import 3rd-party libraries
from pandas import Timedelta
from pandas._libs.tslibs import timestamps, timedeltas
from dateutil import parser
## import local files
from ogd.common.utils.Logger import Logger

# *** PUBLIC STATICS ***

def Capitalize(value:Any) -> Any:
    """Stupidly simple little function to convert any given strings to upper case, but allow non-strings to pass through unchanged.

    :param value: A value to be converted to upper case, if it's a string.
    :type value: Any
    :return: A capitalized version of `value`, if it was a string, else the original `value`.
    :rtype: Any
    """
    return value.upper() if isinstance(value, str) else value

def ConvertToType(value:Any, to_type:str | Type | List[Type], name:str="Unnamed Element") -> Any:
    """Applies whatever parsing is appropriate based on what type the schema said a column contained.

    :param value: _description_
    :type value: Any
    :param to_type: The desired type of the element.
        * If a string, the function will match against a set of recognized type names.
        * If a type, the function will match against a set of recognized types.
        * If a list of types, the function will attempt to match the raw value's type against all types in the list.  
            If a match is found, where "match" means the raw value is an instance of the given type, the return value will be the same type as the raw value.  
            If the raw value's type matches nothing in the list, the return value will be a parsed instance of the first type in the list.
            The function naively assumes the first type in the list is a recognized type; if it is not, a value of None will be returned.
    :type to_type: str | Type | List[Type]
    :param name: _description_
    :type name: str
    :return: _description_
    :rtype: Any
    """
    ret_val : Any

    if Capitalize(value) in [None, "NONE", "NULL", "NAN"]:
        ret_val = None
    # Handle case where there are multiple valid types accepted (i.e. got a list, and everything in list is a type/str)
    elif isinstance(to_type, List) and all(type(x) in {type, str} for x in to_type):
        found = False
        # for each candidate type, check if value already had that type
        for t in to_type:
            if isinstance(value, t):
                ret_val = value
                found = True
        # if we didn't find exact match between value and candidate type, make a "soft" parse attempt on each type
        # Also good gracious me it's a mother****ing while loop in Python, oh my days...
        i = 0
        while not found and i < len(to_type):
            _parsed = _parseToType(value=value, to_type=to_type[i], name=name)
            if _parsed is not None:
                ret_val = _parsed
                found = True
            i += 1

        # If none of the parsers knew how to handle the type of value param,
        # force the issue by calling a "hard" conversion on first type in list of candidate types.
        if not found:
            ret_val = ConvertToType(value, to_type=to_type[0], name=name)
    # Otherwise, handle recognized single types
    else:
        match Capitalize(to_type):
            case 'BOOL' | builtins.bool:
                ret_val = ToBool(name=name, value=value)
            case 'STR' | builtins.str:
                ret_val = ToString(name=name, value=value)
            case 'INT' | builtins.int:
                ret_val = ToInt(name=name, value=value)
            case 'FLOAT' | builtins.float:
                ret_val = ToFloat(name=name, value=value)
            case 'PATH' | pathlib.Path:
                ret_val = ToPath(name=name, value=value)
            case 'DATE' | datetime.date:
                raw_dt  = ToDatetime(name=name, value=value)
                ret_val = raw_dt.date() if raw_dt is not None else None
            case 'DATETIME' | datetime.datetime:
                ret_val = ToDatetime(name=name, value=value)
            case 'TIMEDELTA' | datetime.timedelta:
                ret_val = ToTimedelta(name=name, value=value)
            case 'TIMEZONE' | datetime.timezone:
                ret_val = ToTimezone(name=name, value=value)
            case 'JSON' | 'DICT' | builtins.dict | typing.Dict:
                ret_val = ToJSON(name=name, value=value)
            case 'LIST' | builtins.list | typing.List:
                ret_val = ToList(name=name, value=value)
            case _dummy if isinstance(_dummy, str) and _dummy.startswith('ENUM'):
                # if the column is supposed to be an enum, for now we just stick with the string.
                ret_val = str(value)
            case _:
                _msg = f"Requested type of {to_type} for '{name}' is unknown; defaulting to {name}=None"
                Logger.Log(_msg, logging.WARNING)
                ret_val = None
    return ret_val

def ToBool(name:str, value:Any, force:bool=False) -> Optional[bool]:
    """Attempt to turn a given value into a bool

    Returns None if the value type was not recognized

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a bool representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `bool` constructor on the `value`.
        Defaults to False.
    :type force: bool
    :return: The bool representation of value, if type of value was recognized, else None
    :rtype: Optional[bool]
    """
    ret_val : Optional[bool]

    match type(value):
        case builtins.bool:
            ret_val = value
        case builtins.int | builtins.float:
            ret_val = bool(value)
        case builtins.str:
            ret_val = BoolFromString(bool_str=value)
        case _:
            base_msg : str = f"{name} was unexpected type {type(value)}, expected a bool, float, int, or string!"
            if force:
                ret_val = BoolFromString(value)
                msg = f"{base_msg} Defaulting to BoolFromString(value) == {ret_val}."
            else:
                ret_val = None
                msg = f"{base_msg} Defaulting to None."
            Logger.Log(msg, logging.WARN)
    return ret_val

def ToInt(name:str, value:Any, force:bool=False) -> Optional[int]:
    """Attempt to turn a given value into an int

    Returns None if the value type was not recognized

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to an int representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `int` constructor on the `value`, which may raise error.
        If the constructor errors, None will be returned anyway.
        Defaults to False.
    :type force: bool
    :return: The int representation of value, if type of value was recognized, else None
    :rtype: Optional[int]
    """
    ret_val : Optional[int]

    try:
        match type(value):
            case builtins.int:
                ret_val = value
            case builtins.float:
                ret_val = int(round(value))
                Logger.Log(f"{name} was a float value, rounding to nearest int: {ret_val}.", logging.DEBUG)
            case builtins.str:
                ret_val = int(value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                if force:
                    ret_val = int(value)
                    msg = f"{base_msg} Defaulting to int(value) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
    except ValueError as err:
        Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to int, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
        ret_val = None
    return ret_val

def ToFloat(name:str, value:Any, force:bool=False) -> Optional[float]:
    """Attempt to turn a given value into a float

    Returns None if the value type was not recognized

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a float representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `float` constructor on the `value`.
        If the constructor errors, None will be returned anyway.
        Defaults to False.
    :type force: bool
    :return: The float representation of value, if type of value was recognized, else None
    :rtype: Optional[float]
    """
    ret_val : Optional[float]

    try:
        match type(value):
            case builtins.float:
                ret_val = value
            case builtins.int:
                ret_val = float(value)
            case builtins.str:
                ret_val = float(value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                if force:
                    ret_val = float(value)
                    msg = f"{base_msg} Defaulting to float(value) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
    except ValueError as err:
        Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to float, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
        ret_val = None
    return ret_val

def ToString(name:str, value:Any) -> str:
    """Attempt to turn a given value into a str

    Returns None if the value type was not recognized.
    This is a cheat, relative to other `To<Type>` functions in the class,
    because anything that is not a string will be converted with str(value).

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a str representation
    :type value: Any
    :return: The str representation of value, if type of value was recognized, else None
    :rtype: Optional[str]
    """
    ret_val : str

    match type(value):
        case builtins.str:
            ret_val = value
        case _:
            ret_val = str(value)
            # Logger.Log(f"{name} was unexpected type {type(value)}, expected a string! Defaulting to str(value) == {ret_val}", logging.WARN)
    return ret_val

def ToPath(name:str, value:Any, force:bool=False) -> Optional[pathlib.Path]:
    """Attempt to turn a given value into a path

    Returns None if the value type was not recognized.

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a path representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `Path` constructor on the `value`.
        If the constructor errors, None will be returned anyway.
        Defaults to False.
    :type force: bool
    :return: The path representation of value, if type of value was recognized, else None
    :rtype: Optional[path]
    """
    ret_val : Optional[pathlib.Path]

    try:
        match type(value):
            case dummy if issubclass(dummy, pathlib.Path):
                ret_val = value
            case builtins.str:
                ret_val = pathlib.Path(value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a Path or string!"
                if force:
                    ret_val = pathlib.Path(str(value))
                    msg = f"{base_msg} Defaulting to Path(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
    except TypeError as err:
        Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to Path, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
        ret_val = None
    return ret_val

def ToDatetime(name:str, value:Any, force:bool=False) -> Optional[datetime.datetime]:
    """Attempt to turn a given value into a datetime

    Returns None if the value type was not recognized.

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a datetime representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `DatetimeFromString` converter on the string of `value`.
        Defaults to False.
    :type force: bool
    :return: The datetime representation of value, if type of value was recognized, else None
    :rtype: Optional[datetime]
    """
    ret_val : Optional[datetime.datetime]

    match type(value):
        case datetime.datetime:
            ret_val = value
        case datetime.date:
            midnight = datetime.datetime.min.time()
            ret_val = datetime.datetime.combine(date=value, time=midnight)
            Logger.Log(f"{name} was a date value, defaulting to midnight of the given date: {ret_val}", logging.WARN)
        case builtins.str:
            ret_val = DatetimeFromString(time_str=value)
        case timestamps.Timestamp:
            ret_val = value.to_pydatetime()
        case _:
            base_msg : str = f"{name} was unexpected type {type(value)}, expected a datetime or string!"
            if force:
                ret_val = DatetimeFromString(str(value))
                msg = f"{base_msg} Defaulting to DatetimeFromString(str(value)) == {ret_val}."
            else:
                ret_val = None
                msg = f"{base_msg} Defaulting to None."
            Logger.Log(msg, logging.WARN)
    return ret_val

def ToTimedelta(name:str, value:Any, force:bool=False) -> Optional[datetime.timedelta]:
    """Attempt to turn a given value into a timedelta

    Returns None if the value type was not recognized.

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a timedelta representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `TimedeltaFromString` converter on the string of `value`.
        Defaults to False.
    :type force: bool
    :return: The timedelta representation of value, if type of value was recognized, else None
    :rtype: Optional[timedelta]
    """
    ret_val : Optional[datetime.timedelta]
    match type(value):
        case datetime.timedelta:
            ret_val = value
        case datetime.time:
            ret_val = value - datetime.datetime.min.time()
            Logger.Log(f"{name} was a time value, treating the time is difference from 0: {ret_val}", logging.WARN)
        case builtins.str:
            ret_val = TimedeltaFromString(time_str=value)
        case builtins.int:
            ret_val = datetime.timedelta(seconds=value)
        case timedeltas.Timedelta:
            ret_val = value.to_pytimedelta()
        case _:
            base_msg : str = f"{name} was unexpected type {type(value)}, expected a timedelta, time, or string!"
            if force:
                ret_val = TimedeltaFromString(str(value))
                msg = f"{base_msg} Defaulting to TimedeltaFromString(str(value)) == {ret_val}."
            else:
                ret_val = None
                msg = f"{base_msg} Defaulting to None."
            Logger.Log(msg, logging.WARN)
    return ret_val

def ToTimezone(name:str, value:Any, force:bool=False) -> Optional[datetime.timezone]:
    """Attempt to turn a given value into a timezone

    .. TODO use timedelta from string, possibly, and then create timezone from the delta

    Returns None if the value type was not recognized.

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a timezone representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `TimezoneFromString` convertor on the string of `value`.
        Defaults to False.
    :type force: bool
    :return: The timezone representation of value, if type of value was recognized, else None
    :rtype: Optional[timezone]
    """
    ret_val : Optional[datetime.timezone]
    match type(value):
        case datetime.timezone:
            ret_val = value
        case datetime.timedelta:
            ret_val = datetime.timezone(value)
        case builtins.str:
            ret_val = TimezoneFromString(time_str=value)
        case _:
            base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
            if force:
                ret_val = TimezoneFromString(str(value))
                msg = f"{base_msg} Defaulting to TimezoneFromString(str(value)) == {ret_val}."
            else:
                ret_val = None
                msg = f"{base_msg} Defaulting to None."
            Logger.Log(msg, logging.WARN)
    return ret_val

def ToList(name:str, value:Any, force:bool=False) -> Optional[List]:
    """Attempt to turn a given value into a list

    Returns None if the value type was not recognized.

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a list representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `List` constructor on the `value`.
        If the constructor errors, None will be returned anyway.
        Defaults to False.
    :type force: bool
    :return: The list representation of value, if type of value was recognized, else None
    :rtype: Optional[List]
    """
    ret_val : Optional[List]
    try:
        match type(value):
            case builtins.list:
                # if input was a list already, then just give it back. Else, try to load it from string.
                ret_val = value
            case builtins.str:
                if value not in {'None', 'null', ''}: # watch out for nasty corner cases.
                    ret_val = list(json.loads(value))
                else:
                    ret_val = None
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a list or string!"
                if force:
                    ret_val = list(json.loads(str(value)))
                    msg = f"{base_msg} Defaulting to list(json.loads(str(value))) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
    except JSONDecodeError as err:
        Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to list, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
        ret_val = None
    return ret_val

def ToJSON(name:str, value:Any, force:bool=False, sort:bool=False) -> Optional[Dict]:
    """Attempt to turn a given value into a JSON-style dictionary

    Returns None if the value type was not recognized.

    .. TODO: Add a 'sanitize' param to purge anything that looks like an IP address or other pii

    :param name: An identifier for the value, used for debug outputs.
    :type name: str
    :param value: The value to parse to a JSON representation
    :type value: Any
    :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
        If False, return None when such cases arise. If True, attempt to use `Dict` constructor on the `value`.
        If the constructor errors, None will be returned anyway.
        Defaults to False.
    :type force: bool
    :return: The JSON representation of value, if type of value was recognized, else None
    :rtype: Optional[Dict]
    """
    ret_val : Optional[Dict]
    try:
        match type(value):
            case builtins.dict:
                # if input was a dict already, then just give it back. Else, try to load it from string.
                ret_val = value
            case builtins.str:
                if value not in {'None', ''}: # watch out for nasty corner cases.
                    ret_val = json.loads(value)
                else:
                    ret_val = None
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a dict or string!"
                if force:
                    ret_val = json.loads(str(value))
                    msg = f"{base_msg} Defaulting to json.loads(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
    except JSONDecodeError as err:
        Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to JSON, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
        ret_val = None
    if sort and ret_val is not None:
        ret_val = dict(sorted(ret_val.items()))
    return ret_val

def BoolFromString(bool_str:str) -> bool:
    ret_val : bool

    match bool_str.upper():
        case 'TRUE' | 'YES':
            ret_val = True
        case 'FALSE' | 'NO':
            ret_val = False
        case _:
            ret_val = bool(bool_str)
    return ret_val

def DatetimeFromString(time_str:str) -> Optional[datetime.datetime]:
    """_summary_

    TODO : handle null inputs!
    TODO : handle more date formats, or something. I dunno, copied this from another area where we were parsing dates.

    :param time_str: _description_
    :type time_str: str
    :raises ValueError: _description_
    :raises ValueError: _description_
    :return: _description_
    :rtype: datetime.datetime
    """
    ret_val : Optional[datetime.datetime] = None

    if time_str == None or time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
        raise ValueError(f"Got a non-timestamp value of {time_str} when converting a datetime column from data source!")

    # Approach 1: use dateutil parser to parse, assuming an iso format
    try:
        ret_val = parser.isoparse(time_str)
    # Approach 2: if dateutil threw error, try using the general parse
    except ValueError:
        Logger.Log(f"Attempted to convert a time string that was not in ISO format: {time_str}, switching to general parser instead!", logging.DEBUG)
        try:
            ret_val = parser.parse(time_str)
        except ValueError:
            Logger.Log(f"Could not parse timestamp {time_str}, it did not match any expected formats!", logging.WARNING)
        else:
            pass
    else:
        pass

    return ret_val

@staticmethod
def TimedeltaFromString(time_str:str) -> Optional[datetime.timedelta]:
    ret_val : Optional[datetime.timedelta]

    if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
        ret_val = None
    else:
        neg_pattern    : LiteralString = r"(?P<neg>-)"
        day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
        hour_pattern   : LiteralString = r"(?P<hour>\d+)"
        minute_pattern : LiteralString = r"(?P<minute>\d+)"
        second_pattern : LiteralString = r"(?P<second>\d+)"
        micros_pattern : LiteralString = r"(?P<micros>\d+)"
        pattern = re.compile(f"{neg_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}:{second_pattern}\\.{micros_pattern}")

        match = re.fullmatch(pattern=pattern, string=time_str)
        if match:
            ret_val = datetime.timedelta(
                days=int(match.group("day") or 0),
                hours=int(match.group("hour") or 0),
                minutes=int(match.group("minute") or 0),
                seconds=int(match.group("second") or 0),
                microseconds=int(match.group("micros") or 0)
            )
            # if we matched the negative sign, then make the timedelta negative.
            if match.group("neg"):
                ret_val = -ret_val
        else:
            match = re.fullmatch(pattern=r"-?\d+", string=time_str)
            if match:
                ret_val = datetime.timedelta(seconds=int(time_str))
            else:
                Logger.Log(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats. Parsing with Pandas instead.", logging.WARNING)
                ret_val = Timedelta(time_str).to_pytimedelta()
    
    return ret_val

def TimezoneFromString(time_str:str) -> Optional[datetime.timezone]:
    ret_val : Optional[datetime.timezone]

    offset : Optional[datetime.timedelta] = None
    if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
        return None
    else:
        utc_pattern    : LiteralString = r"(?P<utc>UTC)"
        dir_pattern    : LiteralString = r"(?P<dir>\+|-)"
        day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
        hour_pattern   : LiteralString = r"(?P<hour>\d+)"
        minute_pattern : LiteralString = r"(?P<minute>\d+)"
        second_pattern : LiteralString = r"(?P<second>\d+)"
        micros_pattern : LiteralString = r"(?P<micros>\d+)"
        raw_pattern = f"{utc_pattern}?{dir_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}:{second_pattern}(\\.{micros_pattern})?"
        pattern = re.compile(raw_pattern)

        match = re.fullmatch(pattern=pattern, string=time_str)
        if match:
            offset = datetime.timedelta(
                days=int(match.group("day") or 0),
                hours=int(match.group("hour") or 0),
                minutes=int(match.group("minute") or 0),
                seconds=int(match.group("second") or 0),
                microseconds=int(match.group("micros") or 0)
            )
            # if we matched the negative sign, then make the timedelta negative.
            if match.group("dir") == "-":
                offset = -1*offset
        else:
            match = re.fullmatch(pattern=r"-?\d+", string=time_str)
            if match:
                offset = datetime.timedelta(seconds=int(time_str))
            else:
                Logger.Log(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats.", logging.WARNING)
        if offset:
            MAX_OFFSET = 24*60*60
            if offset.total_seconds() > MAX_OFFSET:
                offset = datetime.timedelta(seconds=offset.total_seconds() % MAX_OFFSET)
            if offset.total_seconds() < -24*60*60:
                offset = datetime.timedelta(seconds=(offset.total_seconds() % MAX_OFFSET) - MAX_OFFSET)

        ret_val = datetime.timezone(offset=offset) if offset is not None else None
        return ret_val
    raise ValueError(f"Could not parse timezone {time_str} of type {type(time_str)}, it did not match any expected formats.")

# *** PUBLIC METHODS ***

# *** PRIVATE STATICS ***

def _parseToType(value:Any, to_type:str | Type, name:str="Unnamed Element") -> Any:
    """Private function to attempt to parse a value to a specific type.

    Unlike the main ConvertToType function, however,
    this function will not attempt a conversion if the type of the "value" variable is not recognized.
    Instead, it will simply return None

    :param value: _description_
    :type value: Any
    :param to_type: _description_
    :type to_type: str | Type | List[Type]
    :param name: _description_
    :type name: str
    :return: _description_
    :rtype: Any
    """
    ret_val : Any

    if value is None:
        ret_val = None
    elif value == "None" or value == "null" or value == "nan":
        ret_val = None
    else:
        match (Capitalize(to_type)):
            case 'BOOL' | builtins.bool:
                ret_val = ToBool(name=name, value=value)
            case 'STR' | builtins.str:
                ret_val = ToString(name=name, value=value)
            case 'INT' | builtins.int:
                ret_val = ToInt(name=name, value=value)
            case 'FLOAT' | builtins.float:
                ret_val = ToFloat(name=name, value=value)
            case 'PATH' | pathlib.Path:
                ret_val = ToPath(name=name, value=value)
            case 'DATE' | datetime.date:
                raw_dt  = ToDatetime(name=name, value=value)
                ret_val = raw_dt.date() if raw_dt is not None else None
            case 'DATETIME' | datetime.datetime:
                ret_val = ToDatetime(name=name, value=value)
            case 'TIMEDELTA' | datetime.timedelta:
                ret_val = ToTimedelta(name=name, value=value)
            case 'TIMEZONE' | datetime.timezone:
                ret_val = ToTimezone(name=name, value=value)
            case 'JSON' | 'DICT' | builtins.dict | typing.Dict:
                ret_val = ToJSON(name=name, value=value)
            case 'LIST' | builtins.list | typing.List:
                ret_val = ToList(name=name, value=value)
            case _dummy if isinstance(_dummy, str) and _dummy.startswith('ENUM'):
                # if the column is supposed to be an enum, for now we just stick with the string.
                ret_val = str(value)
            case _:
                _msg = f"Requested type of {to_type} for '{name}' is unknown; defaulting to {name}=None"
                Logger.Log(_msg, logging.WARNING)
                ret_val = None
    return ret_val

# *** PRIVATE METHODS ***