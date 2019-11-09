# systemcall.py
#
# Module for running system commands

import threading
import logging
import os
import signal
import subprocess

class SystemCallError(Exception): pass
class SystemCallTimeout(Exception): pass


class SystemCallResult(object):
    def __init__(self, command, returncode, stdout, stderr):
        self.command = command
        self.returncode = returncode
        self.bytes_stdout = stdout
        self.bytes_stderr = stderr

    def stdout(self, encoding='utf8'):
        return self.bytes_stdout.decode(encoding)

    def stderr(self, encoding='utf8'):
        return self.bytes_stdout.decode(encoding)

    def __str__(self):
        if self.bytes_stdout:
            return str(self.bytes_stdout)
        else:
            return ''

    def __repr__(self):
        this = {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.bytes_stdout,
            "stderr": self.bytes_stderr
        }
        return repr(this)


def systemcall(command, timeout=9999999, success_codes=[0]):
    def kill_process(process):
        os.kill(process.pid, signal.SIGTERM)

    logging.info((
        f'System command: {command}, timeout: {timeout}, '
        f'success_codes: {success_codes}'
    ))
    process = subprocess.Popen(
        args = command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        shell = True
    )

    t = threading.Timer(timeout, kill_process, [process])
    t.start()

    process.wait()

    if not t.isAlive():
        raise SystemCallTimeout(
            f'Command timed out after running for {timeout} seconds.'
        )
    elif t.isAlive():
        t.cancel()

    stdout = b''.join(process.stdout.readlines())
    stderr = b''.join(process.stderr.readlines())
    returncode = process.returncode

    if returncode not in success_codes:
        logging.info(
            f'status: {returncode}, stdout: {stdout}, stderr: {stderr}'
        )
        raise SystemCallError(
            f'status: {returncode}, stdout: {stdout}, stderr: {stderr}'
        )

    result = SystemCallResult(
        command,
        returncode,
        stdout.strip(),
        stderr.strip()
    )

    return result
