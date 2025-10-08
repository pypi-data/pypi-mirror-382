import signal
import sys


# Signal handling as early as practical
def signal_handler(sig, frame):
  print("ABORTING!")
  sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
