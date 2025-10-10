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

The ExternalConstraintAbstract class intended to provide control over the attitude checking 
processes performed by AGM
"""

from abc import abstractmethod


class ExternalConstraintAbstract(object):
    """The ExternalConstraintAbstract class intended to provide control over the attitude checking 
       processes performed by AGM"""
    
    id = ""
    step = "UNKNOWN"

    def __init__(self, id):
        """Initialises the ExternalConstraintAbstract instance.

        :param id: Shall match a External Constraint Id element in "extConstraintIds" 
                   optional list of the "attitudeSimulationConfiguration" section of the session file.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this external constraint
        self.id = id

    def _process_ext_const_message(self, msg_data):
        """Process an OSVE library callback message

        This method handles the OSVE external constraint message received as a dict.

        :param msg_data: Dictionary with message data.
        :type msg_data: dict
        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """

        res = 0

        # Update the execution step: "Load and checkings (CHK)" or "Simulation (SIM)"
        self.step = msg_data["step"]

        if msg_data["type"] == "EC_configureConstraintChecks":
            res = self.configureConstraintChecks()

        elif msg_data["type"] == "EC_resetConstraintFlags":
            self.resetConstraintFlags()

        elif msg_data["type"] == "EC_notifyEnvironmentInitialised":
            res = self.notifyEnvironmentInitialised()

        elif msg_data["type"] == "EC_update": 
            res = self.update(msg_data["time"], 
                                    [
                                        msg_data["q0"],
                                        msg_data["q1"],
                                        msg_data["q2"],
                                        msg_data["q3"]
                                    ])

        elif msg_data["type"] == "EC_cleanup":
            self.cleanup()

        elif msg_data["type"] == "EC_getInError":
            res = self.getInError(msg_data["skipChecks"], 
                                        msg_data["showMessages"], 
                                        msg_data["checkConstraints"], 
                                        msg_data["breakFound"])
        
        else:
            raise Exception("ExternalConstraintAbstract._process_ext_const_message, ExternalConstraint, unimplemented callback type: " + str(msg_data["type"]))
        
        return res

    @abstractmethod
    def configureConstraintChecks(self) -> int:
        """This callback function is called by AGM to notify external constraints
           to load and validate it's specific configuration.
           To abort execution return an integer smaller than zero.

        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """
        return 0

    @abstractmethod
    def resetConstraintFlags(self):
        """This callback function is called by AGM to notify external constraints
           that all the flagged constraints shall be resetted.
        """

    @abstractmethod
    def notifyEnvironmentInitialised(self) -> int:
        """This callback function is called by AGM to notify external constraints
           to that everything looks ready to start simulation.
           To abort execution return an integer smaller than zero.

        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """
        return 0
    
    @abstractmethod
    def update(self, time, sc_quats) -> int:
        """This callback function is called by AGM to notify external constraints
           that spacecraft attitude data has been updated and constraints shall be
           reevaluated.
           To abort execution return an integer smaller than zero.

        :param time: The current time in format: YYYY-MM-DDTHH:mm:SSZ
        :type time: str

        :param sc_quats: The spacecracft quaternions relative to J2000
        :type sc_quats: list of double

        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """
        return 0

    @abstractmethod
    def cleanup(self):
        """This callback function is called by AGM to notify external constraints
           that all computed and temporary data shall be cleaned up.
        """

    @abstractmethod
    def getInError(self, skipChecks, showMessages, checkConstraints, breakFound) -> int:
        """This callback function is called by AGM at the end of every timestep to 
           check if any constraint has been violated. In this case this external
           constrain shall returns an integer greater than 0 then OSVE will consider that 
           this external constrain has violations, otherwise not.

        :param skipChecks: Indicates if constraint checks shall be skipped or not, depends on the simulation stage.
        :type skipChecks: bool

        :param showMessages: Indicates if the external constaints shall do logging or not, depends on the simulation stage.
        :type showMessages: bool

        :param checkConstraints: Defines the way constraints are checked during the update of the timeline at each current time.
                                0 => NONE: No constraints are checked at all.
                                1 => ALWAYS: Constraints are checked for every call as if it was the first time (no memory).
                                2 => CONTINUOUS: Constraints are checked assuming the calls are continuous in time (with memory).
        :type checkConstraints: int

        :param breakFound: Indicates if the external constaints if there are any contraint violated at current time.
        :type breakFound: bool
        
        :return: Returns an integer with the callback handling status: (ret > 0) -> Contraint Violation, (ret <= 0) -> Continue.
        :rtype: int
        """
        return 0

