import os
import sys
import ctypes
from ctypes import wintypes, byref, windll
import win32con
import win32gui
import win32api
import subprocess
import ConfigParser

class ShellController():
  def __init__(self, config_parser):
    self.config_parser = config_parser
    self.shell_hwnd = None
    self.shell_proc = None
    self.shell_is_open = False
    self.findwindow_title = "/tmp/this_window_name_is_unique"
    self.shell_executable_path = self.config_parser.get('Gwake', 'ShellExecutablePath')
    self.shell_font = self.config_parser.get('Gwake', 'ShellFont')
    self.cygwin_bin_path = self.config_parser.get('Gwake', 'CygwinBinPath')
    self.shell_open_command = [self.shell_executable_path, '-sl', '1500', '-fn', 
                               self.shell_font, '-bg', 'black', '-fg', 'grey', '-sr', '-e',
                               './bash.exe', '--rcfile', '/cygdrive/c/cygwin/home/pvnic_000/guake-like_windows_shell/broadcast-mywindow.sh']
    self.transparent_factor = 0.95
    self.shell_height = 500

  def show_shell(self):
    if not self.is_shell_proc_running():
      print "No shell found, openning a new instance"
      self._open_shell()

    self.set_transparency()
    screen_width = win32api.GetSystemMetrics(0)
    win32gui.ShowWindow(self.shell_hwnd, win32con.SW_SHOW)
    win32gui.SetWindowPos(self.shell_hwnd,
                          win32con.HWND_TOPMOST,  # placement-order handle
                          0,     # horizontal position
                          0,      # vertical position
                          screen_width,  # width
                          self.shell_height, # height
                          0)
    win32gui.SetForegroundWindow(self.shell_hwnd)
    win32gui.PostMessage(self.shell_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
    self.shell_is_open = True

  def hide_shell(self):
    win32gui.ShowWindow(self.shell_hwnd, win32con.SW_HIDE)
    self.shell_is_open = False

  def set_transparency(self):
    existing_bits = win32gui.GetWindowLong(self.shell_hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(self.shell_hwnd, win32con.GWL_EXSTYLE, existing_bits | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(self.shell_hwnd, 1, int(self.transparent_factor * 255), win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

  def toggle_shell(self):
    print("Toggling shell")
    if self.shell_is_open:
      self.hide_shell()
    else:
      self.show_shell()

  def is_shell_proc_running(self):
    if self.shell_proc is None:
        return False
    running = self.shell_proc.poll() is None
    return running

  def _open_shell(self):
    drive_letter = os.getcwd()[0]
    print("Executing command " + str(self.shell_open_command))
    self.shell_proc = subprocess.Popen(self.shell_open_command, 
                                       cwd=self.cygwin_bin_path,
                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
    self.shell_hwnd = 0
    while self.shell_hwnd == 0:
      print "finding window"
      self.shell_hwnd = win32gui.FindWindow(None, 
                                            self.findwindow_title)

class HotKeyListener:
  TOGGLE_SHELL_MESSAGE = 1

  def __init__(self, config_parser):
    self.toggle_shell_key = win32con.VK_F5
    self.config_parser = config_parser
    self.shell_controller = ShellController(self.config_parser)

  def _register_hotkey(self):
    print "Registering shell toggle hotkey, " + str(self.toggle_shell_key) + ", to message " + str(self.TOGGLE_SHELL_MESSAGE)
    success = windll.user32.RegisterHotKey(None, self.TOGGLE_SHELL_MESSAGE, None, self.toggle_shell_key)
    if not success:
      raise Exception("Could not register shell toggle hot key")

  def _unregister_hotkey(self):
    print "Unregistering shell toggle hotkey attached to message " + str(self.TOGGLE_SHELL_MESSAGE)
    success = windll.user32.UnregisterHotKey(None, self.TOGGLE_SHELL_MESSAGE)
    if not success:
      raise Exception("Could not unregister shell toggle hot key")

  def listen(self):
    try:
      self._register_hotkey()
      msg = wintypes.MSG()
      while windll.user32.GetMessageA(byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
          if msg.wParam == self.TOGGLE_SHELL_MESSAGE:
            self.shell_controller.toggle_shell()

        windll.user32.TranslateMessage(byref(msg))
        windll.user32.DispatchMessageA(byref(msg))
    except Exception as ex:
      print "Caught exception: " + str(ex)
    finally:
      self._unregister_hotkey()


if __name__ == "__main__":
  config_parser = ConfigParser.ConfigParser()
  config_file_path = "gwake.conf"
  config_parser.read(config_file_path)
  hotkey_listener = HotKeyListener(config_parser)
  hotkey_listener.listen()
