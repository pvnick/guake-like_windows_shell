# guake-like_windows_shell
A python script for toggling a cygwin/rxvt shell using F5

## How to use:
1. Install cygwin, including the rxvt terminal
2. You must have python installed on your system (Gwake is written for Python 2.7)
3. Install the ctypes python package
  * You can find an msi installer at http://sourceforge.net/projects/ctypes/files/?source=navbar
4. Install the PyWin32 package from http://sourceforge.net/projects/pywin32/files/pywin32/
5. Modify the appropriate settings in the gwake.conf
6. Launch using python gwake.py (or the included batch file, which runs the same command)
7. Use F5 to toggle the rxvt shell
