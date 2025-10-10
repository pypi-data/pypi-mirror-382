import pathos.multiprocessing as multiprocessing
from pathos.helpers import mp as pathos_mp
from typing import List, Dict
import multiprocessing as mp
from multiprocessing.pool import MapResult
import dataclasses
from time import sleep

@dataclasses.dataclass
class PIDPool:
    """Used for tracking all active processes"""
    pid: str
    pool: multiprocessing.ProcessPool
    result: MapResult
    queue: mp.Queue

class ReturnObject:
    """Wrapper for MapResult to pull value from list"""
    def __init__(self, mapResult: MapResult):
        self.raw = mapResult

    def get(self, timeout = None, waitforready=False):
        if not self.raw.ready() and not waitforready:
            raise Exception("Attempting to get result of process that has not finished!")
        return self.raw.get(timeout=timeout)[0] #map returns a list

activepools: Dict[str, List[PIDPool]] = {'default': []}
idcounter = 0

def handleStdoutRedirect(queue):
    try:
        while not queue.empty():
            import sys
            i = queue.get()
            if not i[0]:
                sys.stdout.write(i[1])
            else:
                sys.stderr.write(i[1])
    except BrokenPipeError:
        pass #don't really know how to fix this... mostly happens during shutdowns so its probably fine

def cleanupDeadProcesses(poolgroup='default', verbose=False):
    """
    Removes all processes that have stoppped

    Returns True if removed at least one value
    """
    for i in range(len(activepools[poolgroup]) - 1, -1, -1):
        if activepools[poolgroup][i].result.ready():
            item = activepools[poolgroup].pop(i)
            if verbose:
                print("Removing terminated process with pid: <" + str(item.pid) + ">")
            if not item.result.successful():
                item.result.get() #This throws error back in main process
            handleStdoutRedirect(item.queue)



def block(pid = None, poolgroup = 'default', delay = 0.1, verbose=False):
    """Waits for all processes matching pid in poolgroup to exit, if pid is None, waits for all"""
    while True:
        sleep(delay)
        cleanupDeadProcesses(poolgroup, verbose)
        for item in activepools[poolgroup]:
            handleStdoutRedirect(item.queue)
            if item.pid == pid or pid is None:
                break
        else:
            break #drops out of loop


def terminateProcessesByPID(pid, poolgroup='default', verbose=False):
    """Terminates all processes that match pid, or all if None is provided."""
    cleanupDeadProcesses(poolgroup, verbose)
    for i in range(len(activepools[poolgroup]) -1, -1, -1):
        item = activepools[poolgroup][i]
        if item.pid == pid or pid is None or item.pid is None:
            if verbose:
                if pid is None:
                    reason = "terminating all processes."
                elif item.pid is None:
                    reason = "process did not have pid."
                else:
                    reason = "pid matched with terminate request."
                print("Terminating process with pid: <" + str(item.pid) + "> because", reason)
            handleStdoutRedirect(item.queue)
            item.pool.terminate()
            item.pool.join()
            activepools[poolgroup].pop(i)

class SingletonProcess:
    poolgroup = 'default'
    verbose = False

    def __init__(self, func):
        """Creates a singleton process from a function"""
        self.func = func
        activepools[self.poolgroup] = []

    @staticmethod
    def getPID(args, kwargs):
        """Looks for a pid kwarg in function call. This could be overridden for your use case"""
        _ = args
        if 'pid' in kwargs:
            return kwargs.pop('pid')
        else:
            return None

    def subwrapper(self, allargs):
        import sys
        def swrite(data):
            allargs[2].put((False, data))
        def ewrite(data):
            allargs[2].put((True, data))

        setattr(sys.stdout, 'write', swrite)
        setattr(sys.stderr, 'write', ewrite)
        return self.func(*allargs[0], **allargs[1])

    def __call__(self, *args, **kwargs):
        """Calls the function with given args, and terminates existing processes with matching ids"""
        global idcounter

        pid = self.getPID(args, kwargs)
        if self.verbose:
            print("Calling func", self.func.__name__, "with pid: <" + str(pid) + "> in a new process.")
        terminateProcessesByPID(pid, self.poolgroup, self.verbose)

        idcounter += 1
        queue = pathos_mp.Manager().Queue()
        pool = multiprocessing.ProcessPool(id=idcounter)
        result = pool.amap(self.subwrapper, [(args, kwargs, queue)])
        activepools[self.poolgroup].append(PIDPool(pid, pool, result, queue))
        return ReturnObject(result)

class VBSingletonProcess(SingletonProcess):
    """Verbose alternative to SingletonProcess, functionally identical"""
    verbose = True

class ThreadSafeSingletonProcess(SingletonProcess):
    """Forces use of spawn on linux instead of fork"""
    def __init__(self, func):
        mp.set_start_method("spawn", force=True)
        super().__init__(func)

class VBThreadSafeSingletonProcess(ThreadSafeSingletonProcess):
    """Verbose alternative to ThreadSafeSingletonProcess, functionally identical"""
    verbose = True