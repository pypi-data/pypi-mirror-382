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

The OsvePtrLogger class intended to provide the OSVE logs
grouped by PTR Block. Note it requires AGM/AGE simulation in order to work.
"""

from osve.subscribers.osve_ptr_abstract import OsvePtrAbstract

class OsvePtrLogger(OsvePtrAbstract):
    """The OsvePtrLogger class intended to provide the OSVE logs
       grouped by PTR Block. Note it requires AGM/AGE simulation in order to work."""

    blocks_data = []
    def __init__(self, id):
        """Initialises the OsvePtrAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        super().__init__(id)

    def onPtrBlockEnd(self, blockData) -> int:
        """This function will be called every PTR block end, 
        and will store the blockData to the list of already stored blocks_data.

        :param blockData: Dictionary that contains the produced block data.
        :type blockData: dict

        :return: Returns 0
        :rtype: int
        """
        self.blocks_data.append(blockData)
        return 0
    
    def log(self, verbose=False):
        """This function will produce an OSVE simulation log but in this case the logs
        will be grouped by PTR block designer.

        :param verbose: True for verbose output logs.
        :type verbose: bool

        :return: Returns a dictionary with the logs grouped by designer.
        :rtype: dict
        """
        ptr_log = {}
        idx = 1
        for blockData in self.blocks_data:
            
            log_report = False
            # Log the block if it has an ERROR.
            for log_data in blockData["block_logs"]:
                if log_data["severity"] == 'ERROR':
                    log_report = True
            
            if log_report:
                if str(blockData["block_type"]) != 'SLEW':
                    
                    if "observations" in blockData:
                        designer = blockData["observations"]["designer"]
                        observations = blockData["observations"]["observations"]
                        for observation in observations:
                            if observation["unit"] == designer:
                                designer_obs = observation["definition"]
                        if verbose: print(f'BLOCK {str(idx)} | {designer} | {designer_obs} | {str(blockData["block_start"])} - {str(blockData["block_end"])}')

                    else:
                        if verbose: print(f'BLOCK {str(idx)} | SOC | {str(blockData["block_type"])} {str(blockData["block_mode"])} | {str(blockData["block_start"])} - {str(blockData["block_end"])}')
                        designer = 'SOC'
                        designer_obs = f'{str(blockData["block_type"])} {str(blockData["block_mode"])}'

                    if "block_logs" in blockData:
                        error_messages = []
                        for log_data in blockData["block_logs"]:
                            if str(log_data["severity"]) != 'DEBUG' and str(log_data["module"]) == 'AGM':
                            
                                error_message = "      " + str(log_data["severity"]) + " , " + str(log_data["time"]) + " , " + str(log_data["text"])
                                if verbose: print(error_message)
                                error_messages.append({
                                    'severity':str(log_data["severity"]),
                                    'time':str(log_data["time"]),
                                    'text':str(log_data["text"])
                                })    

                    if designer not in ptr_log:
                        ptr_log[designer] = {}
                    ptr_log[designer][f'Block ({str(idx)})'] =  \
                                                   {'observation':designer_obs,
                                                    'start_time':str(blockData["block_start"]), 
                                                    'end_time':str(blockData["block_end"]),
                                                    'error_messages':error_messages}                    
                
                else:
                    
                    try:
                        prev_designer_obs_end = str(self.blocks_data[idx-2]["block_end"])
                        prev_designer = self.blocks_data[idx-2]["observations"]["designer"]
                        observations = self.blocks_data[idx-2]["observations"]["observations"]
                        for observation in observations:
                            if observation["unit"] == prev_designer:
                                prev_designer_obs = observation["definition"]
                    except:
                        prev_designer = 'SOC'                        
                        prev_designer_obs = f'{str(self.blocks_data[idx-2]["block_type"])} {str(self.blocks_data[idx-2]["block_mode"])}'
                    try:
                        next_designer_obs_start = str(self.blocks_data[idx]["block_start"])
                        next_designer = self.blocks_data[idx]["observations"]["designer"]
                        observations = self.blocks_data[idx]["observations"]["observations"]
                        for observation in observations:
                            if observation["unit"] == next_designer:
                                next_designer_obs = observation["definition"]
                    except:
                        next_designer = 'SOC'
                        next_designer_obs = f'{str(self.blocks_data[idx]["block_type"])} {self.str(self.blocks_data[idx]["block_mode"])}'
                        
                    print(f'BLOCK {str(idx)} |  {prev_designer},{next_designer} | SLEW | {prev_designer_obs_end} ({prev_designer_obs}) - {next_designer_obs_start} ({next_designer_obs}) ')        

                    if "block_logs" in blockData:
                        error_messages = []
                        for log_data in blockData["block_logs"]:
                            if str(log_data["severity"]) != 'DEBUG' and str(log_data["module"]) == 'AGM':
                            
                                error_message = "      " + str(log_data["severity"]) + " , " + str(log_data["time"]) + " , " + str(log_data["text"])
                                if verbose: print(error_message)
                                error_messages.append({
                                    'severity':str(log_data["severity"]),
                                    'time':str(log_data["time"]),
                                    'text':str(log_data["text"])
                                })    
                    
                    if prev_designer not in ptr_log:
                        ptr_log[prev_designer] = {}
                    ptr_log[prev_designer][f'Block ({str(idx-1)}) SLEW AFTER'] = \
                                                   {'observation':f'{prev_designer_obs}',
                                                   'start_time':prev_designer_obs_end, 
                                                   'end_time':next_designer_obs_start,
                                                   'error_messages':error_messages}

                    if next_designer not in ptr_log:
                        ptr_log[next_designer] = {}
                    ptr_log[next_designer][f'Block ({str(idx+1)}) SLEW BEFORE'] = \
                                                   {'observation':f'{next_designer_obs}',
                                                   'start_time':prev_designer_obs_end, 
                                                   'end_time':next_designer_obs_start,
                                                   'error_messages':error_messages}
            
            idx += 1                
        
        return ptr_log
