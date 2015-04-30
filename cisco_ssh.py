import paramiko
import time
import os
import socket
import logging

class CiscoSSH:
    DELAY = 1 
    TIMEOUT = 3000
    BUFFER = 5000
    RETRIES = 5 

    def __init__(self, creds=None, ip=None, port=None, path_to_keys=None, logger=None):
        # need to add facility for username. password combos
        self.ip = ip
        self.port = port or 22
        self.creds = creds
        self.chan = None
        self.logger = logger or logging.getLogger(__name__)

        self.load_keys(path=path_to_keys)
#        self.authenticate()

    def __islist(self, x):
        return (type(x) is list) and x or []

    def load_keys(self, path=None):
        self.path = path or "~/.ssh/known_hosts"
        d = os.path.expanduser(self.path)

        if not os.path.exists(os.path.dirname(d)):
            os.makedirs(os.path.dirname(d))

        if not os.path.exists(d):
            open(d, 'a').close()
            
        paramiko.util.load_host_keys(d)

    def authenticate(self, pre_cmds=None):
        i = 0
        while True:
            try:
                print self.ip, self.port
                t = paramiko.Transport((self.ip, self.port))
                t.start_client()
                auth = t.auth_password(self.creds[i][0], self.creds[i][1])
            except paramiko.ssh_exception.AuthenticationException:
                i+=1
            except (socket.error, paramiko.ssh_exception.SSHException, IndexError) as e:
                return False, e
            else:
                break

        self.chan = t.open_session()
        self.chan.get_pty()
        self.chan.invoke_shell()
        self.chan.setblocking(0)
        self.chan.settimeout(8)

        if pre_cmds:
            self.send_cmd(pre_cmds)

        return True, self.creds[i][0]

    def collect_output(self):
        _buf = ""
        for i in range(CiscoSSH.RETRIES):
            time.sleep(CiscoSSH.DELAY)
            while self.chan.recv_ready():
                    _buf += self.chan.recv(CiscoSSH.BUFFER)
        return _buf

    def send_cmd(self, cmds=None):
        cmds = self.__islist(cmds)
        buf = ""

        buf += self.collect_output()

        for cmd in cmds:
            self.chan.send(cmd + "\n")
            buf += self.collect_output()

        return buf
