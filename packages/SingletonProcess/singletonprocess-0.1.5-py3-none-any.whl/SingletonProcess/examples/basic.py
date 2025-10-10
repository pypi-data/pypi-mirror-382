from SingletonProcess import SingletonProcess, block
from time import sleep

def printListSlow(l: list):
    for item in l:
        print(item)
        sleep(1)

@SingletonProcess
def printListMP(l: list):
    for item in l:
        print(item)
        sleep(1)

if __name__ == "__main__":
    print("No Multiprocessing: ")
    printListSlow(['a', 'b', 'c'])
    printListSlow(['d', 'e', 'f'])

    print("\nWith multiprocessing: ")
    printListMP(['u', 'v', 'w'], pid='a')
    printListMP(['x', 'y', 'z'], pid='b')
    block()

    print("\nOverrides: ")
    printListMP(range(0, 10))
    sleep(1)
    printListMP(['a', 'b', 'c'])
    block()