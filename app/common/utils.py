import subprocess

from psutil import process_iter


def get_lcu_process():
    for process in process_iter():
        if process.name() == 'LeagueClientUx.exe':
            yield process


def is_lcu_process_exist():
    processes = subprocess.check_output('tasklist /FI "imagename eq League of Legends.exe" /NH', shell=True)
    return b'League of Legends.exe' in processes


def get_lcu_pids():
    try:
        processes = subprocess.check_output(
            'tasklist /FI "imagename eq LeagueClientUx.exe" /NH',
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        raise e
    pids = []
    if not b'LeagueClientUx.exe' in processes:
        return pids

    arr = processes.split()
    for i, s in enumerate(arr):
        if s == b'LeagueClientUx.exe':
            pids.append(int(arr[i + 1]))
    return pids


def get_port_token(process):
    args = {}
    for cmdline_arg in process.cmdline():
        if len(cmdline_arg) > 0 and '=' in cmdline_arg:
            key, value = cmdline_arg[2:].split('=', 1)
            args[key] = value
    return args['app-port'], args['remoting-auth-token']
