import os
import platform
import signal
import socket
import subprocess
import time

import pytest


def spawn_process(command: list[str]) -> subprocess.Popen:
    if platform.system() == 'Windows':
        command[0] = 'python'
        process = subprocess.Popen(
            command, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        return process
    process = subprocess.Popen(command, preexec_fn=os.setsid)
    return process


def kill_process(process: subprocess.Popen) -> None:
    if platform.system() == 'Windows':
        process.send_signal(signal.CTRL_BREAK_EVENT)
        process.kill()
        return

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def start_server(domain: str, port: int) -> subprocess.Popen:
    """
    Call this method to wait for the server to start
    """
    # Start the server
    command = [
        'velithon',
        'run',
        '--app',
        'tests.app.server:app',
        '--host',
        domain,
        '--port',
        str(port),
    ]
    process = spawn_process(command)

    # Wait for the server to be reachable
    timeout = 5  # The maximum time we will wait for an answer
    start_time = time.time()
    while True:
        current_time = time.time()
        if current_time - start_time > timeout:
            # didn't start correctly before timeout, kill the process and exit with an exception
            kill_process(process)
            raise ConnectionError('Could not reach server')
        try:
            sock = socket.create_connection((domain, port), timeout=5)
            sock.close()
            break  # We were able to reach the server, exit the loop
        except Exception:
            pass
    return process


@pytest.fixture(scope='session')
def session():
    domain = '127.0.0.1'
    port = 5005
    process = start_server(domain, port)
    yield
    kill_process(process)
