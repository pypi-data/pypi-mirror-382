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

The OsveEventSubscriber class is an implementation of the OsveSubscriberAbstract intended to 
let the developer an easy handling of the OSVE Events
"""

from osve.subscribers.osve_subscriber_abstract import OsveSubscriberAbstract


class OsveEventSubscriber(OsveSubscriberAbstract):

    """The OsveEventSubscriber class is an implementation of the OsveSubscriberAbstract intended to 
    let the developer an easy handling of the OSVE Events. The developer just needs to specify 
    the datapack Id and a callback function to be called everytime an event is risen. 
    See OsveEventSubscriber.__init__() documentation for more details."""
        
    onEventStateChangedFn = None

    def __init__(self, id, onEventStateChangedFn):
        """Initialises the OsveEventSubscriber instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str

        :param onEventStateChangedFn: A callback function of type ( functionName(dictionary) -> int ), so this function
                                      is called every time an OSVE event is risen.
        :type onEventStateChangedFn: function
        """
                
        super().__init__(id)
        self.onEventStateChangedFn = onEventStateChangedFn

    def onEventStateChanged(self, data) -> int:
        """This callback function is called every time that an OSVE event is risen.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the event properties.
        :type data: dict

        :rtype: int
        """
        return self.onEventStateChangedFn(data) if not self.onEventStateChangedFn is None else 0
