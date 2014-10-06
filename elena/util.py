from config import DEBUG

def debug(msg):
    if DEBUG:
        print("[DEBUG]: " + msg)

