# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:22:31 2025

@author: Jablonski
"""
from __future__ import annotations
from attrs import field
from pytoolconfig import dataclass

import pandas as pd
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum
import io

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.core.wrapper import SIR3S_Model

class Dataframes_SIR3S_Model(SIR3S_Model):
    """
    This class is supposed to extend the general SIR3S_Model class with the possibility of using pandas dataframes when working with SIR 3S. Getting dataframes, inserting elements via dataframes, running algorithms on dataframes should be made possible.
    """

    @dataclass
    class DataFrames:
        df_node: pd.DataFrame = field(default_factory=pd.DataFrame)
        df_pipe: pd.DataFrame = field(default_factory=pd.DataFrame)

    def __init__(self):
        super().__init__()
        self.data_frames = self.DataFrames()

    def generate_dataframes(self):
        """
        Manually generate and populate all relevant dataframes.

        Inlcude optional param with ElemenTypes to only create certain dataframes
        """
        if not self.__is_a_model_open():
            logger.warning("No model is open. Cannot generate dataframes.")
            return

        logger.info("Generating dataframes...")
        
        logger.info("Generating df_node...")
        _metadata_props=self.GetPropertiesofElementType(self.ObjectTypes.Node)
        _result_props=self.GetResultProperties_from_elementType(self.ObjectTypes.Node, onlySelectedVectors=True)
        self.data_frames.df_node = self.generate_element_dataframe(metadata_props=_metadata_props, result_props=_result_props, element_type=self.ObjectTypes.Node)
        logger.info("df_node generated")
    
        logger.info("Generating df_pipe...")
        _metadata_props=self.GetPropertiesofElementType(self.ObjectTypes.Pipe)
        _result_props=self.GetResultProperties_from_elementType(self.ObjectTypes.Pipe, onlySelectedVectors=True)
        self.data_frames.df_pipe = self.generate_element_dataframe(metadata_props=_metadata_props, result_props=_result_props, element_type=self.ObjectTypes.Pipe)
        logger.info("df_pipe generated")

        logger.info("Dataframes generated.")

    def _resolve_given_timestamps(self, timestamps: Optional[List[str]]) -> List[str]:
        """
        Resolve the list of timestamps to use:
        - If `timestamps` is None: use all simulation timestamps (if available) else STAT.
        - Validate against available timestamps and filter out invalid ones.

        Returns
        -------
        List[str]
            A list of valid timestamps (possibly empty).
        """
        # --- Default timestamp resolution ---
        if timestamps is None:
            logger.info("[Resolving Timestamps] No timestamps were given. Checking available simulation timestamps (SIR3S_Model.GetTimeStamps()).")
            try:
                simulation_timestamps, tsStat, tsMin, tsMax = self.GetTimeStamps()
                if simulation_timestamps:
                    timestamps = simulation_timestamps
                    logger.info(f"{len(timestamps)} simulation timestamps will be used.")
                elif tsStat:
                    timestamps = [tsStat]
                    logger.info(f"[Resolving Timestamps] No simulation timestamps found. Using stationary timestamp (STAT): {tsStat}")
                else:
                    logger.warning("[Resolving Timestamps] No valid timestamps found. Proceeding with empty timestamp list.")
                    return []
            except Exception as e:
                logger.error(f"[Resolving Timestamps] Error retrieving timestamps: {e}")
                return []

        # --- Validate given timestamps ---
        try:
            all_timestamps, tsStat, tsMin, tsMax = self.GetTimeStamps()
            available_timestamps = list(all_timestamps) if all_timestamps else []
            if tsStat and tsStat not in available_timestamps:
                available_timestamps.append(tsStat)

            valid_timestamps = []
            for ts in timestamps:
                if ts in available_timestamps:
                    valid_timestamps.append(ts)
                else:
                    logger.warning(
                        f"[Resolving Timestamps] Timestamp {ts} is not valid (SIR3S_Model.GetTimeStamps()). It will be excluded."
                    )
            
            if len(valid_timestamps) == 1 and tsStat == valid_timestamps[0]:
                logger.info(f"[Resolving Timestamps] Only static timestamp {tsStat} is available")
            else:
                logger.info(f"[Resolving Timestamps] {len(valid_timestamps)} valid timestamps will be used.")
            return valid_timestamps
        except Exception as e:
            logger.error(f"Error validating timestamps: {e}")
            return []

    def __resolve_given_metadata_properties(
        self,
        element_type: Union[str, "Enum"],
        properties: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Checks the validity of given list of metadata properties. 
        If properties=None => All available properties will be used
        If properties=[] => No properties will be used
        """

        try:
            available_metadata_props = self.GetPropertiesofElementType(ElementType=element_type)
            available_result_props = self.GetResultProperties_from_elementType(
                elementType=element_type,
                onlySelectedVectors=False
            )

            metadata_props: List[str] = []

            if properties is None:
                logger.info(f"[Resolving Metadata Properties] No properties given → using ALL metadata properties for {element_type}.")
                metadata_props = available_metadata_props
            else:
                for prop in properties:
                    if prop in available_metadata_props:
                        metadata_props.append(prop)
                    elif prop in available_result_props:
                        logger.warning(f"[Resolving Metadata Properties] Property '{prop}' is a RESULT property; excluded from metadata.")
                    else:
                        logger.warning(
                            f"[Resolving Metadata Properties] Property '{prop}' not found in metadata or result properties of type {element_type}. Excluding."
                        )

            logger.debug(f"[Resolving Metadata Properties] Using {len(metadata_props)} metadata properties.")
       
        except Exception as e:
            logger.error(f"[Resolving Metadata Properties] Error resolving metadata properties: {e}")
        
        return metadata_props

    def __is_get_endnodes_applicable(self, tk):
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer  # Redirect stdout

        try:
            _ = self.GetEndNodes(tk)
        except Exception:
            sys.stdout = sys_stdout  # Restore stdout
            return False

        sys.stdout = sys_stdout  # Restore stdout
        output = buffer.getvalue()
        buffer.close()

        if "doesnt apply to such Type of Elements" in output:
            return False
        
        return True

    def generate_element_metadata_dataframe(
        self,
        element_type: Union[str, "Enum"],
        properties: Optional[List[str]] = None,
        geometry: Optional[bool] = False,
        end_nodes: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        Generate a dataframe with metadata (static) properties for all devices of a given element type.

        Parameters
        ----------
        element_type : Enum or str
            The element type (e.g., self.ObjectTypes.Node).
        properties : list[str], optional
            If properties=None => All available properties will be used
            If properties=[] => No properties will be used
        geometry : bool, optional
            If True, includes geometric information for each element in the dataframe. Note that this is still a regular DataFrame no GeoDataFrame, to convert it you need a crs values.
            Adds a 'geometry' column containing spatial data (WKT represenation eg. POINT (x y))
            Default is False.
        end_nodes : bool, optional
            If True and supported by the element type, includes tks of end nodes as cols (fkKI, fkKK, fkKI2, fkKK2) in the dataframe.
            Default is False.


        Returns
        -------
        pd.DataFrame
            Dataframe with one row per device (tk) and columns for requested metadata properties, geometry and end nodes.
            Columns: ["tk", <metadata_props>]
        """
        logger.info(f"[metadata] Generating metadata dataframe for element type: {element_type}")

        # --- Collect device keys (tks) ---
        try:
            tks = self.GetTksofElementType(ElementType=element_type)
            logger.info(f"[metadata] Retrieved {len(tks)} element(s) of element type {element_type}.")
        except Exception as e:
            logger.error(f"[metadata] Error retrieving element tks: {e}")
            return pd.DataFrame()

        # --- Resolve given metadata properties ---
        metadata_props = self.__resolve_given_metadata_properties(element_type=element_type, properties=properties)

        # --- Retrieve values ---
        to_retrieve = []
        if metadata_props != []:
            to_retrieve.append(f"metadata properties {metadata_props}")
        if geometry:
            to_retrieve.append("geometry")
        if end_nodes:
            to_retrieve.append("end nodes")
            
        logger.info(f"[metadata] Retrieving {', '.join(to_retrieve)}...")
        
        rows = []

        end_nodes_available = False
        if end_nodes:
            if self.__is_get_endnodes_applicable(tks[0]):
                end_nodes_available = True
            else:
                logger.warning(f"[metadata] End nodes are not defined for element type {element_type}. Dataframe is created without end nodes.")
        
        for tk in tks:
            
            row = {"tk": tk}
            
            # Add metadata properties
            for prop in metadata_props:
                try:
                    row[prop] = self.GetValue(Tk=tk, propertyName=prop)[0]
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get property '{prop}' for tk '{tk}': {e}")
            
            # Add geometry if requested
            if geometry:
                try:
                    row["geometry"] = self.GetGeometryInformation(Tk=tk)
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get geometry information for tk '{tk}': {e}")
            
            # Add end nodes if requested
            if end_nodes_available:
                try:
                    endnode_tuple = self.GetEndNodes(Tk=tk) 
                    row["fkKI"], row["fkKK"], row["fkKI2"], row["fkKK2"] = endnode_tuple
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get end nodes for tk '{tk}': {e}")

            rows.append(row)

        # --- Post-processing ---
        endnode_cols = ["fkKI", "fkKK", "fkKI2", "fkKK2"]
        used_cols = []

        for col in endnode_cols:
            if any(row.get(col, "-1") != "-1" for row in rows):
                used_cols.append(col)
            else:
                for row in rows:
                    row.pop(col, None)

        logger.info(f"[metadata] {len(used_cols)} non-empty end node columns were created)")

        df = pd.DataFrame(rows)
        logger.info(f"[metadata] Done. Shape: {df.shape}")
        return df

    def generate_element_results_dataframe(
        self,
        element_type: Union[str, "Enum"],
        properties: Optional[List[str]] = None,
        timestamps: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Generate a dataframe with RESULT (time-dependent) properties for all devices and timestamps.

        Parameters
        ----------
        element_type : Enum or str
            The element type (e.g., self.ObjectTypes.Node).
        properties : list[str], optional
            List of RESULT property names (vectors) to include. If None, includes ALL available result properties.
        timestamps : list[str], optional
            List of timestamps to include. If None, uses all simulation timestamps (or STAT if no sims).

        Returns
        -------
        pd.DataFrame
            Dataframe with one row per (timestamp, tk) and columns for requested result properties.
            Columns: ["timestamp", "tk", <result_props>]
        """
        logger.info(f"[results] Generating results dataframe for element type: {element_type}")

        # --- Resolve timestamps (all devices × timestamps) ---
        valid_timestamps = self._resolve_given_timestamps(timestamps)
        if not valid_timestamps:
            logger.warning("[results] No valid timestamps. Returning empty dataframe.")
            return pd.DataFrame(columns=["timestamp", "tk"])

        # --- Collect device keys (tks) ---
        try:
            tks = self.GetTksofElementType(ElementType=element_type)
            logger.info(f"[results] Retrieved {len(tks)} tks.")
        except Exception as e:
            logger.error(f"[results] Error retrieving tks: {e}")
            return pd.DataFrame(columns=["timestamp", "tk"])

        # --- Determine result properties ---
        try:
            available_metadata_props = self.GetPropertiesofElementType(ElementType=element_type)
            available_result_props = self.GetResultProperties_from_elementType(
                elementType=element_type,
                onlySelectedVectors=False
            )

            result_props: List[str] = []

            if properties is None:
                logger.info(f"[results] No properties given → using ALL result properties for {element_type}.")
                result_props = available_result_props
            else:
                for prop in properties:
                    if prop in available_result_props:
                        result_props.append(prop)
                    elif prop in available_metadata_props:
                        logger.warning(f"[results] Property '{prop}' is a METADATA property; excluded from results.")
                    else:
                        logger.warning(
                            f"[results] Property '{prop}' not found in metadata or result properties of type {element_type}. Excluding."
                        )

            logger.info(f"[results] Using {len(result_props)} result properties.")
        except Exception as e:
            logger.error(f"[results] Error determining result properties: {e}")
            return pd.DataFrame(columns=["timestamp", "tk"])

        # --- Retrieve result values ---
        logger.info("[results] Retrieving result properties...")
        data_rows = []
        for ts in map(str, valid_timestamps):
            for tk in tks:
                row = {"timestamp": ts, "tk": tk}
                for prop in result_props:
                    try:
                        row[prop] = self.GetResultfortimestamp(timestamp=ts, Tk=tk, property=prop)[0]
                    except Exception as e:
                        logger.warning(f"[results] Failed to get result '{prop}' for tk '{tk}' at '{ts}': {e}")
                data_rows.append(row)

        df = pd.DataFrame(data_rows)
        logger.info(f"[results] Done. Shape: {df.shape}")
        return df

    def apply_metadata_property_updates(
        self,
        element_type: Union[str, Enum],
        updates_df: pd.DataFrame,
        properties_new: Optional[List[str]] = None,
        tag: Optional[str] = "_new",
    ) -> pd.DataFrame:
        """
        Apply metadata updates for a single property using a DataFrame with keys and new values.

        Expects:
        - One key column (default: 'tk'), and
        - Exactly one column named '<metadata_property>_new' (or pass `property_name` to target one explicitly).

        Parameters
        ----------
        element_type : Union[str, Enum]
            The element type to update (e.g., self.ObjectTypes.Pipe).
        updates_df : pd.DataFrame
            Input with at least:
            - key column (default 'tk'), and
            - one '<property>_new' column (e.g., 'diameter_mm_new').
        property_name : Optional[str], default None
            If given, we will look for the column f"{property_name}_new".
            If None, we auto-detect a single '*_new' column.
        on : str, default 'tk'
            Name of the key column in `updates_df`. If it's the index, it will be reset.
        create_missing : bool, default False
            If True, allow creating metadata rows that don't exist yet (your set-logic decides how).
        dry_run : bool, default False
            If True, do NOT apply; just return a normalized summary of what would be changed.
        allow_na : bool, default True
            If False, rows with NaN in the '<property>_new' column will be dropped (skipped).

        Returns
        -------
        pd.DataFrame
            A summary dataframe with columns:
            ['tk', 'property', 'new_value'] (+ 'status' when dry_run)
            representing the intended updates.
        """
        logger.info(f"[update] Applying metadata updates for element type: {element_type}")

        if updates_df is None or updates_df.empty:
            logger.warning("[update] Empty updates_df provided. Nothing to do.")
            return pd.DataFrame(columns=["tk", "property", "new_value"])

        df = updates_df.copy()

        # --- Ensure key ('tk') column is present ---
        if tk not in df.columns:
            if df.index.name == tk:
                df = df.reset_index()
                logger.info(f"[update] Using index as column.")
            else:
                msg = f"[update] tk not found in updates_df (nor as index)."
                logger.error(msg)
                raise KeyError(msg)

        # --- Resolve & Validate given properties_new ---
        logger.info("[update] Resolving & validating given properties_new...")
        properties_new_in_index=df.columns.intersection(properties_new).tolist()
        logger.info(f"[update] In updates_df found: {properties_new_in_index}")
        properties_new_stripped = [p.removesuffix(tag) for p in properties_new]
        metadata_props_new=self.__resolve_given_metadata_properties(element_type=element_type, properties=properties_new_stripped)
        metadata_props_new_with_suffix = [p + tag for p in metadata_props_new]
        logger.info("[update] Resolved & validated given properties_new")

        # TODO
        # --- Set metadata values in model ---
        for tk in self.GetTksofElementType(ElementType=element_type):
            for prop in metadata_props_new:
                msg=self.SetValue(prop, updates_df.iloc[tk, metadata_props_new_with_suffix])
                logger.debug

    def __is_a_model_open(self):
        """
        Returns true if a model is open, false if no model is open or the NetworkType is undefined.
        """
        is_a_model_open = True
        if(self.GetNetworkType=="NetworkType.Undefined"):
            is_a_model_open = False
        return is_a_model_open