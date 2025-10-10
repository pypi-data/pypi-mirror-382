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

The OsveIdleSubscriber class intended to provide a way to IGNORE
callbacks from OSVE when running a session_file with CALLBACKS
datapacks but the user wants to avoid their implementation.
"""

from osve.subscribers.osve_subscriber_abstract import OsveSubscriberAbstract

class OsveIdleSubscriber(OsveSubscriberAbstract):
    """The OsveIdleSubscriber class intended to provide a way to IGNORE
        callbacks from OSVE when running a session_file with CALLBACKS
        datapacks but the user wants to avoid their implementation."""
    
    id = ""
    
    def __init__(self, id):
        super().__init__(id)
    
    def onSimulationStart(self, data) -> int:
        return 0

    def onSimulationTimeStep(self, data) -> int:
        return 0

    def onSimulationPtrBlockStart(self, data) -> int:
        return 0
    
    def onSimulationPtrBlockEnd(self, data) -> int:
        return 0
    
    def onSimulationEnd(self, data) -> int:
        return 0

    def onEventStateChanged(self, data) -> int:
        return 0

    def onMsgReceived(self, severity, module, time, text):
        return 0