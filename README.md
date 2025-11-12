PhantomPort — toy server + scanner + GUI
=======================================

Purpose:
- Educational. Use only on your own machines or test VMs.

Run server (terminal):
$ python3 phantomport.py server

Run scanner (terminal):
$ python3 phantomport.py scan 127.0.0.1 1-1024 40

Run GUI:
$ python3 gui.py

Package to exe (optional, Windows):
$ pip install pyinstaller
$ pyinstaller --onefile phantomport.py
# or for GUI: pyinstaller --onefile gui.py

Safety:
- Do NOT scan or test other people's systems without permission.
