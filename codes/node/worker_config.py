# coding: utf-8

import config


if config.IS_MICROPYTHON: 
    import machine
    id = str(machine.unique_id())
    id = id.replace('\\', '_')
    id = id.replace('b\'', '')
    id = id.replace('_x', '')
    id = id.replace(' ', '')
    id = id.replace('_', '')
    id = id.replace('\'', '')    
    WORKER_NAME = 'NodeMCU_' + id
    
else:
    id = '366'
    WORKER_NAME = 'client_' + id