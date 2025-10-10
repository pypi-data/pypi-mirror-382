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
        sleep(0.25)
        print("  Server running: ", hostname)


if __name__ == '__main__':
    startServer(hostname='https://examplea.com')
    sleep(0.1)
    startServer(hostname='https://exampleb.com')
    sleep(1)
    startServer(hostname='https://examplea.com')  # stops first server
    block()