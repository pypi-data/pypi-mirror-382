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

The OsveDatapack class intended to provide the requested overlays
data obtained from the OSVE simulation.

Usage example:

    theOsveDatapack = OsveDatapack()
    theOsveDatapack.add_overlays(eps_utils.OSVE_OVERLAYS["POWER"])
    theOsveDatapack.commit_changes(local_session_file)
    the_osve.register_subscriber(theOsveDatapack)
    
    if the_osve.execute(test_input_path, local_session_file) == 0:
    
        data = theOsveDatapack.toNumpyArray()

        start_time = data["time"][0]
        end_time = data["time"][-1]

        print("Simulation interval from " + str(data["time"][0]) + " to " + str(data["time"][-1]) +
              " , duration: " + str((data["time"][-1] - data["time"][0]) / np.timedelta64(1, 's')))

        print("Average power consumption (Watts): " + str(np.mean(data["TOTAL_POWER"])))
        print("Maximum power consumption (Watts): " + str(np.max(data["TOTAL_POWER"])))

    else:
        print("OSVE execution failed. See log file.")
    
"""

from osve.subscribers.osve_subscriber_abstract import OsveSubscriberAbstract
from osve.eps_utils import create_empty_callback_datapack
from osve.session_file import save_datapack_in_session_file
import uuid
import numpy as np

class OsveDatapack(OsveSubscriberAbstract):
    """The OsveDatapack class intended to provide the requested overlays
        data obtained from the OSVE simulation."""
    
    has_changes = False
    on_simulation = False
    datapack = None
    data = []

    def __init__(self, timeStep=30, precision=1):
        """Initialises the OsveDatapack instance.

        :param timeStep: [OPTIONAL] Integer specifying the time resolution in seconds to use during this datapack
            generation.
        :type timeStep: int
        :param precision: Integer in range 0..12 specifying the default number of decimal places for reported values.
            If 'precision' not specified, then 1 decimal places will be used.
        :type precision: int        
        """

        super().__init__(str(uuid.uuid4()))
        self.datapack = create_empty_callback_datapack(self.id, timeStep, precision)
        self.has_changes = True

    def add_overlay(self, overlay):
        """Adds an overlay to the list of overlays of the datapack.

        :param overlay: The overlay dict as defined in eps_utils module functions or in the session file datapack fields.
        :type overlay: dict       
        """
                
        self.add_overlays([overlay])
        self.has_changes = True

    def add_overlays(self, overlays):
        """Adds every overlay in the overlays list to the list of overlays of the datapack.

        :param overlays: The list of overlay dicts as defined in eps_utils module functions or in the session file
            datapack fields.
        :type overlays: list       
        """
        self.datapack["fields"].extend(overlays)
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
            
            # Remove unecessary fields to free memory
            del data["id"]
            del data["type"]

            self.data.append(data)
        return 0
    
    def onSimulationEnd(self, data) -> int:
        """Called once simulation is finished.

        :param data: Simulation finish event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """

        self.on_simulation =False
        return 0
    
    def toNumpyArray(self):
        """
        Convert the obtained simulation data to a structured NumPy array.

        :return: Structured Numpy array with overlay names as columns.
        :rtype: numpy.ndarray
        """

        if not self.data:
            return np.array([])  # empty array if the list is empty

        keys = self.data[0].keys()

        dtype = []
        for key in keys:
            sample_val = self.data[0][key]
            if key == "time":
                # Use numpy datetime64 with second precision
                dtype.append((key, 'datetime64[s]'))
            elif isinstance(sample_val, (float, int)):
                dtype.append((key, 'f4'))  # float32
            else:
                max_len = max(len(str(d[key])) for d in self.data)
                dtype.append((key, f'U{max_len}'))

        arr = np.empty(len(self.data), dtype=dtype)

        for i, entry in enumerate(self.data):
            values = []
            for k in keys:
                val = entry[k]
                if k == "time":
                    # Convert to numpy.datetime64
                    val = np.datetime64(val)
                values.append(val)
            arr[i] = tuple(values)

        return arr
    
    def reset(self):
        """This will clear all the status data of the datapack."""
        self.has_changes = False
        self.on_simulation = False
        self.datapack = None
        self.data = []