"""
main.py — entry point.

Starts the screen capture thread (capture.py) then hands the main thread
over to the interactive command CLI (commands.py).
"""

import os
import threading
import psutil

import state
import config
import commands  # importing this file registers all @command decorators
from capture import capture_loop


def main():
    # Depress process priority so the game always gets CPU first
    psutil.Process(os.getpid()).nice(psutil.IDLE_PRIORITY_CLASS)

    # Start screen capture in the background
    thread = threading.Thread(target=capture_loop, name="capture", daemon=True)
    thread.start()

    print(f"ESP32 Ambient Lighting  →  {config.ESP32_IP}:{config.PORT}")
    print(f"Capture running at {config.FRAME_RATE} FPS  |  IDLE priority")
    print("Type 'help' for commands, 'quit' to exit.\n")

    # Hand the main thread over to the command CLI
    while True:
        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not commands.dispatch(raw):
            break

    # Signal the capture thread to exit, then close the socket
    state.stop.set()
    state.sock.close()
    print("Goodbye.")


if __name__ == "__main__":
    main()
