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