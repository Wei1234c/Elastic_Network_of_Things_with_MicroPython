
# Neural network deploy


```python
import os
import sys
import time
 
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'codes', 'client')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'codes', 'node')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'codes', 'shared')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'codes', 'micropython')))
 
import client
from collections import OrderedDict
```


```python
import pandas as pd
from pandas import DataFrame
from time import sleep
REFRACTORY_PERIOD = 0.1   # 0.1 seconds
```


```python
# 每個 ESP8266模組 各代表一個 neurons
# neurons = ['neuron_x1', 'neuron_x2', 'neuron_h1', 'neuron_h2', 'neuron_h3', 'neuron_y'] 
neurons = ['neuron_x1', 'neuron_x2'] 
```

## Start client


```python
the_client = client.Client()
the_client.start()

while not the_client.status['Is connected']:            
    time.sleep(1)
    print('Node not ready yet.')
```

    My name is Client_366
    
    [connected: ('192.168.0.100', 9662)]
    Sending 305 bytes
    Message:
    OrderedDict([('command', 'set connection name'), ('correlation_id', '2017-01-30 18:41:47.523600'), ('kwargs', {'name': 'Client_366'}), ('message_id', '2017-01-30 18:41:47.523600'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'command')])
    
    [Listen to messages]
    
    Data received: 401 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:47.523600'), ('message_id', '2017-01-30 18:41:47.632800'), ('receiver', 'Client_366'), ('reply_to', 'Hub'), ('result', {'NodeMCU_f1d30800': "('192.168.0.103', 30406)", 'Client_366': "('192.168.0.100', 56066)", 'NodeMCU_1dsc000': "('192.168.0.104', 32406)"}), ('sender', 'Hub'), ('time_stamp', '2017-01-30 18:41:47.632800'), ('type', 'result')])
    
    Node not ready yet.
    

## Utilities

### List nodes


```python
# Ask Hub for a list of connected nodes
def list_nodes():
    message = {'type': 'command',
                       'command': 'list connections by name',
                       'need_result': True}     

    _, asynch_result = the_client.request('Hub', message) 

    try:
        remote_nodes = sorted(list(asynch_result.get().keys()))

        print ('\n[____________ Connected nodes ____________]\n')        
        print('\nConnected nodes:\n{}\n'.format(remote_nodes)) 
        
        return remote_nodes

    except Exception as e:
        print(e)
```


```python
def reset_node(node):
    message = {'type': 'exec',
               'to_exec': 'import machine;machine.reset()'}
    the_client.request(node, message) 
```

    
    Data received: 166 bytes
    Message:
    OrderedDict([('info', 'Just check to see if you are still there. No reply needed.'), ('receiver', 'all workers'), ('sender', 'Hub'), ('type', 'info')])
    
    


```python
# reset_node('neuron_x1')
```


```python
def rename_node(node, new_name):
    message = {'type': 'function',
               'function': 'rename',
               'kwargs': {'name': new_name}}
    the_client.request(node, message) 
    
    message = {'type': 'function',
               'function': 'set_connection_name'}
    the_client.request(node, message) 
    

def rename_nodes(nodes, neurons):    
    i = 0 
    for node in nodes:
        if node != the_client.node.worker.name:  # exclude client self
            rename_node(node, neurons[i])
            i += 1
```


```python
def fire(node):
    message = {'type': 'function',
               'function': 'fire'}
    the_client.request(node, message) 

def addConnection(node, neuron):
    message = {'type': 'function',
               'function': 'addConnection',
               'kwargs': {'neuron_id': neuron}}
    the_client.request(node, message) 
    
def set_connections(node, connections):
    message = {'type': 'function',
               'function': 'setConnections',
               'kwargs': {'connections': connections}}
    the_client.request(node, message)     
    
def get_connections(node):
    message = {'type': 'function',
               'function': 'getConnections', 
               'need_result': True}
    _, result = the_client.request(node, message) 
    return result.get()    

def setWeight(node, neuron, weight):
    message = {'type': 'function',
               'function': 'setWeight',
               'kwargs': {'neuron_id': neuron,
                          'weight': weight,}}
    the_client.request(node, message) 

def setThreshold(node, threshold):
    message = {'type': 'function',
               'function': 'setThreshold',
               'kwargs': {'threshold': threshold}}
    the_client.request(node, message) 
        
def getConfig(node):
    message = {'type': 'function',
               'function': 'getConfig', 
               'need_result': True}
    _, result = the_client.request(node, message) 
    return result.get()

def getLog(node):
    message = {'type': 'function',
               'function': 'getLog', 
               'need_result': True}
    _, result = the_client.request(node, message) 
    return result.get()

def emptyLog(node):
    message = {'type': 'function',
               'function': 'emptyLog'}
    the_client.request(node, message)
    
def emptyLogs():
    for neuron in neurons:
        emptyLog(neuron) 
        
# 彙整logs。將所有 neurons 中的 logs merge 在一起，成為一個 Pandas.DataFrame
def mergeLogs():
    logs = []
    
    for neuron in neurons:
        if neuron != the_client.node.worker.name:  # exclude client self
            currentLog = getLog(neuron)
            if currentLog:
                logs += currentLog 
            
    df = DataFrame(list(logs), columns = ['time', 'neuron', 'message']) 
    df.set_index('time', inplace = True)
    df.sort_index(inplace = True)
    
    return df        
```


```python
# print 出 一個 neuron 中的 Log
def printConfig(neuron):
    print('{0:_^78}\n {1}\n'.format(neuron + " config:", getConfig(neuron)))
```

## 設定 network config

### Rename nodes


```python
remote_nodes = list_nodes() 
rename_nodes(remote_nodes, neurons)
time.sleep(2)
remote_nodes = list_nodes()
```

    Sending 276 bytes
    Message:
    OrderedDict([('command', 'list connections by name'), ('correlation_id', '2017-01-30 18:41:49.620800'), ('message_id', '2017-01-30 18:41:49.620800'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'command')])
    
    
    Data received: 401 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:49.620800'), ('message_id', '2017-01-30 18:41:49.698800'), ('receiver', 'Client_366'), ('reply_to', 'Hub'), ('result', {'NodeMCU_f1d30800': "('192.168.0.103', 30406)", 'Client_366': "('192.168.0.100', 56066)", 'NodeMCU_1dsc000': "('192.168.0.104', 32406)"}), ('sender', 'Hub'), ('time_stamp', '2017-01-30 18:41:49.698800'), ('type', 'result')])
    
    
    [____________ Connected nodes ____________]
    
    
    Connected nodes:
    ['Client_366', 'NodeMCU_1dsc000', 'NodeMCU_f1d30800']
    
    Sending 284 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:49.792400'), ('function', 'rename'), ('kwargs', {'name': 'neuron_x1'}), ('message_id', '2017-01-30 18:41:49.792400'), ('receiver', 'NodeMCU_1dsc000'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 264 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:49.907600'), ('function', 'set_connection_name'), ('message_id', '2017-01-30 18:41:49.907600'), ('receiver', 'NodeMCU_1dsc000'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 285 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:50.005000'), ('function', 'rename'), ('kwargs', {'name': 'neuron_x2'}), ('message_id', '2017-01-30 18:41:50.005000'), ('receiver', 'NodeMCU_f1d30800'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 265 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:50.079100'), ('function', 'set_connection_name'), ('message_id', '2017-01-30 18:41:50.079100'), ('receiver', 'NodeMCU_f1d30800'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 276 bytes
    Message:
    OrderedDict([('command', 'list connections by name'), ('correlation_id', '2017-01-30 18:41:52.147300'), ('message_id', '2017-01-30 18:41:52.147300'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'command')])
    
    
    Data received: 388 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.147300'), ('message_id', '2017-01-30 18:41:52.225300'), ('receiver', 'Client_366'), ('reply_to', 'Hub'), ('result', {'Client_366': "('192.168.0.100', 56066)", 'neuron_x1': "('192.168.0.104', 32406)", 'neuron_x2': "('192.168.0.103', 30406)"}), ('sender', 'Hub'), ('time_stamp', '2017-01-30 18:41:52.225300'), ('type', 'result')])
    
    
    [____________ Connected nodes ____________]
    
    
    Connected nodes:
    ['Client_366', 'neuron_x1', 'neuron_x2']
    
    

### 清空 log files


```python
# 清除所有 neurons 中的 logs  
emptyLogs()
```

    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.334500'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:52.334500'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.455100'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:52.455100'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    

### 設定 connections


```python
addConnection('neuron_x1', 'neuron_x2')
getConfig('neuron_x1')
```

    Sending 290 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.673700'), ('function', 'addConnection'), ('kwargs', {'neuron_id': 'neuron_x2'}), ('message_id', '2017-01-30 18:41:52.673700'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 269 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.751700'), ('function', 'getConfig'), ('message_id', '2017-01-30 18:41:52.751700'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 381 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:52.751700'), ('message_id', '20713'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('result', {'output': {'value': 0, 'polarized_time': 3745, 'lasting': 99.99997}, 'inputs': {}, 'connections': {'neuron_x2': 'neuron_x2'}}), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:41:53.323500'), ('type', 'result')])
    
    




    {'connections': {'neuron_x2': 'neuron_x2'},
     'inputs': {},
     'output': {'lasting': 99.99997, 'polarized_time': 3745, 'value': 0}}



### 設定 weights


```python
# hidden layer
setWeight('neuron_x2', 'neuron_x1', 1)  # 設定 neuron_x -> neuron_h1 的 weight = 1
```

    Sending 299 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:53.908900'), ('function', 'setWeight'), ('kwargs', {'weight': 1, 'neuron_id': 'neuron_x1'}), ('message_id', '2017-01-30 18:41:53.908900'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    

### 設定 thresholds


```python
# input layer 
setThreshold('neuron_x2', 0.9)
```

    Sending 281 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.138500'), ('function', 'setThreshold'), ('kwargs', {'threshold': 0.9}), ('message_id', '2017-01-30 18:41:54.138500'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    

### 模擬 sensor input，然後查看各 neurons 的 output 狀態
一個 neuron fire 之後，如果沒有持續的輸入可維持 fire 的狀態，則過 5 秒鐘之 neuron 的 output 一定為 0


```python
fire('neuron_x1')
```

    Sending 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.322700'), ('function', 'fire'), ('message_id', '2017-01-30 18:41:54.322700'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    


```python
### 模擬 sensor input，強迫 neuron x 或 y ouput 1
emptyLogs()  # 清除 logs
sleep(REFRACTORY_PERIOD)  # 等電位歸零 
mergeLogs()  # 彙整 logs
```

    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.504500'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:54.504500'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.573700'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:54.573700'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.723300'), ('function', 'getLog'), ('message_id', '2017-01-30 18:41:54.723300'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:54.723300'), ('message_id', '22677'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:41:55.063900'), ('type', 'result')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:55.141900'), ('function', 'getLog'), ('message_id', '2017-01-30 18:41:55.141900'), ('need_result', True), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 428 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:55.141900'), ('message_id', '24461'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x2'), ('result', [[24005, 'neuron_x2', 'neuron_x1 is kicking neuron_x2.'], [24211, 'neuron_x2', 'neuron_x2 fires.'], [24213, 'neuron_x2', 'Setting output of neuron_x2 to ACTION_POTENTIAL.']]), ('sender', 'neuron_x2'), ('time_stamp', '2017-01-30 18:41:55.504900'), ('type', 'result')])
    
    




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>neuron</th>
      <th>message</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24005</th>
      <td>neuron_x2</td>
      <td>neuron_x1 is kicking neuron_x2.</td>
    </tr>
    <tr>
      <th>24211</th>
      <td>neuron_x2</td>
      <td>neuron_x2 fires.</td>
    </tr>
    <tr>
      <th>24213</th>
      <td>neuron_x2</td>
      <td>Setting output of neuron_x2 to ACTION_POTENTIAL.</td>
    </tr>
  </tbody>
</table>
</div>




```python
### 模擬 sensor input，強迫 neuron x 或 y ouput 1
emptyLogs()  # 清除 logs
sleep(REFRACTORY_PERIOD)  # 等電位歸零
fire('neuron_x1') # force neuron x1 output 1 and fire.
mergeLogs()  # 彙整 logs
```

    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:56.279500'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:56.279500'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:56.372700'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:56.372700'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:56.545300'), ('function', 'fire'), ('message_id', '2017-01-30 18:41:56.545300'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:56.654500'), ('function', 'getLog'), ('message_id', '2017-01-30 18:41:56.654500'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 371 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:56.654500'), ('message_id', '24898'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('result', [[24803, 'neuron_x1', 'neuron_x1 fires.'], [24805, 'neuron_x1', 'Setting output of neuron_x1 to ACTION_POTENTIAL.']]), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:41:57.348300'), ('type', 'result')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:57.426300'), ('function', 'getLog'), ('message_id', '2017-01-30 18:41:57.426300'), ('need_result', True), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 428 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:57.426300'), ('message_id', '26743'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x2'), ('result', [[26329, 'neuron_x2', 'neuron_x1 is kicking neuron_x2.'], [26534, 'neuron_x2', 'neuron_x2 fires.'], [26537, 'neuron_x2', 'Setting output of neuron_x2 to ACTION_POTENTIAL.']]), ('sender', 'neuron_x2'), ('time_stamp', '2017-01-30 18:41:57.899500'), ('type', 'result')])
    
    




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>neuron</th>
      <th>message</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24803</th>
      <td>neuron_x1</td>
      <td>neuron_x1 fires.</td>
    </tr>
    <tr>
      <th>24805</th>
      <td>neuron_x1</td>
      <td>Setting output of neuron_x1 to ACTION_POTENTIAL.</td>
    </tr>
    <tr>
      <th>26329</th>
      <td>neuron_x2</td>
      <td>neuron_x1 is kicking neuron_x2.</td>
    </tr>
    <tr>
      <th>26534</th>
      <td>neuron_x2</td>
      <td>neuron_x2 fires.</td>
    </tr>
    <tr>
      <th>26537</th>
      <td>neuron_x2</td>
      <td>Setting output of neuron_x2 to ACTION_POTENTIAL.</td>
    </tr>
  </tbody>
</table>
</div>




```python
### 模擬 sensor input，強迫 neuron x 或 y ouput 1
emptyLogs()  # 清除 logs
sleep(REFRACTORY_PERIOD)  # 等電位歸零
fire('neuron_x2') # force neuron x2 output 1 and fire.
mergeLogs()  # 彙整 logs
```

    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:58.617100'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:58.617100'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:58.691100'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:41:58.691100'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:58.862700'), ('function', 'fire'), ('message_id', '2017-01-30 18:41:58.862700'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:58.925100'), ('function', 'getLog'), ('message_id', '2017-01-30 18:41:58.925100'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:41:58.925100'), ('message_id', '26964'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:41:59.488900'), ('type', 'result')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.121100'), ('function', 'getLog'), ('message_id', '2017-01-30 18:42:00.121100'), ('need_result', True), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 371 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.121100'), ('message_id', '29499'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x2'), ('result', [[28399, 'neuron_x2', 'neuron_x2 fires.'], [28402, 'neuron_x2', 'Setting output of neuron_x2 to ACTION_POTENTIAL.']]), ('sender', 'neuron_x2'), ('time_stamp', '2017-01-30 18:42:00.504700'), ('type', 'result')])
    
    




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>neuron</th>
      <th>message</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>28399</th>
      <td>neuron_x2</td>
      <td>neuron_x2 fires.</td>
    </tr>
    <tr>
      <th>28402</th>
      <td>neuron_x2</td>
      <td>Setting output of neuron_x2 to ACTION_POTENTIAL.</td>
    </tr>
  </tbody>
</table>
</div>




```python
### 模擬 sensor input，強迫 neuron x 或 y ouput 1
emptyLogs()  # 清除 logs
sleep(REFRACTORY_PERIOD)  # 等電位歸零
fire('neuron_x1') # force neuron x1 output 1 and fire.
fire('neuron_x2') # force neuron x2 output 1 and fire.
mergeLogs()  # 彙整 logs
```

    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.676300'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:42:00.676300'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 247 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.778900'), ('function', 'emptyLog'), ('message_id', '2017-01-30 18:42:00.778900'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.937700'), ('function', 'fire'), ('message_id', '2017-01-30 18:42:00.937700'), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 243 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:00.984500'), ('function', 'fire'), ('message_id', '2017-01-30 18:42:00.984500'), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:01.077500'), ('function', 'getLog'), ('message_id', '2017-01-30 18:42:01.077500'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 371 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:01.077500'), ('message_id', '29180'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('result', [[29084, 'neuron_x1', 'neuron_x1 fires.'], [29087, 'neuron_x1', 'Setting output of neuron_x1 to ACTION_POTENTIAL.']]), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:42:01.600900'), ('type', 'result')])
    
    Sending 266 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:01.725700'), ('function', 'getLog'), ('message_id', '2017-01-30 18:42:01.725700'), ('need_result', True), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 655 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:01.725700'), ('message_id', '31052'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x2'), ('result', [[30586, 'neuron_x2', 'neuron_x2 fires.'], [30588, 'neuron_x2', 'Setting output of neuron_x2 to ACTION_POTENTIAL.'], [30671, 'neuron_x2', 'neuron_x1 is kicking neuron_x2.'], [30676, 'neuron_x2', 'neuron_x2 is still in refractory-period.'], [30680, 'neuron_x2', 'neuron_x2 is still in refractory_period at action potential, then a neuron neuron_x1 kicks in, now sum_of_weighted_inputs >= threshold.']]), ('sender', 'neuron_x2'), ('time_stamp', '2017-01-30 18:42:02.339300'), ('type', 'result')])
    
    




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>neuron</th>
      <th>message</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>29084</th>
      <td>neuron_x1</td>
      <td>neuron_x1 fires.</td>
    </tr>
    <tr>
      <th>29087</th>
      <td>neuron_x1</td>
      <td>Setting output of neuron_x1 to ACTION_POTENTIAL.</td>
    </tr>
    <tr>
      <th>30586</th>
      <td>neuron_x2</td>
      <td>neuron_x2 fires.</td>
    </tr>
    <tr>
      <th>30588</th>
      <td>neuron_x2</td>
      <td>Setting output of neuron_x2 to ACTION_POTENTIAL.</td>
    </tr>
    <tr>
      <th>30671</th>
      <td>neuron_x2</td>
      <td>neuron_x1 is kicking neuron_x2.</td>
    </tr>
    <tr>
      <th>30676</th>
      <td>neuron_x2</td>
      <td>neuron_x2 is still in refractory-period.</td>
    </tr>
    <tr>
      <th>30680</th>
      <td>neuron_x2</td>
      <td>neuron_x2 is still in refractory_period at act...</td>
    </tr>
  </tbody>
</table>
</div>




```python
for neuron in reversed(neurons): printConfig(neuron)
```

    Sending 269 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:02.877900'), ('function', 'getConfig'), ('message_id', '2017-01-30 18:42:02.877900'), ('need_result', True), ('receiver', 'neuron_x2'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 455 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:02.877900'), ('message_id', '32233'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x2'), ('result', {'output': {'value': 1, 'polarized_time': 30589, 'lasting': 99.99997}, 'inputs': {'neuron_x1': {'value': 1, 'kick_time': 30672, 'lasting': 500.0}}, 'weights': {'neuron_x1': 1}, 'threshold': 0.8999998}), ('sender', 'neuron_x2'), ('time_stamp', '2017-01-30 18:42:03.366300'), ('type', 'result')])
    
    ______________________________neuron_x2 config:_______________________________
     {'output': {'value': 1, 'polarized_time': 30589, 'lasting': 99.99997}, 'inputs': {'neuron_x1': {'value': 1, 'kick_time': 30672, 'lasting': 500.0}}, 'weights': {'neuron_x1': 1}, 'threshold': 0.8999998}
    
    Sending 269 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:03.491100'), ('function', 'getConfig'), ('message_id', '2017-01-30 18:42:03.491100'), ('need_result', True), ('receiver', 'neuron_x1'), ('reply_to', 'Client_366'), ('sender', 'Client_366'), ('type', 'function')])
    
    
    Data received: 382 bytes
    Message:
    OrderedDict([('correlation_id', '2017-01-30 18:42:03.491100'), ('message_id', '31427'), ('receiver', 'Client_366'), ('reply_to', 'neuron_x1'), ('result', {'output': {'value': 1, 'polarized_time': 29087, 'lasting': 99.99997}, 'inputs': {}, 'connections': {'neuron_x2': 'neuron_x2'}}), ('sender', 'neuron_x1'), ('time_stamp', '2017-01-30 18:42:03.980900'), ('type', 'result')])
    
    ______________________________neuron_x1 config:_______________________________
     {'output': {'value': 1, 'polarized_time': 29087, 'lasting': 99.99997}, 'inputs': {}, 'connections': {'neuron_x2': 'neuron_x2'}}
    
    

### Stop the demo


```python
# Stopping
the_client.stop()
the_client = None
print ('\n[________________ Demo stopped ________________]\n')
```

    
    [________________ Demo stopped ________________]
    
    
