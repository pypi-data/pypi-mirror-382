from SingletonProcess import SingletonProcess, block
import multiprocessing as mp
from time import sleep

@SingletonProcess
def complicatedOperation(l: list):
    r = []
    for i in range(len(l) - 1, - 1, -1):
        r.append(l[i])
    return r

if __name__ == "__main__":
    ret = complicatedOperation(['u', 'v', 'w'])
    block()
    print(ret.get())