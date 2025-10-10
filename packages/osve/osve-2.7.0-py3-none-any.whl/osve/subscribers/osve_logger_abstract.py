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

The OsveLoggerAbstract class intended to provide runtime access to logging messages reported by OSVE
"""

from abc import abstractmethod


class OsveLoggerAbstract(object):
    """The OsveLoggerAbstract class intended to provide runtime access to logging messages reported by OSVE"""
    
    id = ""

    def __init__(self, id):
        """Initialises the OsveLoggerAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this logger
        self.id = id

    def _process_log_message(self, msg_data):
        """Process an OSVE library callback message

        This method handles the OSVE log message received as a JSON object.

        :param msg_data: Dictionary with message data.
        :type msg_data: dict
        :return: Returns an integer with the callback handling status: (ret >= 0) -> Continue, (ret < 0) -> Abort simulation.
        :rtype: int
        """
        
        self.onMsgReceived(msg_data["severity"], 
                            msg_data["module"], 
                            msg_data["time"],
                            msg_data["text"])
        
    @abstractmethod
    def onMsgReceived(self, severity, module, time, text):
        """Abstract method onMsgReceived() to be implemented by child class to handle the message to log.

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
                
        return 0

