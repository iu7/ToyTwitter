import time
import datetime

__write_to_console__ = True

def getTime():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')

def getData():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

class Logger:
    # should be async
    def write(self, message, level=0):
        lstr = "MESSAGE"
        if level == 1:
            lstr = "\033[93mWARNING\033[0m"
        elif level == 2:
            lstr = "\033[91mERROR\033[0m"
        
        msg = "[\033[92m{user}\033[0m] {time} {level}: {msg}".format(user=self.user, time=getTime(), level=lstr, msg=message)

        if self.writeToConslole:
            print msg
        else:
            self.fd.write(msg + "\n")
    
    # fn, user are strings
    def __init__(self, fn, user, writeToConslole=__write_to_console__):
        
        if not writeToConslole:
            assert fn is not None, "Logger recieved null insteat of file name"
        
        self.writeToConslole = writeToConslole
        self.fd = open(fn, 'a')
        self.user = user

        self.write("Started new logger session {data}".format(data=getData()))

    
if __name__ == '__main__':
    myclass = Logger("logger_log.txt", "logger")
    # test
    myclass.write("Simple message", 0)
    myclass.write("Warning message", 1)
    myclass.write("Error message", 2)