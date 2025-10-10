# *****************************************************************************#
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
# *****************************************************************************#


"""
Created on June 2025

@author: Ricardo Valles Blanco (ESAC)

The OsveFiles class is intended to provide access to the EPS Files Layer

Usage example:

    theOsveFiles = OsveFiles()
    theOsveFiles.add_datastore("SSMM_EXP", "UVS_BULK_DATASTORE")
    theOsveFiles.commit_changes(local_session_file)
    the_osve.register_subscriber(theOsveFiles)
    
    if the_osve.execute(test_input_path, local_session_file) == 0:
    
        files = theOsveFiles.getFilesMap()

    else:
        print("OSVE execution failed. See log file.")
    
"""
import json

from osve.subscribers.osve_subscriber_abstract import OsveSubscriberAbstract
from osve.eps_utils import create_empty_callback_datapack, get_experiment_datastore_files_overlay
from osve.session_file import save_datapack_in_session_file
import uuid


class OsveFiles(OsveSubscriberAbstract):
    """The OsveFiles class intended to provide access to the EPS Files Layer of an EPS Mass-Memory Datastore"""

    has_changes = False
    on_simulation = False
    datapack = None
    filesMap = {}
    onFilesMapChangedFn = None

    def __init__(self, onFilesMapChangedFn=None):
        """Initialises the OsveFiles instance.

        :param onFilesMapChangedFn: [OPTIONAL] The onFilesMapChangedFn callback function to be called every time the
            files map is updated. This function shall support two input parameters, the first on is the time as string,
            and the second will be the updated filesMap.
        :type onFilesMapChangedFn: function pointer       
        """

        super().__init__(str(uuid.uuid4()))
        self.onFilesMapChangedFn = onFilesMapChangedFn
        self.datapack = create_empty_callback_datapack(self.id, 1, 0)
        self.has_changes = True

    def add_datastore(self, experiment, datastore):
        """Adds an experiment's datastore to the list of datastores for being analysed.

        :param experiment: The mass memory experiment name.
        :type experiment: str
         :param datastore: A valid datastore name of the mass memory.
        :type datastore: str
        """
        overlay = get_experiment_datastore_files_overlay(experiment, datastore)
        self.datapack["fields"].append(overlay)
        self.has_changes = True

    def commit_changes(self, session_file_path):
        """Saves the datapack in the session file specified, in order to OSVE to take this datapack into account.

        :param session_file_path: The session file path where to store this OSVE Datapack.
        :type session_file_path: string       
        """

        save_datapack_in_session_file(session_file_path, self.datapack)
        self.has_changes = False

    def onSimulationStart(self, data) -> int:
        """Called once simulation is started, it will raise an exception if datapack changes are not committed.

        :param data: Simulation start event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """

        if self.has_changes:
            raise "Changes not committed!, please commit datapack changes with 'commit_changes()' before starting simulation."

        self.reset()
        self.on_simulation = True
        return 0

    def onSimulationTimeStep(self, data) -> int:
        """Called on every OSVE simulation time step, this method will store the requested OSVE simulation data into 
        the datapack. 

        :param data: Simulation step data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """

        if self.on_simulation:

            # Remove un-necessary fields to free memory
            del data["id"]
            del data["type"]

            time = data["time"]
            del data["time"]

            filesMapChanged = str(self.filesMap) != str(data) if self.onFilesMapChangedFn is not None else False
            self.filesMap = data

            if filesMapChanged:
                return self.onFilesMapChangedFn(time, self.getFilesMap())

        return 0

    def onSimulationEnd(self, data) -> int:
        """Called once simulation is finished.

        :param data: Simulation finish event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """

        self.on_simulation = False
        return 0

    def getFilesMap(self):
        """
        Returns the files map when called after simulation end.

        :return: Dictionary with the files per datastore
        :rtype: dict
        """
        filesMap = {}

        for ds_key in self.filesMap:
            filesMap[ds_key] = json.loads(self.filesMap[ds_key].replace("\"[", "[")
                                                               .replace("\"\"", "\"")
                                                               .replace("]\"", "]"))

        return filesMap

    def reset(self):
        """This will clear all the status data of the datapack."""
        self.has_changes = False
        self.on_simulation = False
        self.datapack = None
        self.filesMap = {}
