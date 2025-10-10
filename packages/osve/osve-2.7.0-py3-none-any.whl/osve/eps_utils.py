#*****************************************************************************#
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
#*****************************************************************************# 


"""
Created on June, 2025

@author: Ricardo Valles Blanco (ESAC)

This module contains some functions to handle EPS input or output files.


OSVE_OVERLAYS: Constant with predefined overlay sets for fast OSVE datapack creation
====================================================================================

All overlays are implemented as lists of overlay maps. This allows developers
to extend the current datapack fields list directly with one line of code.

Supported overlay sets: POWER, ATT_QUAT, BODY_RATE, WMM_WHL_TORQUE.

Example
-------

.. code-block:: python

    datapack = create_empty_datapack("blabla.csv", timeStep=10, precision=7)
    datapack["fields"].extend(OSVE_OVERLAYS["ATT_QUAT"])
    datapack["fields"].extend(OSVE_OVERLAYS["BODY_RATE"])
    datapack["fields"].extend(OSVE_OVERLAYS["WMM_WHL_TORQUE"])

    local_session_file_path = "ABSOLUTE PATH TO YOUR LOCAL OSVE SESSION FILE"
    session = load_session_file(local_session_file_path)
    session["sessionConfiguration"]["outputFiles"]["dataPacks"].append(datapack)
    save_session_file(local_session_file_path, session)

"""

import os
import numpy as np
from datetime import datetime

OSVE_OVERLAYS = {

   "POWER":            [{ "type": "MAPPS", "overlayId": "TOTAL_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_AVAIL_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_ANGLE" },
                        { "type": "MAPPS", "overlayId": "EPS_BATTERY_DOD" }],

   "ATT_QUAT":         [{ "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS1" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS2" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS3" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_VALUE" }],

    "BODY_RATE":       [{ "type": "MAPPS", "overlayId": "TOTAL_BODY_RATE" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_X" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_Y" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_Z" }],

    "WMM_WHL_TORQUE":  [{ "type": "MAPPS", "overlayId": "WMM_WHL_1_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_2_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_3_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_4_TORQUE" }],

    "WMM_GGT":         [{ "type": "MAPPS", "overlayId": "WMM_GGT_X" },
                        { "type": "MAPPS", "overlayId": "WMM_GGT_Y" },
                        { "type": "MAPPS", "overlayId": "WMM_GGT_Z" }]
}


# ==============================================================================
# ==============================================================================


def extract_files(file_path, basepath, is_recursive=False):
    """
    Returns a JSON with the whole files hierarchy including the ones
    referenced by "Include_file:" keyword in the EDFs or ITLs

    :param file_path: Path to EDF or ITL file.
    :type file_path: str
    :param basepath: Base path of the ITL or EDF file.
    :type basepath: str
    :param is_recursive: Flag to detect if comes from recursion or not. By default is False.
    :type is_recursive: bool
    :return: Returns a dict with a tree structure with the files hierarchy.
    :rtype: dict
    """
    file = open(file_path, "r")
    text = file.read()
    file.close()

    files = {}

    for line in text.splitlines():

        if line.startswith("#"):
            # Ignore comments
            continue

        tokens = line.split()

        if not len(tokens):
            # Ignore empty line
            continue
        

        if tokens[0] == "Include_file:":
            # Include_file: "JUICE/EDF_JUI_SPC_THERMAL.edf"

            incl_file_path = tokens[1].replace("\"", "")
            inc_files = extract_files(os.path.join(basepath, incl_file_path), basepath, is_recursive=True)
            files[os.path.join(basepath, incl_file_path)] = inc_files
    
    if not is_recursive:
        return {file_path: files}

    else:
        return files if len(files) else ""
    

def read_all_files(file_path, basepath):
    """
    Returns a string with the contents of all the files including the ones
    referenced by "Include_file:" keyword in the EDFs or ITLs

    :param file_path: Path to EDF or ITL file.
    :type file_path: str
    :param basepath: Base path of the ITL or EDF file.
    :type basepath: str
    :return: Returns a string with the appended contents of all referenced files.
    :rtype: dict
    """

    file = open(file_path, "r")
    text = file.read()
    file.close()

    all_text = ""

    for line in text.splitlines():
        
        all_text += line + "\r\n"

        if line.startswith("Include_file:") or line.startswith("Include:"):
            # Include_file: "JUICE/EDF_JUI_SPC_THERMAL.edf"
            incl_file_path = line.split(":")[1].replace("\"", "").strip()
            all_text += read_all_files(os.path.join(basepath, incl_file_path), basepath)

    return all_text


def extract_modelling(edf_path, basepath):
    """
    Returns a JSON detailing the EPS Experiments model from an EDF file

    :param edf_path: Path to EDF file.
    :type edf_path: str
    :param basepath: Base path of the EDF file.
    :type basepath: str
    :return: Returns a JSON detailing the EPS Experiments model from an EDF file
    :rtype: dict
    """

    all_edfs_text = read_all_files(edf_path, basepath)

    model = {}

    experiment=None
    module=None

    for line in all_edfs_text.splitlines():

        if line.startswith("#"):
            # Ignore comments
            continue

        tokens = line.split()

        if not len(tokens):
            # Ignore empty line
            continue
        
        if tokens[0] == "Experiment:":
            # Experiment: JUICE "JUICE Spacecraft"
            experiment = tokens[1]
            experiment_name = line.split("\"")[1] if "\"" in line else ""
            model[experiment] = { "id":   experiment,
                                  "name": experiment_name }

        elif tokens[0] == "Module:":
            # Module: RCT "RCT"
            module = tokens[1]
            module_name = line.split("\"")[1] if "\"" in line else ""
            if "modules" not in model[experiment]:
                model[experiment]["modules"] = {}

            model[experiment]["modules"][module] = { "id":   module,
                                                     "name": module_name }
                
        elif tokens[0] == "Mode:":
            # Mode: OFF
            
            if "modes" not in model[experiment]:
                model[experiment]["modes"] = []

            model[experiment]["modes"].append(tokens[1])
        
        elif tokens[0] == "Module_state:":
            # Module_state: OFF
            
            module_obj = model[experiment]["modules"][module]
            if "module_states" not in module_obj:
                module_obj["module_states"] = []

            module_obj["module_states"].append(tokens[1])

        elif tokens[0] == "Dataflow:":
            # Dataflow: FROM SSMM_LOW_RES
            model[experiment]["Dataflow"] = {"type": tokens[1], "value": tokens[2]}

        elif tokens[0] == "Link_section:":
            # Link_section: EXPERIMENT SSMM_HIGH_RES
            if tokens[1] == "EXPERIMENT":
                experiment = tokens[2]
            elif tokens[1] == "MODULE":
                module = tokens[2]

        elif tokens[0] == "Data_store:":
            # Data_store: <data store [[HK|SHARED|<experiment>] SELECTIVE]> <memory size [[Mbytes]]> <packet size [[bytes]]> [<priority>] [<identifier>]
            if "Data_store" not in model[experiment]:
                model[experiment]["Data_store"] = []

            model[experiment]["Data_store"].append({"name": tokens[1]})

    return model


def print_files_map(files_map, indent="   ", carry_indent=""):
    """
    Prints in a formated way the files map returned by extract_files()

    :param files_map: Dict with the data returned by eps_utils.extract_files()
    :type file_path: dict
    :param indent: String with the indentation characters offset.
    :type indent: str
    :param carry_indent: String with the indentation characters offset accumulated at this level.
    :type carry_indent: str
    """

    for key in files_map:
        print(carry_indent + " - " + str(os.path.basename(key)))
        if not isinstance(files_map[key], str):
            print_files_map(files_map[key], indent=indent, carry_indent=(carry_indent + indent))
    
    print ("")


def create_empty_datapack(file_path, timeStep=30, precision=1):
    """
    Returns an empty datapack object.

    :param file_path: File path where to store the datapack.
    :type file_path: str
    :param timeStep: Time resolution of the datapack in seconds.
    :type timeStep: int
    :param precision: Default datapack numeric representation precission.
    :type precision: int
    :return: Returns an empty datapack with the specified parameters.
    :rtype: dict
    """
        
    return { 
             "filePath": file_path,
             "timeStep": timeStep,
             "precision": precision,
             "fields": [{
                         "type": "time",
                         "format": "utc"
                         }]
            }


def create_empty_callback_datapack(id, timeStep=30, precision=1):
    """
    Returns an empty datapack object of type CALLBACK.

    :param id: String with the Id of the CALLBACK datapack.
    :type id: str
    :param timeStep: Time resolution of the datapack in seconds.
    :type timeStep: int
    :param precision: Default datapack numeric representation precission.
    :type precision: int
    :return: Returns an empty datapack with the specified parameters.
    :rtype: dict
    """
    
    datapack = create_empty_datapack(id, timeStep, precision)
    datapack["type"] = "CALLBACK"
    return datapack


def get_exp_power_overlays(eps_modelling):
    """
    Given an eps_modelling object obtained with eps_utils.extract_modelling(),
    returns a list with all the experiment's power overlays.

    :param eps_modelling: eps_modelling object returned by eps_utils.extract_modelling().
    :type eps_modelling: dict
    :return: Returns a list with all the experiment's power overlays.
    :rtype: list
    """

    overlays = []

    for exp_key in eps_modelling:
        experiment = eps_modelling[exp_key]

        exp_overlay = get_experiment_power_overlay(exp_key)
        overlays.append(exp_overlay)

        if "modules" in experiment:
            for module_key in experiment["modules"]:
                mod_overlay = get_experiment_module_power_overlay(exp_key, module_key)
                overlays.append(mod_overlay)
    
    return overlays


def get_experiment_overlay(experiment_name, overlay_id):
    """
    Returns an overlay given an experiment's name and an overlay id.

    :param experiment_name: The EPS experiment's name.
    :type experiment_name: str
    :param overlay_id: A supported OSVE Overlay Id.
    :type overlay_id: str
    :return: Returns an overlay with requested values.
    :rtype: dict
    """
    return {
                "type": "MAPPS",
                "overlayId": overlay_id,
                "parameter1": experiment_name
            }


def get_experiment_power_overlay(experiment_name):
    """
    Returns the experiment's power consumption overlay.

    :param experiment_name: The EPS experiment's name.
    :type experiment_name: str
    :return: Returns the experiment's power consumption overlay.
    :rtype: dict
    """
    return get_experiment_overlay(experiment_name, "EXP_POWER")


def get_experiment_module_power_overlay(experiment_name, module_name):
    """
    Returns the experiment's module's power consumption overlay.

    :param experiment_name: The EPS experiment's name.
    :type experiment_name: str
    :return: Returns the experiment's module's power consumption overlay.
    :rtype: dict
    """
    exp_overlay = get_experiment_power_overlay(experiment_name)
    exp_overlay["parameter2"] = module_name
    return exp_overlay


def get_experiment_datastore_files_overlay(experiment_name, datastore_name):
    """
    Returns a files overlay given an experiment's name and an datastore's name.

    :param experiment_name: The EPS experiment's name.
    :type experiment_name: str
    :param datastore_name: The datastore's name.
    :type datastore_name: str
    :return: Returns an overlay with requested values.
    :rtype: dict
    """
    return {
                "type": "OSVE",
                "overlayId": "EPS_DS_FILES",
                "parameter1": experiment_name,
                "parameter2": datastore_name
            }


def get_datarate_avg_columns(edf_path, basepath):

    model = extract_modelling(edf_path, basepath)

    columns = ["Time", "Available_Uplink"]

    for experiment in model:

        if "Dataflow" in model[experiment]:
            if model[experiment]["Dataflow"]["type"].startswith("FROM"):
                columns.append(experiment + "_Downlink")
                columns.append(experiment + "_Accum")
                continue

        elif "Data_store" in model[experiment]:
            columns.append(experiment + "_Memory")
            columns.append(experiment + "_Accum")

            for ds in model[experiment]["Data_store"]:
                columns.append(experiment + "_" + ds["name"] + "_Memory")
                columns.append(experiment + "_" + ds["name"] + "_Accum")

        else:
            columns.append(experiment + "_Upload")
            columns.append(experiment + "_Download")
            columns.append(experiment + "_Memory")
            columns.append(experiment + "_Accum")

    return columns


def read_data_rate_file(dr_filepath, edf_path, basepath):

    columns = get_datarate_avg_columns(edf_path, basepath)
    converters = {0: lambda x: datetime.strptime(x.decode("utf-8"), "%d-%b-%Y_%H:%M:%S")}

    for idx in range(len(columns)):
        if idx > 0:
            converters[idx] = float

    input_data = np.genfromtxt(dr_filepath, skip_header=26, delimiter=",",
                               names=columns, dtype=object, converters=converters)

    return input_data, columns
