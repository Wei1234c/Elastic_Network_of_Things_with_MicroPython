# coding: utf-8

import config


if config.IS_MICROPYTHON:    
    import machine
    id = str(machine.unique_id())
    id = id.replace('\\', '_')    
    for c in ['b\'', '_x', ' ', '_', '\'', '(', ')', '#', '|']:
        id = id.replace(c, '')
    WORKER_NAME = 'NodeMCU_' + id
    
else:
    WORKER_NAME = 'Client_366'