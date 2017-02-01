# coding: utf-8

# noinspection PyUnresolvedReferences
import config


if config.IS_MICROPYTHON:
    # noinspection PyUnresolvedReferences
    import machine
    unique_id = str(machine.unique_id())
    unique_id = unique_id.replace('\\', '_')    
    for c in ['b\'', '_x', ' ', '_', '\'', '(', ')', '#', '|']:
        unique_id = unique_id.replace(c, '')
    WORKER_NAME = 'NodeMCU_' + unique_id
    
else:
    WORKER_NAME = 'Client_366'
