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
Created on July, 2023

@author: Ricardo Valles Blanco (ESAC)

The OsveSubscriberAbstract class intended to provide on the fly 
simulation status and data to the main OSVE caller program.
"""

from abc import abstractmethod
from ctypes import *


# Some ctypes callback definitions
class Callback(Structure):
    _fields_ = [('jsonStr', c_char_p)]


CALLBACK = CFUNCTYPE(c_int, POINTER(Callback))


class OsveSubscriberAbstract(object):
    """The OsveSubscriberAbstract class intended to provide on the fly simulation status and data to the main OSVE caller program. 
       This class shall be inherited by a child class tht must implement/override the OsveSubscriberAbstract abstract methods."""
    
    id = ""
    
    def __init__(self, id):
        """Initialises the OsveSubscriberAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this subscriber
        self.id = id

    def _process_message(self, msg_data):
        """Process an OSVE library callback message

        This method handles the OSVE message received as a JSON object.

        :param msg_data: Dictionary with message data.
        :type msg_data: dict
        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """
        
        if msg_data["type"] == "OSVE_SIMULATION_START":
            res = self.onSimulationStart(msg_data)

        elif msg_data["type"] == "OSVE_SIMULATION_STEP":
            res = self.onSimulationTimeStep(msg_data)

        elif msg_data["type"] == "OSVE_SIMULATION_PTR_BLOCK_START":
            res = self.onSimulationPtrBlockStart(msg_data)

        elif msg_data["type"] == "OSVE_SIMULATION_PTR_BLOCK_END":
            res = self.onSimulationPtrBlockEnd(msg_data)

        elif msg_data["type"] == "OSVE_SIMULATION_END":
            res = self.onSimulationEnd(msg_data)

        elif msg_data["type"] == "OSVE_EVENT_STATE_CHANGED":
            res = self.onEventStateChanged(msg_data)
        
        else:
            raise Exception("OsveSubscriberAbstract._process_message, unimplemented callback type: " + str(msg_data["type"]))
        
        return res
        
    @abstractmethod
    def onSimulationStart(self, data) -> int:
        """This callback function is called every time a simulation started.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the selected ovelay name's and unit's.
        :type data: dict

        :rtype: int
        """
        return 0

    @abstractmethod
    def onSimulationTimeStep(self, data) -> int:
        """This callback function is called every time a time step has been simulated.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the selected ovelay name's and values.
        :type data: dict

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onSimulationPtrBlockStart(self, data) -> int:
        """This callback function is called every time a PTR block execution is
           started. If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains some block data of the started block.
        :type data: dict

        :rtype: int
        """
        return 0
     
    @abstractmethod
    def onSimulationPtrBlockEnd(self, data) -> int:
        """This callback function is called every time a PTR block execution is
           finished. If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the block start date of the finished block.
        :type data: dict

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onSimulationEnd(self, data) -> int:
        """This callback function is called every time that a simulation finishes.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the simulation end time.
        :type data: dict

        :rtype: int
        """
        return 0

    @abstractmethod
    def onEventStateChanged(self, eventData) -> int:
        """This callback function is called every time that an OSVE event is risen.
           If returned int is smaller than 0 then simulation is aborted.

        :param eventData: Dictionary that contains the event properties.
        :type eventData: dict

        :rtype: int
        """
        return 0
