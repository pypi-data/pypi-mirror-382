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

This module contains some functions to handle OSVE Session files
"""

import os
import json
from shutil import move
from tempfile import mkstemp


def get_base_path(rel_path, root_path):
    """
    Returns a the absolute path of an OSVE relative path with a given root path.

    :param rel_path: Absolute or relative path to a scenario path.
    :type rel_path: str
    :param root_path: OSVE scenario root path.
    :type root_path: str
    :return: Returns the absolute path of a given scenario relative path.
    :rtype: str
    """
    return rel_path if os.path.isabs(rel_path) \
                    else os.path.abspath(os.path.join(root_path, rel_path))


def write_local_session_file(relative_session_file, JUICE_SCENARIO_DIR, KERNELS_JUICE):
    """
    Creates a "local" session file, with all the "path variables" replaced by
    the local user paths.

    :param relative_session_file: Relative of generic session file. So the one with variables to replace in its contents.
    :type relative_session_file: str
    :param JUICE_SCENARIO_DIR: Absolute path to the scenario in the JUICE repository (JUICE_OPS, JUICE_PREOPS or JUICE_VV).
    :type JUICE_REPO: str
    :param KERNELS_JUICE: Absolute path to the 'kernels' folder of the JUICE SPICE Kernel Dataset.
    :type KERNELS_JUICE: str
    :return: Returns the path of the created local session file.
    :rtype: str
    """

    local_session_file = relative_session_file.replace(".json", "_local.json")

    replacements = {}
    replacements["JUICE_SCENARIO_DIR"] = JUICE_SCENARIO_DIR
    replacements["KERNELS_JUICE"] = KERNELS_JUICE

    with open(local_session_file, "w+") as f:

        # Items are replaced as per correspondence in between the replacements dictionary
        with open(relative_session_file, 'r') as t:
            for line in t:
                if '{' in line:
                    for k, v in replacements.items():
                        if '{' + k + '}' in line:
                            line = line.replace('{' + k + '}', v.replace("\\", "/"))

                f.write(line)

    print("Created OSVE local session file: " + os.path.abspath(local_session_file))
    print("Don't forget removing it when done.")

    return local_session_file


def load_session_file(session_file_path):
    """
    Loads a session file from a given path.

    :param session_file_path: Relative or absolute path of session file to load.
    :type session_file_path: str
    :return: Returns a dictionay with the loaded session file data.
    :rtype: dict
    """

    if os.path.exists(session_file_path):
        with open(session_file_path) as f:
            session = json.load(f)
            if session is not None and "sessionConfiguration" in session:
                return session
            else:
                raise("Session file has no valid JSON format: " + str(session_file_path))
    else:
        raise("Session file doesn't exists: " + str(session_file_path))


def save_session_file(session_file_path, session):
    """
    Saves dictionay with the session file data into a given session file path.

    :param session_file_path: Relative or absolute path where to save the session file data.
    :type session_file_path: str
    :param session: Dictionay with the session file data to be saved.
    :type session: dict
    """
    with open(session_file_path, 'w') as f:
        json.dump(session, f)


def get_datapacks_from_session_file(session_file_path):
    """
    Returns the list of datapack objects defined in a session file.

    :param session_file_path: Relative or absolute path of session file to load.
    :type session_file_path: str
    :return: List of datapack objects defined in the session file.
    :rtype: list
    """
    session = load_session_file(session_file_path)

    session_conf = session["sessionConfiguration"]
    if "outputFiles" in session_conf:
        outFiles = session_conf["outputFiles"] 
        if "dataPacks" in outFiles:
            return outFiles["dataPacks"]
    
    return []


def save_datapack_in_session_file(session_file_path, datapack):
    """
    Saves a datapack object in the datapacks list of a session file.

    A Datapack object is basically a dict object with specified keys and proper values as
    specified in Session File's datapacks declaration documentation.

    :param session_file_path: Relative or absolute path of session where to save the datapack.
    :type session_file_path: str
    :param datapack: Datapack object to be saved.
    :type datapack: dict
    """
    session = load_session_file(session_file_path)

    session_conf = session["sessionConfiguration"]
    if "outputFiles" not in session_conf:
        session_conf["outputFiles"] = {}

    outFiles = session_conf["outputFiles"] 
    if "dataPacks" not in outFiles:
        outFiles["dataPacks"] = []
    
    outFiles["dataPacks"].append(datapack)
    
    save_session_file(session_file_path, session)


def show_report(session_file_path, root_scenario_path):
    """
    Prints a report with the details of the session file configuration settings.

    :param session_file_path: Relative or absolute path of session file to load.
    :type session_file_path: str
    :param root_scenario_path: Relative or absolute path of the root folder of the scenario.
    :type root_scenario_path: str
    """
    with open(session_file_path) as f:
        config = json.load(f)

        agm_config = None
        eps_config = None
        input_config = None
        modelling_config = None

        if "sessionConfiguration" in config:

            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

            if "instrumentSimulationConfiguration" in sessionConfiguration:
                eps_config = sessionConfiguration["instrumentSimulationConfiguration"]

            if "inputFiles" in sessionConfiguration:
                input_config = sessionConfiguration["inputFiles"]

                if "modellingConfiguration" in input_config:
                    modelling_config = input_config["modellingConfiguration"]

        print("")
        print("SESSION FILE REPORT:")

        if agm_config is not None:

            if "baselineRelPath" in agm_config:
                agm_base_path = get_base_path(agm_config["baselineRelPath"], root_scenario_path)
            else:
                print(" + No baselineRelPath found at attitudeSimulationConfiguration.")

            print("")
            print("- AGM:")

            if "ageConfigFileName" in agm_config:
                print(" + AGM configuration file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["ageConfigFileName"]))
            else:
                print(" + No ageConfigFileName found at attitudeSimulationConfiguration.")

            if "fixedDefinitionsFile" in agm_config:
                print(" + AGM fixed definitions file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["fixedDefinitionsFile"]))
            else:
                print(" + No fixedDefinitionsFile found at attitudeSimulationConfiguration.")

            if "predefinedBlockFile" in agm_config:
                print(" + AGM predefined block file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["predefinedBlockFile"]))
            else:
                print(" + No predefinedBlockFile found at attitudeSimulationConfiguration.")

            if "eventDefinitionsFile" in agm_config:
                print(" + AGM event definitions file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["eventDefinitionsFile"]))
            else:
                print(" + No eventDefinitionsFile found at attitudeSimulationConfiguration.")

            print("")
            print("- SPICE Kernels:")
            if "kernelsList" in agm_config:

                if "baselineRelPath" in agm_config["kernelsList"]:
                    kernels_base_path = get_base_path(agm_config["kernelsList"]["baselineRelPath"], root_scenario_path)
                else:
                    print(" + No baselineRelPath found at kernelsList.")

                if "fileList" in agm_config["kernelsList"]:
                    for kernel in agm_config["kernelsList"]["fileList"]:
                        if "fileRelPath" in kernel:
                            print(" + " + os.path.join(root_scenario_path, kernels_base_path, kernel["fileRelPath"]))
                        else:
                            print(" + No Kernel file relative path (fileRelPath) found.")
                else:
                    print(" + No fileList found at kernelsList.")
            else:
                print(" + No kernelsList found at attitudeSimulationConfiguration.")

        else:
            print("")
            print("- No AGM configuration found.")

        if eps_config is not None:
            eps_base_path = get_base_path(eps_config["baselineRelPath"], root_scenario_path)

            print("")
            print("- EPS:")

            if "unitFileName" in eps_config:
                print(" + EPS Units definition file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["unitFileName"]))
            else:
                print(" + No EPS Units definition file (unitFileName) found.")

            if "configFileName" in eps_config:
                print(" + EPS Configuration file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["configFileName"]))
            else:
                print(" + No EPS Configuration file (configFileName) found.")

            if "eventDefFileName" in eps_config:
                print(" + EPS Events definition file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["eventDefFileName"]))
            else:
                print(" + No EPS Events definition file (eventDefFileName) found.")

            if modelling_config is not None:
                modelling_base_path = get_base_path(modelling_config["baselineRelPath"], root_scenario_path)

                if "edfFileName" in modelling_config:
                    print(" + EPS Experiments definition file (EDF): " + os.path.join(root_scenario_path, modelling_base_path, modelling_config["edfFileName"]))
                else:
                    print(" + No EPS Experiments definition file (edfFileName) found.")

                if "observationDefFileName" in modelling_config:
                    print(" + EPS Observations definition file: " + os.path.join(root_scenario_path, modelling_base_path, modelling_config["observationDefFileName"]))
                else:
                    print(" + No EPS Observations definition file (observationDefFileName) found.")

            else:
                print("")
                print("- No EPS Modelling configuration found.")
        else:
            print("")
            print("- No EPS configuration found.")

        if input_config is not None:
            input_base_path = get_base_path(input_config["baselineRelPath"], root_scenario_path)

            print("")
            print("- Input files: " + input_base_path)

            if "xmlPtrPath" in input_config:
                print(" + AGM PTR File: " + os.path.join(root_scenario_path, input_base_path, input_config["xmlPtrPath"]))
            else:
                print(" + No AGM PTR (xmlPtrPath) found.")

            if "segmentTimelineFilePath" in input_config:
                print(" + EPS ITL File: " + os.path.join(root_scenario_path, input_base_path, input_config["segmentTimelineFilePath"]))
            else:
                print(" + No EPS ITL (segmentTimelineFilePath) found.")

            if "eventTimelineFilePath" in input_config:
                print(" + EPS EVENT File: " + os.path.join(root_scenario_path, input_base_path, input_config["eventTimelineFilePath"]))
            else:
                print(" + No EPS EVENT (eventTimelineFilePath) found.")

        else:
            print("")
            print("- No input files configuration found.")

        print("")


def get_kernels_to_load(session_file_path, root_scenario_path):
    """
    Returns a list of absolute paths with the SPICE kernels to be loaded from a session file.

    :param session_file_path: Relative or absolute path of session file to take kernels to load.
    :type session_file_path: str
    :param root_scenario_path: Relative or absolute path of the root folder of the scenario.
    :type root_scenario_path: str
    :return: List of absolute paths with the SPICE kernels to be loaded.
    :rtype: list
    """
    kernels_to_load = []

    with open(session_file_path) as f:
        config = json.load(f)

        if "sessionConfiguration" in config:
            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

        if agm_config is not None:
            if "kernelsList" in agm_config:
                if "baselineRelPath" in agm_config["kernelsList"]:
                    kernels_base_path = get_base_path(agm_config["kernelsList"]["baselineRelPath"], root_scenario_path)
                else:
                    raise "No baselineRelPath found at kernelsList."

                if "fileList" in agm_config["kernelsList"]:
                    for kernel in agm_config["kernelsList"]["fileList"]:
                        if "fileRelPath" in kernel:
                            kernels_to_load.append(os.path.abspath(os.path.join(kernels_base_path, kernel["fileRelPath"])))
                        else:
                            raise "No Kernel file relative path (fileRelPath) found."
                else:
                    raise "No fileList found at kernelsList."
            else:
                raise "No kernelsList found at attitudeSimulationConfiguration."

        else:
            raise "No AGM configuration found."

    return kernels_to_load    


def write_local_mk(mk_path, kernels_path):
    """
    [DEPRECATED] Use JUICE SPICE Git Hooks instead.
    See: https://s2e2.cosmos.esa.int/bitbucket/projects/SPICE_KERNELS/repos/juice/browse/misc/git_hooks/skd_post_merge
    
    Writes a local SPICE Meta-Kernel by copying and replacing (..) with a given kernels_path.

    :param mk_path: Path to the Meta-kernel to copy from.
    :type mk_path: str
    :param kernels_path: Absolute path to the "kernels" path of the SPICE Kernels Dataset.
    :type kernels_path: str
    :return: Tuple [bool, str], the creation success status flag and the path to the local Meta-Kernel.
    :rtype: list
    """

    replaced = False

    local_mk_path = mk_path.split('.')[0] + '_local.tm'

    if not os.path.exists(local_mk_path):
        # Create temp file
        fh, abs_path = mkstemp()
        with os.fdopen(fh, 'w') as new_file:
            with open(mk_path) as old_file:
                for line in old_file:

                    updated_line = line.replace("'..'","'" + kernels_path + "'")
                    new_file.write(updated_line)
                    # flag for replacing having happened
                    if updated_line != line:
                        replaced = True

        if replaced:
            # Update the permissions
            os.chmod(abs_path, 0o644)

            # Move new file

            move(abs_path, local_mk_path)

            print ("Created local SPICE Meta-Kernel: " + str(local_mk_path))

            return True, local_mk_path

    return False, ""


def remove_local_session_file(local_session_file):
    """
    Removes a "local" session file.

    :param local_session_file: Path of the "local" session file to be removed.
    :type local_session_file: str
    """

    if os.path.exists(local_session_file):
        os.remove(local_session_file)
        print(f"OSVE local session file removed: {local_session_file}")
    else:
        print(f"OSVE local session file not present {local_session_file}")


def get_path_from_session_file(file_key, session_file_path, root_scenario_path):
    """
    Returns the absolute path of any file specified in session file.

    :param file_key: File key as specified in the session file, for example: "ageConfigFileName", "xmlPtrPath", "edfFileName", "mgaDataFilePath"..
    :type file_key: str
    :param session_file_path: Relative or absolute path of session file to take the file path.
    :type session_file_path: str
    :param root_scenario_path: Relative or absolute path of the root folder of the scenario.
    :type root_scenario_path: str
    :return: Tuple [str, str], The file absolute path and the base path in case of file_key is found, None if not found.
    :rtype: list
    """
        
    with open(session_file_path) as f:
        config = json.load(f)

        agm_config = None
        eps_config = None
        input_config = None
        modelling_config = None

        if "sessionConfiguration" in config:

            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

            if "instrumentSimulationConfiguration" in sessionConfiguration:
                eps_config = sessionConfiguration["instrumentSimulationConfiguration"]

            if "inputFiles" in sessionConfiguration:
                input_config = sessionConfiguration["inputFiles"]

                if "modellingConfiguration" in input_config:
                    modelling_config = input_config["modellingConfiguration"]

        if agm_config is not None:

            if "baselineRelPath" in agm_config:
                agm_base_path = get_base_path(agm_config["baselineRelPath"], root_scenario_path)

            if file_key in agm_config:
                agm_base_path = os.path.join(root_scenario_path, agm_base_path)
                return os.path.join(agm_base_path, file_key), agm_base_path

        if eps_config is not None:
            eps_base_path = get_base_path(eps_config["baselineRelPath"], root_scenario_path)

            if file_key in eps_config:
                eps_base_path = os.path.join(root_scenario_path, eps_base_path)
                return os.path.join(eps_base_path, eps_config[file_key]), eps_base_path
            
            if modelling_config is not None:
                modelling_base_path = get_base_path(modelling_config["baselineRelPath"], root_scenario_path)

                if file_key in modelling_config:
                    modelling_base_path = os.path.join(root_scenario_path, modelling_base_path)
                    return os.path.join(modelling_base_path, modelling_config[file_key]), modelling_base_path

        if input_config is not None:
            input_base_path = get_base_path(input_config["baselineRelPath"], root_scenario_path)

            if file_key in input_config:
                input_base_path = os.path.join(root_scenario_path, input_base_path)
                return os.path.join(input_base_path, input_config[file_key]), input_base_path
    
    return None
