"""DataOuterface Module
"""
## import standard libraries
import abc
import logging
import sys
from typing import List, Optional, Set

# import local files
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.EventSet import EventSet
from ogd.common.models.Feature import Feature
from ogd.common.models.FeatureSet import FeatureSet
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.typing import ExportRow
from ogd.common.utils.Logger import Logger

class Outerface:
    """Base class for feature and event output.

    :param Interface: _description_
    :type Interface: _type_
    :return: _description_
    :rtype: _type_
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Connector(self) -> StorageConnector:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # @abc.abstractmethod
    # def _destination(self, mode:ExportMode) -> str:
        # raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Location function!")

    @abc.abstractmethod
    def _removeExportMode(self, mode:ExportMode) -> str:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")


    @abc.abstractmethod
    def _setupGameEventsTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _setupDetectorEventsTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _setupAllFeaturesTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _setupSessionTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _setupPlayerTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _setupPopulationTable(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeAllFeatureLines(self, feature_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeSessionLines(self, session_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePlayerLines(self, player_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePopulationLines(self, population_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode]):
        self._config  : DataTableConfig = table_config
        self._modes   : Set[ExportMode] = export_modes

    @property
    def Config(self) -> DataTableConfig:
        return self._config

    @property
    def ExportModes(self) -> Set[ExportMode]:
        return self._modes

    @property
    def SessionCount(self) -> int:
        return self._session_ct
    @SessionCount.setter
    def SessionCount(self, new_val) -> None:
        self._session_ct = new_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # def Destination(self, mode:ExportMode):
    #     return self._destination(mode=mode)

    def RemoveExportMode(self, mode:ExportMode):
        self._removeExportMode(mode)
        self._modes.discard(mode)
        Logger.Log(f"Removed mode {mode} from {type(self).__name__} output.", logging.INFO)

    def WriteHeader(self, mode:ExportMode, header:Optional[List[str]]=None):
        """Write the header to the table for a given export type.

        If the table does not exist, the outerface will attempt to create it.

        .. TODO : Sort out a better way to make sure the header and output format are the same,
        i.e. if write calls are going to specify pivot format, we should allow that to be specified when calling here,
        rather than needing to get the pivot format header and pass in, then later just say "as_pivot=True" when sending in data.
        Solution might be to put this responsibility on the FeatureSet as well, since it's in a better spot to say what's what.

        :param mode: _description_
        :type mode: ExportMode
        :param header: _description_, defaults to None
        :type header: Optional[List[str]], optional
        """
        if mode in self.ExportModes:
            match (mode):
                case ExportMode.EVENTS:
                    self._setupGameEventsTable(header=header or [])
                    Logger.Log(f"Wrote event header for {self.Config.Location} events", depth=3)
                case ExportMode.DETECTORS:
                    self._setupDetectorEventsTable(header=header or [])
                    Logger.Log(f"Wrote processed event header for {self.Config.Location} events", depth=3)
                case ExportMode.FEATURES:
                    self._setupAllFeaturesTable(header=Feature.ColumnNames())
                    Logger.Log(f"Wrote all-features header for {self.Config.Location} features", depth=3)
                case ExportMode.SESSION:
                    self._setupSessionTable(header=header or [])
                    Logger.Log(f"Wrote session feature header for {self.Config.Location} sessions", depth=3)
                case ExportMode.PLAYER:
                    self._setupPlayerTable(header=header or [])
                    Logger.Log(f"Wrote player feature header for {self.Config.Location} players", depth=3)
                case ExportMode.POPULATION:
                    self._setupPopulationTable(header=header or [])
                    Logger.Log(f"Wrote population feature header for {self.Config.Location} populations", depth=3)
                case _:
                    Logger.Log(f"Failed to write header for unrecognized export mode {mode}!", level=logging.WARN, depth=3)
        else:
            Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)

    def WriteEvents(self, events:EventSet, mode:ExportMode) -> None:
        if isinstance(self.Config.TableSchema, EventTableSchema):
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.EVENTS:
                        lines = events.GameEventLines(schema=self.Config.TableSchema)
                        self._writeGameEventLines(events=lines)
                        Logger.Log(f"Wrote {len(lines)} {self.Config.Location} events", depth=3)
                    case ExportMode.DETECTORS:
                        lines = events.EventLines(schema=self.Config.TableSchema)
                        self._writeAllEventLines(events=lines)
                        Logger.Log(f"Wrote {len(events)} {self.Config.Location} processed events", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Event export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write events from {type(self).__name__}, outerface was not configured for a Events table!", logging.WARNING, depth=3)

    def WriteFeatures(self, features:FeatureSet, mode:ExportMode, as_pivot:bool=False) -> None:
        if isinstance(self.Config.TableSchema, FeatureTableSchema):
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.SESSION:
                        lines = features.SessionLines(schema=self.Config.TableSchema, as_pivot=True)
                        self._writeAllFeatureLines(feature_lines=lines)
                        self._writeSessionLines(
                            session_lines = lines if as_pivot else features.SessionLines(schema=self.Config.TableSchema, as_pivot=False)
                        )
                        Logger.Log(f"Wrote {len(lines)} {self.Config.Location} session lines", depth=3)
                    case ExportMode.PLAYER:
                        lines = features.PlayerLines(schema=self.Config.TableSchema, as_pivot=True)
                        self._writeAllFeatureLines(feature_lines=lines)
                        self._writePlayerLines(
                            player_lines = lines if as_pivot else features.PlayerLines(schema=self.Config.TableSchema, as_pivot=False)
                        )
                        Logger.Log(f"Wrote {len(lines)} {self.Config.Location} player lines", depth=3)
                    case ExportMode.POPULATION:
                        lines = features.PopulationLines(schema=self.Config.TableSchema, as_pivot=True)
                        self._writeAllFeatureLines(feature_lines=lines)
                        self._writePopulationLines(
                            population_lines = lines if as_pivot else features.PopulationLines(schema=self.Config.TableSchema, as_pivot=False)
                        )
                        Logger.Log(f"Wrote {len(lines)} {self.Config.Location} population lines", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Feature export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write features from {type(self).__name__}, outerface was not configured for a Features table!", logging.WARNING, depth=3)

    def WriteMetadata(self, dataset_schema:DatasetSchema):
        
        self._writeMetadata(dataset_schema=dataset_schema)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
