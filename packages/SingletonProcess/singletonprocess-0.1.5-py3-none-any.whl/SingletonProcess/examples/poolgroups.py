from SingletonProcess import SingletonProcess, block, terminateProcessesByPID
from time import sleep

class GroupA(SingletonProcess):
    poolgroup = "A"

class GroupB(SingletonProcess):
    poolgroup = "B"

@GroupA
def printListA(l: list):
    for item in l:
        print(item)
        sleep(1)

@GroupB
def printListB(l: list):
    for item in l:
        print(item)
        sleep(1)

if __name__ == "__main__":
    printListA([1, 2, 3, 4, 5, 6])
    printListB([10, 20, 30, 40, 50, 60])
    sleep(2.5)
    printListB(['a', 'b', 'c', 'd'])
    block(poolgroup='A')
    terminateProcessesByPID(pid=None,  poolgroup='B') #kills everytihng in B
    block()