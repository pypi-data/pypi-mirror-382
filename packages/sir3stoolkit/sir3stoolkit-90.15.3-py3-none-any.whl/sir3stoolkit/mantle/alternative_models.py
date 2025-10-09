# -*- coding: utf-8 -*-
"""
Created on Weg Sep 01 14:04:43 2025

@author: Jablonski
"""

import pandapipes as pp
import pandas as pd
from shapely import wkt

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.mantle.dataframes import Dataframes_SIR3S_Model

class Alternative_Models_SIR3S_Model(Dataframes_SIR3S_Model):
    """
    This class is supposed to extend the Dataframes class that extends the general SIR3S_Model class with the possibility of using alternative District Heating models such as pandapipes.
    """
    def SIR_3S_to_pandapipes(self):
        """
        This function returns a pandapipes network that is a copy of the open SIR 3S network.
        """
        net = pp.create_empty_network(fluid="water")

        # --- Nodes/Junctions ---
        df_nodes_metadata = self.generate_element_metadata_dataframe(self.ObjectTypes.Node, ['Name', 'Zkor', 'QmEin', 'bz.PhEin', 'Ktyp'], geometry=True)
        df_nodes_results = self.generate_element_results_dataframe(self.ObjectTypes.Node, ['PH', 'T', 'QM'], self.GetTimeStamps()[0])
        df_nodes = pd.merge(df_nodes_metadata, df_nodes_results, on='tk', how='inner')

        js = {}

        for idx, row in df_nodes.iterrows():
            geom = wkt.loads(row["geometry"])
            x, y = geom.x, geom.y

            j = pp.create_junction(
                net,
                pn_bar=float(row['PH']),
                tfluid_k=273.15 + float(row['T']),
                height_m=float(row['Zkor']),
                name=f"{row['Name']}~{row['tk']}"
            )

            # Assign geodata to junction_geodata table
            net.junction_geodata.at[j, "x"] = x
            net.junction_geodata.at[j, "y"] = y

            js[row['tk']] = j

        # --- Pipes ---
        df_pipes_metadata = self.generate_element_metadata_dataframe(self.ObjectTypes.Pipe, ['L', 'Di', 'Rau', 'Name'], end_nodes=True, geometry=True)
        
        for idx,row in df_pipes_metadata.iterrows():
            raw_value = row["Rau"]
            row["Rau"] = float(str(raw_value).replace(",", "."))

        ps = {}

        for idx, row in df_pipes_metadata.iterrows():
            geom = wkt.loads(row["geometry"])  
            coords = list(geom.coords)        

            # Create pipe
            p = pp.create_pipe_from_parameters(
                net,
                from_junction=js[row['fkKI']],
                to_junction=js[row['fkKK']],
                length_km=float(row['L']) / 1000.,
                diameter_m=float(row['Di']) / 1000.,
                k_mm=float(row['Rau']),
                name=f"{row['Name']}~{row['tk']}"
            )
            ps[row['tk']] = p

            net.pipe_geodata.at[p, "coords"] = coords

        # --- Source/Sinks ---
        for idx, row in df_nodes.iterrows():
            ktyp = (row.get("Ktyp"))
            tk = row.get("tk")

            # Create source if Ktyp is PKON and PH > 0
            if ktyp == "PKON" and float(row.get("PH", 0)) > 0:
                pp.create_ext_grid(
                    net,
                    junction=js[tk],
                    p_bar=float(row["PH"]),
                    t_k=273.15 + float(row["T"]),
                    name=f"Src: {row['Name']}~{tk}"
                )

            # Create sink if Ktyp is QKON and QM < 0
            elif ktyp == "QKON" and float(row.get("QM", 0)) < 0:
                pp.create_sink(
                    net,
                    junction=js[tk],
                    mdot_kg_per_s=abs(float(row["QM"])),
                    name=f"Snk: {row['Name']}~{tk}"
                )

        return net