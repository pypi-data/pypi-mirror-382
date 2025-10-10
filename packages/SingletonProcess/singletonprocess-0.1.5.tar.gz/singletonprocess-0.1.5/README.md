# SingletonProcess

![Tests Badge](https://github.com/RobertJN64/SingletonProcess/actions/workflows/tests.yml/badge.svg)
![Python Version Badge](https://img.shields.io/pypi/pyversions/SingletonProcess)
![License Badge](https://img.shields.io/github/license/RobertJN64/SingletonProcess)

A SingletonProcess is a function that is run in a seperate process and
only one exists at a time. This is useful for use facing functions that must
run in the background and need to be shutdown automatically.

**Always guard your code with `if __name__ == '__main__'` or multiprocessing will fail.**

Note: This module handles one specific use case very well.
In high performance applications or different use cases,
you may be better off with a custom
solution.

## Examples

See [examples](/SingletonProcess/examples) for more examples.

Run two processes simultaneously (notice the unique process ID)

```python
from SingletonProcess import SingletonProcess, block
from time import sleep

@SingletonProcess
def longComputation(x):
    sleep(5)
    return x ** 2

if __name__ == '__main__':
    a = longComputation(1, pid='a')
    b = longComputation(2, pid='b')
    block()
    print(a, b)
```

Stop new process automatically (notice pid=None, which acts as a wildcard
and stops all processes)

```python
from SingletonProcess import SingletonProcess, block

@SingletonProcess
def uniqueProcess():
    while True:
        print("Doing important stuff!")

if __name__ == '__main__':
    uniqueProcess()
    uniqueProcess() #stops execution of first process
    block()
```

Use ```VBSingletonProcess``` and ```verbose = True``` to see
detailed info about internal proccesses.

```python
from SingletonProcess import VBSingletonProcess, block, terminateProcessesByPID
from time import sleep

@VBSingletonProcess
def printList(l: list):
    for item in l:
        print(item)
        sleep(1)

if __name__ == "__main__":
    printList([1, 2, 3, 4, 5, 6], pid='a')
    printList([10, 20, 30, 40, 50, 60], pid='b')
    sleep(2.5)
    printList(['a', 'b', 'c', 'd'])
    sleep(2.5)
    printList(['hello', 'hello', 'world', 'world'], pid='c')
    sleep(2.5)
    printList(['so', 'long', 'and', 'thanks', 'for', 'all', 'the', 'fish'], pid='c')
    printList(range(0,100), pid='d')
    block(pid='c', verbose=True)
    terminateProcessesByPID(pid='d', verbose=True)
    block(verbose=True)
```

Use different poolgroups to seperate out different types of tasks.

```python
from SingletonProcess import SingletonProcess, block

class GroupA(SingletonProcess):
    poolgroup = 'A'
    
class GroupB(SingletonProcess):
    poolgroup = 'B'

@GroupA
def uniqueProcessA():
    while True:
        print("Doing important stuff!")
        
@GroupB
def uniqueProcessB():
    while True:
        print("Doing other important stuff!")

if __name__ == '__main__':
    uniqueProcessA()
    uniqueProcessB() #first process still runs
    block(poolgroup='A')
    block(poolgroup='B')
```

You can also override the `getPID` class method for custom use cases.
```python
from SingletonProcess import SingletonProcess, block
from time import sleep

class SafeServer(SingletonProcess):
    @staticmethod
    def getPID(args, kwargs):
        return kwargs['hostname']
    
@SafeServer
def startServer(hostname):
    print("Starting server on hostname: ", hostname)
    while True:
        pass

if __name__ == '__main__':
    startServer(hostname='https://examplea.com')
    startServer(hostname='https://exampleb.com')
    sleep(1)
    startServer(hostname='https://examplea.com') #stops first server
    block()
```

## ThreadSafeSingletonProcess

Uses spawn instead of fork on linux, which may work better for projects that also use threads.