from typing import Any, Dict, List, Optional, Tuple

from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.GameData import GameData
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapElement
from ogd.common.utils.typing import ExportRow, Map, conversions

class Feature(GameData):
    """
    
    .. todo:: Add element to track the feature extractor version in some way.

    :param GameData: _description_
    :type GameData: _type_
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, feature_type:str,
                 game_unit:Optional[str], game_unit_index:Optional[int],
                 app_id:str, user_id:Optional[str], session_id:str,
                 subfeatures:List[str], values:List[Any]):
        """_summary_

        :param name: _description_
        :type name: str
        :param feature_type: _description_
        :type feature_type: str
        :param game_unit: _description_
        :type game_unit: Optional[str]
        :param game_unit_index: _description_
        :type game_unit_index: Optional[int]
        :param app_id: _description_
        :type app_id: str
        :param user_id: _description_
        :type user_id: Optional[str]
        :param session_id: _description_
        :type session_id: str
        :param subfeatures: _description_
        :type subfeatures: List[str]
        :param values: _description_
        :type values: List[Any]
        """
        super().__init__(app_id=app_id, user_id=user_id, session_id=session_id)
        self._name = name
        self._feature_type = feature_type
        self._game_unit = game_unit
        self._game_unit_index = game_unit_index
        self._subfeatures = subfeatures
        self._values  = values

    def __str__(self) -> str:
        return f"Name: {self.Name}\tGame Unit: {self.GameUnit}{self.GameUnitIndex}\nValue: {self._values}\nPlayer: {self.PlayerID}\tSession: {self.SessionID}"

    def __repr__(self) -> str:
        return self.Name

    # *** PROPERTIES ***

    @property
    def ColumnValues(self) -> List[Tuple[Any, ...]]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        return [
            (
                feat_name,  self.FeatureType, self.GameUnit,  self.GameUnitIndex,
                self.AppID, self.UserID,      self.SessionID, self.ValueMap.get(feat_name)
            )
            for feat_name in self.FeatureNames
        ]

    @property
    def ExportMode(self) -> ExportMode:
        if self.PlayerID == "*" and self.SessionID == "*":
            return ExportMode.POPULATION
        elif self.SessionID == "*":
            return ExportMode.PLAYER
        else:
            return ExportMode.SESSION

    @property
    def Name(self) -> str:
        return self._name

    @property
    def FeatureType(self) -> str:
        return self._feature_type

    @property
    def GameUnit(self) -> str:
        return self._game_unit or "*"

    @property
    def GameUnitIndex(self) -> str | int:
        return self._game_unit_index or "*"
    @property
    def CountIndex(self) -> str | int:
        return self.GameUnitIndex

    @property
    def Subfeatures(self) -> List[str]:
        return self._subfeatures

    @property
    def FeatureNames(self) -> List[str]:
        return [self.Name] + self._subfeatures

    @property
    def Values(self) -> List[Any]:
        """Ordered list of values from the feature.

        The first is the base value, and each value after corresponds to the subfeature in the same order in Subfeatures.

        :return: _description_
        :rtype: List[Any]
        """
        return self._values
    @property
    def FeatureValues(self) -> List[Any]:
        """Alias for `Values` property

        Ordered list of values from the feature.
        The first is the base value, and each value after corresponds to the subfeature in the same order in Subfeatures.

        :return: _description_
        :rtype: List[Any]
        """
        return self.Values

    @property
    def ValueMap(self) -> Dict[str, Any]:
        ret_val : Dict[str, Any]

        if len(self.FeatureNames) != len(self.Values):
            raise ValueError(f"For {self.Name}, number of Features did not match number of values!")
        else:
            ret_val = {self.FeatureNames[i] : self.Values[i] for i in range(len(self.FeatureNames))}
        
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    @staticmethod
    def ColumnNames() -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["name",   "feature_type", "game_unit",  "game_unit_index", 
                "app_id", "user_id",      "session_id", "value"]

    @staticmethod
    def FromJSON(json_data:Dict) -> "Feature":
        """_summary_

        TODO : rename to FromDict, and make classmethod, to match conventions of schemas.

        :param json_data: _description_
        :type json_data: Dict
        :return: _description_
        :rtype: Event
        """
        return Feature(
            name             =json_data.get("feature_name", json_data.get("name", "FEATURE NAME NOT FOUND")),
            feature_type     =json_data.get("feature_type", "FEATURE TYPE NOT FOUND"),
            game_unit        =json_data.get("game_unit", "GAME UNIT NOT FOUND"),
            game_unit_index  =json_data.get("game_unit_index", "GAME UNIT INDEX NOT FOUND"),
            app_id           =json_data.get("app_id", "APP ID NOT FOUND"),
            user_id          =json_data.get("user_id", "USER ID NOT FOUND"),
            session_id       =json_data.get("session_id", "SESSION ID NOT FOUND"),
            subfeatures      =json_data.get("subfeatures", []),
            values           =json_data.get("values", ["VALUE NOT FOUND"]),
        )

    @classmethod
    def FromRow(cls, row:ExportRow, schema:FeatureTableSchema, fallbacks:Map={}) -> "Feature":
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
        ret_val : Feature

        # define vars to be passed as params
        fname      : str
        ftype      : str
        unit       : Optional[str]
        unit_index : Optional[int]
        app_id     : str
        user_id    : Optional[str]
        sess_id    : str
        subfeats   : List[str]
        vals       : List[str]

        # 1. Get Feature info
        fname = schema.ColumnValueFromRow(row=row, mapping=schema.Map.FeatureNameColumn, concatenator=".",
                                          column_name="feature_name", expected_type=str, fallback=fallbacks.get("feature_name"))
        if not isinstance(fname, str):
            fname = conversions.ToString(name="feature_name", value=fname)

        ftype = schema.ColumnValueFromRow(row=row, mapping=schema.Map.FeatureTypeColumn, concatenator=".",
                                          column_name="feature_type", expected_type=str, fallback=fallbacks.get("feature_type"))
        if not isinstance(ftype, str):
            feat_name = conversions.ToString(name="feature_type", value=ftype)

        # 2. Get game unit info
        unit = schema.ColumnValueFromRow(row=row, mapping=schema.Map.GameUnitColumn, concatenator=".",
                                         column_name="game_unit", expected_type=str, fallback=fallbacks.get("game_unit"))
        if not isinstance(feat_name, str):
            unit = conversions.ToString(name="game_unit", value=unit)

        unit_index = schema.ColumnValueFromRow(row=row, mapping=schema.Map.GameUnitIndexColumn, concatenator=".",
                                              column_name="game_unit_index", expected_type=str, fallback=fallbacks.get("game_unit_index"))
        if not isinstance(feat_name, str):
            unit_index = conversions.ToInt(name="game_unit_index", value=unit_index)

        # 3. Get ID data
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

        # 4. Get feature-specific data
        raw_subs = schema.ColumnValueFromRow(row=row, mapping=schema.Map.SubfeaturesColumn, concatenator=", ",
                                            column_name="subfeatures", expected_type=list, fallback=fallbacks.get('subfeatures'))
        subfeats = conversions.ToList(name="subfeatures", value=raw_subs, force=True) or []

        raw_vals = schema.ColumnValueFromRow(row=row, mapping=schema.Map.ValuesColumn, concatenator=", ",
                                            column_name="values", expected_type=list, fallback=fallbacks.get('values'))
        vals = conversions.ToList(name="values", value=raw_vals, force=True) or []

        ret_val = Feature(name=fname, feature_type=ftype,
                       game_unit=unit, game_unit_index=unit_index,
                       app_id=app_id, user_id=user_id, session_id=sess_id,
                       subfeatures=subfeats, values=vals)
        # ret_val.ApplyFallbackDefaults(index=cls._next_index)
        # cls._next_index = (event_index or cls._next_index) + 1

        return ret_val

    # *** PUBLIC METHODS ***

    def ToRow(self, schema:FeatureTableSchema) -> ExportRow:
        ret_val : List = [None]*len(schema.Columns)

        all_maps : List[Dict[int, Any]] = [
            schema.ColumnValueToRow(
                raw_value=self.Name,          mapping=schema.Map.FeatureNameColumn, concatenator=".", element_name="feature_name"
            ),
            schema.ColumnValueToRow(
                raw_value=self.Name,          mapping=schema.Map.FeatureTypeColumn, concatenator=".", element_name="feature_type"
            ),
            schema.ColumnValueToRow(
                raw_value=self.FeatureType,   mapping=schema.Map.GameUnitColumn,     concatenator=".", element_name="game_unit"
            ),
            schema.ColumnValueToRow(
                raw_value=self.GameUnit,      mapping=schema.Map.GameUnitIndexColumn, concatenator=".", element_name="game_unit_index"
            ),
            schema.ColumnValueToRow(
                raw_value=self.GameUnitIndex, mapping=schema.Map.AppIDColumn, concatenator=".", element_name="app_id"
            ),
            schema.ColumnValueToRow(
                raw_value=self.AppID,         mapping=schema.Map.UserIDColumn, concatenator=".", element_name="user_id"
            ),
            schema.ColumnValueToRow(
                raw_value=self.UserID,        mapping=schema.Map.SessionIDColumn, concatenator=".", element_name="session_id"
            ),
            schema.ColumnValueToRow(
                raw_value=self.SessionID,     mapping=schema.Map.SubfeaturesColumn, concatenator=", ", element_name="subfeatures"
            ),
            schema.ColumnValueToRow(
                raw_value=self.Subfeatures,   mapping=schema.Map.ValuesColumn, concatenator=", ", element_name="values"
            )
        ]

        for mapping in all_maps:
            for idx, val in mapping.items():
                ret_val[idx] = val
            
        return tuple(ret_val)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

