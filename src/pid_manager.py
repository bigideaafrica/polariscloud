# src/pid_manager.py

import os
import signal
import sys

import pid

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polaris.pid')

def create_pid_file():
    try:
        pidfile = pid.PidFile(pidname='polaris-cli-tool', piddir=os.path.dirname(PID_FILE))
        return pidfile
    except pid.PidFileAlreadyRunningError:
        print("Polaris CLI Tool is already running.")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating PID file: {e}")
        sys.exit(1)

def remove_pid_file():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        print(f"Error removing PID file: {e}")
