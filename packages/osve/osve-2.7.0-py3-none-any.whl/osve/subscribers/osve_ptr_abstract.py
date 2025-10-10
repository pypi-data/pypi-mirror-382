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

The OsveSubscriber class intended to provide on the fly 
simulation status and data to the main OSVE caller program.
"""

from abc import abstractmethod
from osve.subscribers.osve_subscriber_abstract import OsveSubscriberAbstract
from osve.subscribers.osve_logger_abstract import OsveLoggerAbstract


class OsvePtrAbstract(OsveSubscriberAbstract, OsveLoggerAbstract):

    """The OsvePtrAbstract class intended to provide on the fly simulation status and data to the main OSVE caller program
       but in this case the data will be provided grouped by PTR Block, and reported every time a block ends. 
       This class shall be inherited by a child class tht must implement/override the OsvePtrAbstract abstract methods."""
    
    current_block = "" # To store ref of current block, consider it finished once changed
    block_steps = []  # To store every timestep data for current PTR block
    block_events = []  # To store risen events during current PTR block
    block_logs = []  # To store logged messages during current PTR block
    on_simulation = False

    def __init__(self, id):
        """Initialises the OsvePtrAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        super().__init__(id)

    def onSimulationStart(self, data) -> int:
        """Called once simulation is started.

        :param data: Simulation start event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """

        self.reset()
        self.on_simulation = True
        return 0

    def onSimulationTimeStep(self, data) -> int:
        """Called on every OSVE simulation time step, this method will store the requested OSVE simulation data into the block steps. 

        :param data: Simulation step data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """
        if self.on_simulation:
            self.block_steps.append(data)
        return 0

    def onSimulationPtrBlockStart(self, data) -> int:
        """Called on every PTR Block start during simulation, this method will notify that a new PTR block has started. 

        :param data: Block start data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """
                
        ret = 0
        
        if self.on_simulation:
            ret = self.onPtrBlockStart(data)

        return ret
    
    def onSimulationPtrBlockEnd(self, data) -> int:
        """Called on every PTR Block end during simulation, this method will store the recollected block data and then
         notify that the current PTR block has ended. 

        :param data: Block end data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """
        
        ret = 0
        
        if self.on_simulation:
            
            data["block_steps"] = self.block_steps
            data["block_events"] = self.block_events
            data["block_logs"] = self.block_logs

            ret = self.onPtrBlockEnd(data)

            self.reset()

        return ret
    
    def onSimulationEnd(self, data) -> int:
        """Called once simulation is finished.

        :param data: Simulation finish event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """
        self.on_simulation =False
        return 0

    def onEventStateChanged(self, data) -> int:
        """Called every time an OSVE Event status has changed.

        :param data: Event data.
        :type data: dict
        :return: Returns 0.
        :rtype: int
        """
                
        if self.on_simulation:
            self.block_events.append(data)
        return 0

    def onMsgReceived(self, severity, module, time, text):
        """onMsgReceived() will handle the messages sent for logging.

        :param severity: Message severity.
        :type severity: str
        :param module: The OSVE Module that produces the message.
        :type module: str
        :param time: Sting with a formated date.
        :type time: str
        :param text: Message text to log.
        :type text: str
        :return: Returns 0
        :rtype: int
        """
        if self.on_simulation:
            self.block_logs.append({"severity": severity, "module": module, "time": time, "text": text})
        return 0

    @abstractmethod
    def onPtrBlockStart(self, blockData) -> int:
        """This callback function is called every time a PTR block execution is
           started. It provides as an argument a dictionary with the every
           timestep data, risen events and logs.
           If returned int is smaller than 0 then simulation is aborted.

        :param blockData: Dictionary that contains the some block data.
        :type blockData: dict

        :return: Returns 0
        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onPtrBlockEnd(self, blockData) -> int:
        """This callback function is called every time a PTR block execution is
           finished. It provides as an argument a dictionary with the every
           timestep data, risen events and logs.
           If returned int is smaller than 0 then simulation is aborted.

        :param blockData: Dictionary that contains the produced block data.
        :type blockData: dict

        :return: Returns 0
        :rtype: int
        """
        return 0
    
    def reset(self):
        """This will clear all the status data of the OsvePtrAbstract object."""
        self.block_steps = []
        self.block_events = []
        self.block_logs = []
