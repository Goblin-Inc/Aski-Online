#!/usr/bin/python3
import os, sys
try:
    import PyQt6
except ImportError:
    if os.path.exists("/usr/bin/python3") and os.path.realpath(sys.executable) != os.path.realpath("/usr/bin/python3"):
        os.execv("/usr/bin/python3", ["/usr/bin/python3", *sys.argv])
from app.application import Application


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()