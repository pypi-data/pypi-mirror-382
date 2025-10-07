# -*- coding: utf-8 -*-

import os
import time


class PidFile(object):
    def __init__(self, file=None, timeout=0, exit_code=0, raise_except=False):
        self.file = file
        self.timeout = timeout
        self.exit_code = exit_code
        self.raise_except = raise_except
        self.os_win = 1 if os.sep == '\\' else 0

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        self.unlock()

    def lock(self):
        if not self.file:
            return
        if os.path.exists(self.file):
            pid = 0
            with open(self.file, 'r') as f:
                pid = int(f.read())
            if pid:
                if self.os_win:
                    s = 'tasklist /FI "PID eq ' + str(pid) + '" | find " ' + str(pid) + ' "'
                else:
                    s = 'ps -ax | awk \'{print $1}\' | grep -e \"^' + str(pid) + '$\"'
                if os.popen(s).read():
                    c = 1
                    if self.timeout:
                        mtime = os.path.getmtime(self.file)
                        if time.time() - mtime > self.timeout:
                            if self.os_win:
                                s = 'taskkill /F /PID ' + str(pid)
                            else:
                                s = 'kill -9 ' + str(pid)
                            os.system(s)
                            c = 0
                    if c:
                        s = "Already running, pid: " + str(pid)
                        if self.raise_except:
                            raise Exception(s)
                        else:
                            print(s)
                            exit(self.exit_code)

                os.unlink(self.file)
        with open(self.file, 'w') as f:
            f.write(str(os.getpid()))

    def unlock(self):
        if not self.file:
            return
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                pid = int(f.read())
            if pid == os.getpid():
                os.unlink(self.file)

