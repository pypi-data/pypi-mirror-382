## import standard libraries
from datetime import datetime, timedelta, timezone
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple, Union
# import local files
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapElement
from ogd.common.models.GameData import GameData
from ogd.common.models import SemanticVersion as SV
from ogd.common.utils.typing import ExportRow, Map, conversions, Version

class EventSource(IntEnum):
    """Enum for the possible sources of an event - a game, or a generator.
    """
    GAME = 1
    GENERATED = 2

## @class Event
class Event(GameData):
    """
    Completely dumb struct that enforces a particular structure for the data we get from a source.
    Basically, whenever we fetch data, the TableConfig will be used to map columns to the required elements of an Event.
    Then the extractors etc. can just access columns in a direct manner.
    """

    # *** BUILT-INS & PROPERTIES ***

    _latest_session = None
    _latest_index   = 0
    def __init__(self, app_id:str,              user_id:Optional[str],          session_id:str,
                 app_version:Optional[Version], app_branch:Optional[str],       log_version:Optional[Version],     
                 timestamp:datetime,            time_offset:Optional[timezone], event_sequence_index:Optional[int],
                 event_name:str,                event_source:"EventSource",     event_data:Map,
                 game_state:Optional[Map],      user_data:Optional[Map]):
        """Constructor for an Event struct

        :param app_id: _description_
        :type app_id: str
        :param user_id: _description_
        :type user_id: Optional[str]
        :param session_id: _description_
        :type session_id: str
        :param app_version: _description_
        :type app_version: Optional[str]
        :param app_branch: _description_
        :type app_branch: Optional[str]
        :param log_version: _description_
        :type log_version: Optional[str]
        :param timestamp: _description_
        :type timestamp: datetime
        :param time_offset: _description_
        :type time_offset: Optional[timezone]
        :param event_sequence_index: _description_
        :type event_sequence_index: Optional[int]
        :param event_name: _description_
        :type event_name: str
        :param event_source: _description_
        :type event_source: EventSource
        :param event_data: _description_
        :type event_data: Map
        :param game_state: _description_
        :type game_state: Optional[Map]
        :param user_data: _description_
        :type user_data: Optional[Map]
        """
        super().__init__(app_id=app_id,           user_id=user_id,       session_id=session_id)
        self.app_version          : Version       = app_version if app_version is not None else SV.SemanticVersion(0)
        self.app_branch           : str           = app_branch  if app_branch  is not None else "main"
        self.log_version          : Version       = log_version if log_version is not None else SV.SemanticVersion(0)
        self.timestamp            : datetime      = timestamp
        self.time_offset          : Optional[timezone] = time_offset
        self.event_sequence_index : Optional[int] = event_sequence_index
        self.event_name           : str           = event_name
        self.event_source         : EventSource   = event_source
        self.event_data           : Map           = event_data
        self.game_state           : Map           = game_state if game_state is not None else {}
        self.user_data            : Map           = user_data if user_data is not None else {}
        self._hash                : Optional[int] = None

    def __str__(self):
        return f"app_id       : {self.app_id}\n"\
             + f"user_id      : {self.user_id}\n"\
             + f"session_id   : {self.session_id}\n"\
             + f"app_version  : {self.app_version}\n"\
             + f"app_branch   : {self.app_branch}\n"\
             + f"log_version  : {self.log_version}\n"\
             + f"timestamp    : {self.timestamp}\n"\
             + f"offset       : {self.TimeOffsetString}\n"\
             + f"index        : {self.event_sequence_index}\n"\
             + f"event_name   : {self.event_name}\n"\
             + f"event_source : {self.event_source.name}\n"\
             + f"event_data   : {self.event_data}\n"\
             + f"game_state   : {self.game_state}\n"\
             + f"user_data    : {self.user_data}\n"\

    def __hash__(self):
        _elems = [self.AppID, self.UserID, self.SessionID,
                  self.AppVersion, self.AppBranch, self.LogVersion,
                  self.Timestamp, self.TimeOffset, self.EventSequenceIndex,
                  self.EventName, self.EventSource, self.EventData,
                  self.GameState, self.UserData]
        _str_elems = [str(elem) for elem in _elems]
        return hash("".join(_str_elems))

    # *** PROPERTIES ***

    @property
    def ColumnValues(self) -> Tuple[Optional[str | datetime | timezone | Map | int], ...]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        return (self.session_id,       self.app_id,             self.timestamp,        self.event_name,
                self.event_data,       self.event_source.name,  self.AppVersionString, self.app_branch,
                self.LogVersionString, self.TimeOffsetString,   self.user_id,          self.user_data,
                self.game_state,       self.event_sequence_index)

    @property
    def Hash(self) -> int:
        if not self._hash:
            self._hash = hash(self)
        return self._hash

    @property
    def AppVersion(self) -> Version:
        """The semantic versioning value for the game that generated this Event.

        Some legacy games may use a single integer or a string similar to AppID in this column.

        :return: The semantic versioning string for the game that generated this Event
        :rtype: str
        """
        return self.app_version
    @property
    def AppVersionString(self) -> str:
        """The semantic versioning string for the game that generated this Event.

        :return: The semantic versioning string for the game that generated this Event
        :rtype: str
        """
        return str(self.AppVersion)

    @property
    def AppBranch(self) -> str:
        """The name of the branch of a game version that generated this Event.

        The branch name is typically used for cases where multiple experimental versions of a game are deployed in parallel;
        most events will simply have a branch of "main" or "master."

        :return: The name of the branch of a game version that generated this Event
        :rtype: str
        """
        return self.app_branch

    @property
    def LogVersion(self) -> Version:
        """The version of the logging schema implemented in the game that generated the Event

        For most games, this is a single integer; however, semantic versioning is valid for this column as well.

        :return: The version of the logging schema implemented in the game that generated the Event
        :rtype: str
        """
        return self.log_version
    @property
    def LogVersionString(self) -> str:
        """The versioning string of the logging schema implemented in the game that generated the Event.

        :return: The semantic versioning string for the logging schema implemented in the game that generated the Event
        :rtype: str
        """
        return str(self.LogVersion)

    @property
    def Timestamp(self) -> datetime:
        """A UTC timestamp of the moment at which the game client sent the Event

        The timestamp is based on the GMT timezone, in keeping with UTC standards.
        Some legacy games may provide the time based on a local time zone, rather than GMT.

        :return: A UTC timestamp of the moment at which the game client sent the event
        :rtype: datetime
        """
        return self.timestamp

    @property
    def TimeOffset(self) -> Optional[timezone]:
        """A timedelta for the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset

    @property
    def TimeOffsetString(self) -> Optional[str]:
        """A string representation of the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset.tzname(None) if self.time_offset is not None else None

    @property
    def EventSequenceIndex(self) -> Optional[int]:
        """A strictly-increasing counter indicating the order of events in a session.

        The first event in a session has EventSequenceIndex == 0, the next has index == 1, etc.

        :return: A strictly-increasing counter indicating the order of events in a session
        :rtype: int
        """
        return self.event_sequence_index

    @property
    def EventName(self) -> str:
        """The name of the specific type of event that occurred

        For some legacy games, the names in this column have a format of CUSTOM.1, CUSTOM.2, etc.
        For these games, the actual human-readable event names for these events are stored in the EventData column.
        Please see individual game logging documentation for details.

        :return: The name of the specific type of event that occurred
        :rtype: str
        """
        return self.event_name

    @property
    def EventData(self) -> Map:
        """A dictionary containing data specific to Events of this type.

        For details, see the documentation in the given game's README.md, included with all datasets.
        Alternately, review the {GAME_NAME}.json file for the given game.

        :return: A dictionary containing data specific to Events of this type
        :rtype: Dict[str, Any]
        """
        return self.event_data

    @property
    def EventSource(self) -> EventSource:
        """An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector.

        :return: An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector
        :rtype: EventSource
        """
        return self.event_source

    @property
    def UserData(self) -> Map:
        """A dictionary containing any user-specific data tracked across gameplay sessions or individual games.

        :return: A dictionary containing any user-specific data tracked across gameplay sessions or individual games
        :rtype: Dict[str, Any]
        """
        return self.user_data

    @property
    def GameState(self) -> Map:
        """A dictionary containing any game-specific data that is defined across all event types in the given game.

        This column typically includes data that offers context to a given Event's data in the EventData column.
        For example, this column would typically include a level number or quest name for whatever level/quest the user was playing when the Event occurred.

        :return: A dictionary containing any game-specific data that is defined across all event types in the given game
        :rtype: Dict[str, Any]
        """
        return self.game_state

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    @staticmethod
    def ColumnNames() -> List[str]:
        """_summary_

        TODO: In Event schema 1.0, set order to match ordering of `__init__` function, which is meant to be better-organized.

        :return: _description_
        :rtype: List[str]
        """
        return ["session_id",  "app_id",       "timestamp",   "event_name",
                "event_data",  "event_source", "app_version", "app_branch",
                "log_version", "offset",        "user_id",    "user_data",
                "game_state",  "index"]

    @staticmethod
    def FromJSON(json_data:Dict) -> "Event":
        """_summary_

        TODO : rename to FromDict, and make classmethod, to match conventions of schemas.

        :param json_data: _description_
        :type json_data: Dict
        :return: _description_
        :rtype: Event
        """
        return Event(
            session_id  =json_data.get("session_id", "SESSION ID NOT FOUND"),
            app_id      =json_data.get("app_id", "APP ID NOT FOUND"),
            timestamp   =json_data.get("client_time", "CLIENT TIME NOT FOUND"),
            event_name  =json_data.get("event_name", "EVENT NAME NOT FOUND"),
            event_data  =json_data.get("event_data", "EVENT DATA NOT FOUND"),
            event_source=EventSource.GAME,
            app_version =json_data.get("app_version", None),
            app_branch  =json_data.get("app_branch", None),
            log_version =json_data.get("log_version", None),
            time_offset =None,
            user_id     =json_data.get("user_id", None),
            user_data   =json_data.get("user_data", None),
            game_state  =json_data.get("game_state", None),
            event_sequence_index=json_data.get("event_sequence_index", json_data).get("session_n", None)
        )

    @classmethod
    def FromRow(cls, row:ExportRow, schema:EventTableSchema, fallbacks:Map={}) -> "Event":
        """Function to convert a row to an Event, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        .. TODO Use conversions utils to deal with the types we're getting from the row.

        :param row: _description_
        :type row: Tuple
        :param concatenator: _description_, defaults to '.'
        :type concatenator: str, optional
        :param fallbacks: _description_, defaults to {}
        :type fallbacks: Map, optional
        :raises TypeError: _description_
        :return: _description_
        :rtype: Event
        """
        ret_val : Event

        # define vars to be passed as params
        app_id      : str
        user_id     : Optional[str]
        sess_id     : str
        app_ver     : Version
        app_br      : str
        log_ver     : Version
        tstamp      : datetime
        offset      : Optional[timezone]
        event_index : Optional[int]
        ename       : str
        edata       : Map
        state       : Optional[Map]
        udata       : Optional[Map]

        # 1. Get ID data
        app_id = schema.ColumnValueFromRow(row=row, mapping=schema.Map.AppIDColumn, concatenator=".",
                                           column_name="app_id", expected_type=str, fallback=fallbacks.get("app_id"))
        if not isinstance(app_id, str):
            app_id = conversions.ToString(name="app_id", value=app_id)

        user_id = schema.ColumnValueFromRow(row=row, mapping=schema.Map.UserIDColumn, concatenator=".",
                                            column_name="user_id", expected_type=str, fallback=fallbacks.get("user_id"))
        if user_id is not None and not isinstance(user_id, str):
            user_id = conversions.ToString(name="user_id", value=user_id)

        sess_id = schema.ColumnValueFromRow(row=row, mapping=schema.Map.SessionIDColumn, concatenator=".",
                                            column_name="sess_id", expected_type=str, fallback=fallbacks.get("session_id"))
        if not isinstance(sess_id, str):
            sess_id = conversions.ToString(name="session_id", value=sess_id)
        if cls._latest_session != sess_id:
            cls._latest_session = sess_id
            cls._next_index = 0

        # 2. Get versioning data
        expected_types = [str, int, SV.SemanticVersion]
        log_ver = schema.ColumnValueFromRow(row=row, mapping=schema.Map.LogVersionColumn, concatenator=".",
                                            column_name="log_ver", expected_type=SV.SemanticVersion, fallback=fallbacks.get('log_version', "0"))
        if not any(isinstance(log_ver, t) for t in expected_types):
            log_ver = SV.SemanticVersion.FromString(semver=str(log_ver))

        app_ver = schema.ColumnValueFromRow(row=row, mapping=schema.Map.AppVersionColumn, concatenator=".",
                                            column_name="app_ver", expected_type=SV.SemanticVersion, fallback=fallbacks.get('app_version'))
        if not any(isinstance(app_ver, t) for t in expected_types):
            app_ver = SV.SemanticVersion.FromString(semver=str(app_ver))

        app_br = schema.ColumnValueFromRow(row=row, mapping=schema.Map.AppBranchColumn, concatenator=".",
                                           column_name="app_br", expected_type=str, fallback=fallbacks.get('app_branch'))
        if not isinstance(app_br, str):
            app_br = conversions.ToString(name="app_branch", value=app_br)

        # 3. Get sequencing data
        tstamp  = schema.ColumnValueFromRow(row=row, mapping=schema.Map.TimestampColumn, concatenator=".",
                                            column_name="timestamp", expected_type=datetime, fallback=None)
        if not isinstance(tstamp, datetime):
            tstamp = conversions.ToDatetime(name="timestamp", value=tstamp, force=True)

        offset = schema.ColumnValueFromRow(row=row, mapping=schema.Map.TimeOffsetColumn, concatenator=".",
                                           column_name="offset", expected_type=str, fallback=fallbacks.get('time_offset'))
        if isinstance(offset, timedelta):
            offset = conversions.ToTimezone(name="offset", value=offset, force=True)

        event_index = schema.ColumnValueFromRow(row=row, mapping=schema.Map.EventSequenceIndexColumn, concatenator=".",
                                                column_name="index", expected_type=int, fallback=fallbacks.get('event_sequence_index', cls._next_index))
        if not isinstance(event_index, int):
            event_index = conversions.ToInt(name="event_sequence_index", value=event_index or cls._next_index, force=True)

        # 4. Get event-specific data
        ename   = schema.ColumnValueFromRow(row=row, mapping=schema.Map.EventNameColumn, concatenator=".",
                                            column_name="ename", expected_type=str, fallback=fallbacks.get('event_name'))
        if not isinstance(ename, str):
            ename = conversions.ToString(name="event_name", value=ename)

        esrc = schema.ColumnValueFromRow(row=row, mapping=schema.Map.EventSourceColumn, concatenator=".",
                                         column_name="esrc", expected_type=str, fallback=fallbacks.get('event_source', EventSource.GAME))
        if not isinstance(esrc, EventSource):
            esrc = EventSource.GENERATED if esrc == "GENERATED" else EventSource.GAME

        raw_data = schema.ColumnValueFromRow(row=row, mapping=schema.Map.EventDataColumn, concatenator=".",
                                             column_name="edata", expected_type=dict, fallback=fallbacks.get('event_data'))
        edata   = conversions.ToJSON(name="event_data", value=raw_data, force=True, sort=True) or {}

        # 5. Get context data

        udata   = schema.ColumnValueFromRow(row=row, mapping=schema.Map.UserDataColumn, concatenator=".",
                                            column_name="udata", expected_type=dict, fallback=fallbacks.get('user_data'))

        raw_state = schema.ColumnValueFromRow(row=row, mapping=schema.Map.GameStateColumn, concatenator=".",
                                            column_name="state", expected_type=dict, fallback=fallbacks.get('game_state'))
        state     = conversions.ToJSON(name="game_state", value=raw_state, force=True, sort=True) or {}

        ret_val = Event(app_id=app_id, user_id=user_id, session_id=sess_id,
                        timestamp=tstamp, time_offset=offset, event_sequence_index=event_index,
                        event_name=ename, event_source=esrc, event_data=edata,
                        app_version=app_ver, app_branch=app_br, log_version=log_ver,
                        user_data=udata, game_state=state, )
        ret_val.ApplyFallbackDefaults(index=cls._next_index)
        cls._next_index = (event_index or cls._next_index) + 1

        return ret_val

    # *** PUBLIC METHODS ***

    def ApplyFallbackDefaults(self, app_id:Optional[str]=None, index:Optional[int]=None, in_place:bool=True) -> "Event":
        ret_val : Event

        if in_place:
            if self.app_id == None and app_id != None:
                self.app_id = app_id
            if self.event_sequence_index == None:
                self.event_sequence_index = index
            ret_val = self
        else:
            ret_val = Event(
                app_id               = self.app_id               if self.app_id is not None or app_id is None else app_id,
                event_sequence_index = self.event_sequence_index if self.event_sequence_index is not None     else index,

                user_id=self.UserID, session_id=self.SessionID,
                app_version=self.AppVersion, app_branch=self.AppBranch, log_version=self.LogVersion,
                timestamp=self.Timestamp, time_offset=self.TimeOffset,
                event_name=self.EventName, event_source=self.EventSource, event_data=self.EventData,
                game_state=self.GameState, user_data=self.UserData
            )
        return ret_val

    def ToRow(self, schema:EventTableSchema) -> ExportRow:
        ret_val : List = [None]*len(schema.Columns)

        all_elems : Dict[str, Tuple[Any, ColumnMapElement]] = {
            "app_id"     : (self.AppID, schema.Map.AppIDColumn),
            "user_id"    : (self.UserID, schema.Map.UserIDColumn),
            "session_id" : (self.SessionID, schema.Map.SessionIDColumn),
            "log_ver"    : (self.LogVersion, schema.Map.LogVersionColumn),
            "app_ver"    : (self.AppVersion, schema.Map.AppVersionColumn),
            "app_branch" : (self.AppBranch, schema.Map.AppBranchColumn),
            "timestamp"  : (self.Timestamp, schema.Map.TimestampColumn),
            "offset"     : (self.TimeOffset, schema.Map.TimeOffsetColumn),
            "index"      : (self.EventSequenceIndex, schema.Map.EventSequenceIndexColumn),
            "event_name" : (self.EventName, schema.Map.EventNameColumn),
            "event_src"  : (self.EventSource, schema.Map.EventSourceColumn),
            "event_data" : (self.EventData, schema.Map.EventDataColumn),
            "user_data"  : (self.UserData, schema.Map.UserDataColumn),
            "game_state" : (self.GameState, schema.Map.GameStateColumn)
        }

        for key, details in all_elems.items():
            mapped = schema.ColumnValueToRow(raw_value=details[0], mapping=details[1],
                                             concatenator=".",     element_name=key)
            for idx, val in mapped.items():
                ret_val[idx] = val
            
        return tuple(ret_val)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

