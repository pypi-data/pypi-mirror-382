# standard imports
import builtins
import json
import logging
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import chain
from typing import Dict, Final, List, LiteralString, Optional, Tuple, Type, override, Sequence
# 3rd-party imports
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
# OGD imports
from ogd.common.filters import *
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

type BigQueryParameter = bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter | bigquery.RangeQueryParameter
@dataclass
class ParamaterizedClause:
    clause: LiteralString = ""
    params: Sequence[BigQueryParameter] = field(default_factory=lambda:[])

class BigQueryInterface(Interface):
    """Implementation of Interface functions for BigQuery.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, store:Optional[BigQueryConnector]=None):
        self._store : BigQueryConnector

        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, BigQueryConfig):
            self._store = BigQueryConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"BigQueryInterface config was for a connector other than BigQuery! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    @property
    def DBPath(self) -> str:
        """The path of form "[projectID].[datasetID].[tableName]" used to make queries

        TODO : do something more... clever than directly using configured values. That's how it's been so far, and that's fine,
        but wouldn't want any clever inputs here.

        :return: The full path from project ID to table name, if properly set in configuration, else the literal string "INVALID SOURCE SCHEMA".
        :rtype: str
        """
        return f"{self.Connector.StoreConfig.Location.DatabaseName}.{self.Config.Location.Location}_*"


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> BigQueryConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        """
        .. TODO : take other filters into account
        """
        ret_val = []

        if self.Connector.Client:
            # 1. Create query & config
            id_col : LiteralString       = "session_id" if mode==IDMode.SESSION else "user_id"
            suffix_clause : LiteralString = ""
            if filters.Sequences.Timestamps.Active and isinstance(filters.Sequences.Timestamps, RangeFilter):
                suffix : ParamaterizedClause = self._generateSuffixClause(date_filter=filters.Sequences.Timestamps)
                suffix_clause = f"WHERE {suffix.clause}" if suffix.clause is not None else ""
            query = f"""\
                SELECT DISTINCT {id_col}
                FROM `{self.DBPath}`
                {suffix_clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=suffix.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for all {mode} ids:\n{query}", logging.DEBUG, depth=3, whitespace_adjust="lstrip")
            try:
                job = self.Connector.Client.query(query, cfg)
                data = job.result()
            except BadRequest as err:
                Logger.Log(f"In _availableIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[id_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {}

        if self.Connector.Client:
            # 1. Create query & config
            where_clause = self._generateWhereClause(filters=filters)
            query = textwrap.dedent(f"""\
                SELECT MIN(client_time), MAX(client_time)
                FROM `{self.DBPath}`
                {where_clause.clause}
            """)
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for full date range:\n{query}", logging.DEBUG, depth=3, whitespace_adjust="lstrip")
            try:
                job = self.Connector.Client.query(query, job_config=cfg)
                data = list(job.result())
                Logger.Log(f"...Query yielded results:\n{data}", logging.DEBUG, depth=3)
            except BadRequest as err:
                Logger.Log(f"In _availableDates, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                if len(data) == 1:
                    dates = data[0]
                    if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
                        _min = dates[0] if isinstance(dates[0], datetime) else datetime.strptime(str(dates[0]), "%m-%d-%Y %H:%M:%S")
                        _max = dates[1] if isinstance(dates[1], datetime) else datetime.strptime(str(dates[1]), "%m-%d-%Y %H:%M:%S")
                        ret_val = {'min':_min, 'max':_max}
                    else:
                        Logger.Log("BigQueryInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
                        ret_val = {'min':datetime.now(), 'max':datetime.now()}
                else:
                    Logger.Log("BigQueryInterface query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
                    ret_val = {'min':datetime.now(), 'max':datetime.now()}
        else:
            Logger.Log(f"Can't retrieve available dates from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.Client:
            # 1. Create query & config
            version_col  : LiteralString       = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"
            where_clause : ParamaterizedClause = self._generateWhereClause(filters=filters)
            query = textwrap.dedent(f"""\
                SELECT DISTINCT {version_col}
                FROM `{self.DBPath}`
                {where_clause.clause}
            """)
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for distinct {mode} versions:\n{query}", logging.DEBUG, depth=3, whitespace_adjust="lstrip")
            try:
                job = self.Connector.Client.query(query, job_config=cfg)
                data = job.result()
            except BadRequest as err:
                Logger.Log(f"In _availableVersions, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[version_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} versions. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} versions from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        ret_val = []

        if self.Connector.Client:
            # 1. Create query & config
            where_clause : ParamaterizedClause = self._generateWhereClause(filters=filters)
            # TODO Order by user_id, and by timestamp within that.
            # Note that this could prove to be wonky when we have more games without user ids,
            # will need to really rethink this when we start using new system.
            # Still, not a huge deal because most of these will be rewritten at that time anyway.
            query = textwrap.dedent(f"""\
                SELECT *
                FROM `{self.DBPath}`
                {where_clause.clause}
                ORDER BY `user_id`, `session_id`, `event_sequence_index` ASC
            """)
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for rows from IDs:\n{query}\nWith Params:\n{where_clause.params}", logging.DEBUG, depth=3, whitespace_adjust="lstrip")
            try:
                job = self.Connector.Client.query(query, job_config=cfg)
                data = job.result()
            except BadRequest as err:
                Logger.Log(f"In _rowsFromIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            except Exception as err:
                Logger.Log(f"Unexpected error in BigQuery of type {type(err)} occurred: {err}", logging.ERROR)
            else:
                Logger.Log(f"...Query yielded results, with query in state: {job.state}", logging.DEBUG, depth=3)
                for row in data:
                    items = tuple(row.items())
                    event = []
                    for item in items:
                        match item[0]:
                            case "event_params":
                                _params = {param['key']:param['value'] for param in item[1]}
                                event.append(json.dumps(_params, sort_keys=True))
                            case "device":
                                event.append(json.dumps(item[1], sort_keys=True))
                            case _:
                                event.append(item[1])
                    ret_val.append(tuple(event))
        else:
            Logger.Log(f"Can't retrieve collection of events from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)

        return ret_val

    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        return []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateSuffixClause(date_filter:RangeFilter[datetime], extra_bound:int=0) -> ParamaterizedClause:
        """Function to generate a BigQuery clause representing a bound on table suffixes.

        In particular, it takes a date filter, and returns a parameterized clause of the form:  
        ```
        _TABLE_SUFFIX BETWEEN @suffixstart AND @suffixend
        ```
        where the `@suffixstart` and `@suffixend` have form YYYYMMDD.

        The `extra_bound` parameter has the function expand the bounds by the given integer value in either direction.
        For example, if the filter specified a range between January 2nd and 3rd,
        an `extra_bound` of 1 would set the returned clause to be between January 1st and 4th.

        :param date_filter: Filter specifying the range of dates for the suffix to take
        :type date_filter: RangeFilter[datetime]
        :param extra_bound: Optional integer to expand the suffix range beyond the range specified by the filter. The value is treated as the number of **days** by which to expand the suffix. Defaults to 0
        :type extra_bound: int, optional
        :return: _description_
        :rtype: ParamaterizedClause
        """
        clause = ""
        params = []

        if date_filter.Min and date_filter.Max:
            _min = date_filter.Min.date() - timedelta(days=extra_bound)
            _max = date_filter.Max.date() + timedelta(days=extra_bound)
            str_min, str_max = _min.strftime("%Y%m%d"), _max.strftime("%Y%m%d")
            clause = "_TABLE_SUFFIX BETWEEN @suffixstart AND @suffixend"
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_min, name="suffixstart")
            )
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_max, name="suffixend")
            )

        return ParamaterizedClause(clause=clause, params=params)


    @staticmethod
    def _generateWhereClause(filters:DatasetFilterCollection) -> ParamaterizedClause:
        sess_clause = BigQueryInterface._setFilterClause(
            filt=filters.IDFilters.Sessions,
            column_name="session_id",
            column_type=str
        )

        users_clause = BigQueryInterface._setFilterClause(
            filt=filters.IDFilters.Players,
            column_name="user_id",
            column_type=str
        )

        times_clause = BigQueryInterface._timerangeFilterClause(
            filt=filters.Sequences.Timestamps,
            column_name="client_time"
        )

        indices_clause : ParamaterizedClause = ParamaterizedClause()
        if isinstance(filters.Sequences.SessionIndices, SetFilter):
            indices_clause = BigQueryInterface._setFilterClause(
                filt=filters.Sequences.SessionIndices,
                column_name="event_session_index",
                column_type=int
            )
        elif isinstance(filters.Sequences.SessionIndices, RangeFilter):
            indices_clause = BigQueryInterface._rangeFilterClause(
                filt=filters.Sequences.SessionIndices,
                column_name="event_session_index",
                column_type=int
            )

        log_clause : ParamaterizedClause = ParamaterizedClause()
        if filters.Versions.LogVersions.Active:
            if isinstance(filters.Versions.LogVersions, SetFilter):
                log_clause = BigQueryInterface._setFilterClause(
                    filt=filters.Versions.LogVersions,
                    column_name="log_version",
                    column_type=str
                )
            elif isinstance(filters.Versions.LogVersions, RangeFilter):
                log_clause = BigQueryInterface._rangeFilterClause(
                    filt=filters.Versions.LogVersions,
                    column_name="log_version",
                    column_type=str
                )

        app_clause : ParamaterizedClause = ParamaterizedClause()
        if filters.Versions.AppVersions.Active:
            if isinstance(filters.Versions.AppVersions, SetFilter):
                app_clause = BigQueryInterface._setFilterClause(
                    filt=filters.Versions.AppVersions,
                    column_name="app_version",
                    column_type=str
                )
            elif isinstance(filters.Versions.AppVersions, RangeFilter):
                app_clause = BigQueryInterface._rangeFilterClause(
                    filt=filters.Versions.AppVersions,
                    column_name="app_version",
                    column_type=str
                )

        branch_clause : ParamaterizedClause = ParamaterizedClause()
        if filters.Versions.AppBranches.Active:
            if isinstance(filters.Versions.AppBranches, SetFilter):
                branch_clause = BigQueryInterface._setFilterClause(
                    filt=filters.Versions.AppBranches,
                    column_name="app_branch",
                    column_type=str
                )
            elif isinstance(filters.Versions.AppBranches, RangeFilter):
                branch_clause = BigQueryInterface._rangeFilterClause(
                    filt=filters.Versions.AppBranches,
                    column_name="app_branch",
                    column_type=str
                )

        events_clause : ParamaterizedClause = ParamaterizedClause()
        if filters.Events.EventNames.Active:
            events_clause = BigQueryInterface._setFilterClause(
                filt=filters.Events.EventNames,
                column_name="event_name",
                column_type=str
            )

        # codes_clause : Optional[LiteralString] = None
        # codes_param  : Sequence[BigQueryParameter] = []
        # if filters.Events.EventCodes.Active:
        #     if isinstance(filters.Versions.AppBranches, SetFilter):
        #         codes_clause, codes_param = BigQueryInterface._setFilterClause(
        #             filt=filters.Events.EventCodes,
        #             column_name="event_code",
        #             column_type=int
        #         )
        #     elif isinstance(filters.Versions.AppBranches, RangeFilter):
        #         codes_clause, codes_param = BigQueryInterface._rangeFilterClause(
        #             filt=filters.Events.EventCodes,
        #             column_name="event_code",
        #             column_type=int
        #         )

        all_clauses     : List[ParamaterizedClause] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause]
        
        # get the actual clause strings
        clause_list     : List[LiteralString]       = [clause.clause for clause in all_clauses if clause.clause is not None and clause.clause != ""]
        where_clause    : LiteralString             = f"WHERE {'\nAND '.join(clause_list)}" if len(clause_list) > 0 else ""

        # get the params
        params_collection = [clause.params for clause in all_clauses]
        params = list(chain.from_iterable(params_collection))

        return ParamaterizedClause(clause=where_clause, params=params)

    @staticmethod
    def _setFilterClause(filt:SetFilter | NoFilter, column_name:LiteralString, column_type:Type) -> ParamaterizedClause:
        ret_val : ParamaterizedClause = ParamaterizedClause("", [])

        if filt.Active:
            elems : List = filt.AsList or []
            if len(elems) > 0:
                exclude    : LiteralString = "NOT" if filt.FilterMode == FilterMode.EXCLUDE else ""
                param_name : LiteralString = f"{column_name}_list"
                clause     : LiteralString = f"`{column_name}` {exclude} IN UNNEST(@{param_name})"
                array_type : str = "INT64" if column_type in {"int", builtins.int} else "STRING" if column_type in {"str", builtins.str} else "STRING"
                match column_type:
                    case builtins.int:
                        array_type = "INT64"
                    case builtins.str:
                        array_type = "STRING"
                    case _:
                        Logger.Log(f"When generating filter clause, column_type was given as {column_type}, which is not currently supported by the BigQueryInterface as an input type for BigQuery parameters. Using str instead.", logging.DEBUG)
                        column_type = str
                        array_type = "STRING"
                params     : List[bigquery.ArrayQueryParameter] = [
                    bigquery.ArrayQueryParameter(name=param_name, array_type=array_type, values=[column_type(elem) for elem in elems])
                ]
                ret_val = ParamaterizedClause(clause, params)

        return ret_val
    
    @staticmethod
    def _rangeFilterClause(filt:RangeFilter | NoFilter, column_name:LiteralString, column_type:Type) -> ParamaterizedClause:
        ret_val : ParamaterizedClause = ParamaterizedClause("", [])

        if filt.Active:
            exclude    : LiteralString
            param_name : LiteralString
            clause     : LiteralString
            param_type : str
            params     : List[bigquery.RangeQueryParameter | bigquery.ScalarQueryParameter]

            match column_type:
                case builtins.int:
                    param_type = "INT64"
                case builtins.str:
                    param_type = "STRING"
                case _:
                    Logger.Log(f"When generating filter clause, column_type was given as {column_type}, which is not currently supported by the BigQueryInterface as an input type for BigQuery parameters. Using str instead.", logging.DEBUG)
                    column_type = str
                    param_type = "STRING"
            # 1. If we have both min and max, use a range
            if filt.Min and filt.Max:
                exclude        = "NOT" if filt.FilterMode == FilterMode.EXCLUDE else ""
                param_name_min = f"{column_name}_min"
                param_name_max = f"{column_name}_max"
                clause = f"`{column_name}` {exclude} BETWEEN @{param_name_min} AND @{param_name_max}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name_min, type_=param_type, value=column_type(filt.Min)),
                    bigquery.ScalarQueryParameter(name=param_name_max, type_=param_type, value=column_type(filt.Max))
                ]
            elif filt.Min:
                exclude    = "<" if filt.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                param_name = f"{column_name}_min"
                clause     = f"`{column_name}` {exclude} @{param_name}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name, type_=param_type, value=column_type(filt.Min))
                ]
            elif filt.Max:
                exclude    = ">" if filt.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                param_name = f"{column_name}_max"
                clause     = f"`{column_name}` {exclude} @{param_name}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name, type_=param_type, value=column_type(filt.Max))
                ]
            else:
                Logger.Log(f"Tried to generate range clause from a range filter (on column {column_name}) that was somehow active with null max and min! This clause will be skipped!", logging.ERROR)
            ret_val = ParamaterizedClause(clause, params)

        return ret_val

    @staticmethod
    def _timerangeFilterClause(filt:RangeFilter[datetime] | NoFilter, column_name:LiteralString) -> ParamaterizedClause:
        ret_val : ParamaterizedClause = ParamaterizedClause("", ())

        if filt.Active:
            exclude    : LiteralString
            param_name : LiteralString
            clause     : LiteralString
            params     : List[bigquery.RangeQueryParameter | bigquery.ScalarQueryParameter]
            # 1. If we have both min and max, use a range
            if filt.Min and filt.Max:
                exclude        = "NOT" if filt.FilterMode == FilterMode.EXCLUDE else ""
                param_name_min = f"{column_name}_min"
                param_name_max = f"{column_name}_max"
                # param_name = f"{column_name}"
                clause         = f"`{column_name}` {exclude} BETWEEN @{param_name_min} AND @{param_name_max}"
                # clause         = f"`{column_name}` {exclude} BETWEEN @{param_name}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name_min, type_="TIMESTAMP", value=filt.Min),
                    bigquery.ScalarQueryParameter(name=param_name_max, type_="TIMESTAMP", value=filt.Max)
                    # bigquery.RangeQueryParameter(name=param_name, range_element_type="TIMESTAMP", start=filt.Min, end=filt.Max)
                ]
            elif filt.Min:
                exclude    = "<" if filt.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                param_name = f"{column_name}_min"
                clause     = f"`{column_name}` {exclude} @{param_name}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name, type_="TIMESTAMP", value=filt.Min)
                ]
            else: # filt.Max is not None
                exclude    = ">" if filt.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                param_name = f"{column_name}_max"
                clause     = f"`{column_name}` {exclude} @{param_name}"
                params = [
                    bigquery.ScalarQueryParameter(name=param_name, type_="TIMESTAMP", value=filt.Max)
                ]
            ret_val = ParamaterizedClause(clause, params)

        return ret_val

    # *** PRIVATE METHODS ***
