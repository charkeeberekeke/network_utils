#!/usr/bin/env python

import paramiko
import time
import os
import socket

islist = lambda x: (type(x) is list) and x or []


def load_keys(path="~/.ssh/known_hosts"):
    d = os.path.expanduser(path)

    if not os.path.exists(os.path.dirname(d)):
        os.makedirs(os.path.dirname(d))

    if not os.path.exists(d):
        open(d, 'a').close()
        
    paramiko.util.load_host_keys(d)

def ssh(ip, port=22, creds=None, pre_cmds=None, cmds=None):
    """
    Function for ssh'ing into a device using paramiko
    """

    i = 0
    pre_cmds = islist(pre_cmds)
    cmds = islist(cmds)

    # Cycle throu list of username/password tuples
    while True:
        try:
            t = paramiko.Transport((ip, port))
            t.start_client()
            auth = t.auth_password(creds[i][0], creds[i][1])
        except paramiko.ssh_exception.AuthenticationException:
            i+=1
        except (socket.error, paramiko.ssh_exception.SSHException) as e:
            return False, e
        else:
            break

    # launch shell
    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    chan.setblocking(0)
    chan.settimeout(8)

    buf = ""

    # send pre_cmds and cmds to device
    chan, buf = send_cmd(chan, pre_cmds)
    chan, buf = send_cmd(chan, cmds)

    chan.close()
    t.close()

    return True, buf

def send_cmd(chan, cmds=None, delay=1, buf_size=1000):
    """
    Send a list of commands to device.
    Function will attach a newline to each command.
    """
    cmds = islist(cmds)
    buf = ""
    for cmd in cmds:
        chan.send(cmd + "\n")
        time.sleep(delay)
        while chan.recv_ready():
            time.sleep(delay)
            buf += chan.recv(buf_size)

    return chan, buf 

def scp(ip, port=22, creds=None, src=None, dst=None):
    i = 0
    while True:
        try:
            t = paramiko.Transport((ip, port))
            t.connect(username=creds[i][0], password=creds[i][1])
        except paramiko.ssh_exception.AuthenticationException:
            i+=1
        except (socket.error, paramiko.ssh_exception.SSHException) as e:
            return False, e
        else:
            break
