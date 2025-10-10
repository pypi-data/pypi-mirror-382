import SingletonProcess as project
from SingletonProcess import VBSingletonProcess, SingletonProcess
from SingletonProcess import VBThreadSafeSingletonProcess, ThreadSafeSingletonProcess
from time import sleep, time
import pytest

@SingletonProcess
def loop(upper, lower):
    l = []
    for i in range(upper, lower):
        l.append([i, time()])
        sleep(1)
    return l

@VBSingletonProcess
def vbloop(upper, lower):
    l = []
    for i in range(upper, lower):
        l.append([i, time()])
        sleep(1)
    return l

class GroupA(SingletonProcess):
    poolgroup = 'A'

@GroupA
def groupALoop(upper, lower):
    l = []
    for i in range(upper, lower):
        l.append([i, time()])
        sleep(1)
    return l

#all these tests are based on the
def test_basic():
    a = loop(5, 10, pid='a')
    sleep(0.5)
    b = loop(15, 20, pid='b')
    project.block(pid='c')
    assert not a.raw.ready()
    assert not b.raw.ready()
    project.block()

    assert len(a.get()) == len(b.get())
    for item in zip(a.get(), b.get()):
        assert item[0] < item[1] #process order was the same

def test_vbbasic():
    a = vbloop(5, 10, pid='a')
    sleep(0.5)
    b = vbloop(15, 20, pid='b')
    project.block(verbose=True)

    assert len(a.get()) == len(b.get())
    for item in zip(a.get(), b.get()):
        assert item[0] < item[1] #process order was the same

def test_none_pid():
    a = loop(5, 10)
    sleep(0.5)
    b = loop(15, 20)
    project.block()

    assert not a.raw.ready()
    assert len(b.get()) == 5

def test_terminate():
    a = loop(5,10, pid='a')
    project.terminateProcessesByPID(pid=None)
    assert not a.raw.ready()
    b = loop(5,10, pid='b')
    c = loop(5,10, pid='c')
    project.terminateProcessesByPID(pid='c')
    assert not c.raw.ready()
    project.block(pid='b')
    assert len(b.get()) == 5

def test_vbterminate():
    a = vbloop(5, 10, pid='a')
    project.terminateProcessesByPID(pid=None, verbose=True)
    assert not a.raw.ready()
    b = vbloop(5, 10, pid='b')
    c = vbloop(5, 10, pid='c')
    project.terminateProcessesByPID(pid='c', verbose=True)
    assert not c.raw.ready()
    project.block(pid='b', verbose=True)
    assert len(b.get()) == 5
    d = vbloop(5, 10)
    project.terminateProcessesByPID(pid='c', verbose=True)
    assert not d.raw.ready()

def test_nondefaultpools():
    a = groupALoop(5,10, pid='a')
    b = loop(5, 15, pid = 'a')
    project.block(poolgroup='A')
    assert a.raw.ready()
    assert not b.raw.ready()
    project.block()
    assert b.raw.ready()

def test_error():
    with pytest.raises(Exception):
        a = loop(5, 10)
        a.get()

@SingletonProcess
def mp_error():
    raise Exception("Help this is an intentional error!")

def test_mp_error():
    with pytest.raises(Exception):
        mp_error()
        project.block()

@ThreadSafeSingletonProcess
def print_x():
    print("x")

@VBThreadSafeSingletonProcess
def print_y():
    print("y")

def test_threadsafe(capture_stdout):
    print_x()
    project.block()
    assert capture_stdout['stdout'] == 'x\n'
    print_y()
