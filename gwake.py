import os
import sys
import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api
import subprocess

def show_shell():
  global shell_hwnd
  screen_width = win32api.GetSystemMetrics(0)
  set_transparency()
  win32gui.ShowWindow(shell_hwnd, win32con.SW_SHOW)
  win32gui.SetWindowPos(shell_hwnd,
                        win32con.HWND_TOPMOST,  # placement-order handle
                        0,     # horizontal position
                        0,      # vertical position
                        screen_width,  # width
                        500, # height
                        0)
  win32gui.SetForegroundWindow(shell_hwnd)
  win32gui.PostMessage(shell_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)

def hide_shell():
  global shell_hwnd
  win32gui.ShowWindow(shell_hwnd, win32con.SW_HIDE)

def set_transparency():
  global shell_hwnd
  transparent_factor = 0.95
  existing_bits = win32gui.GetWindowLong(shell_hwnd, win32con.GWL_EXSTYLE)
  win32gui.SetWindowLong(shell_hwnd, win32con.GWL_EXSTYLE, existing_bits | win32con.WS_EX_LAYERED)
  win32gui.SetLayeredWindowAttributes(shell_hwnd, 1, int(transparent_factor * 255), win32con.LWA_COLORKEY | win32con.LWA_ALPHA)

def toggle_shell():
  print("Toggling shell")
  global shell_is_open, shell_hwnd, shell_proc
  if not is_shell_proc_running():
    open_shell()
    show_shell()
    shell_is_open = True
  elif shell_is_open:
    hide_shell()
    shell_is_open = False
  else:
    show_shell()
    shell_is_open = True

def is_shell_proc_running():
  global shell_proc
  if shell_proc is None:
      return False
  return shell_proc.poll() is None

def open_shell():
  global shell_hwnd, shell_proc
  drive_letter = os.getcwd()[0]
  shell_open_command = [drive_letter + ':\\cygwin\\bin\\rxvt.exe', '-sl', '1500', '-fn', 
                        'Lucida Console-12', '-bg', 'black', '-fg', 'grey', '-sr', '-e',
                        './bash.exe', '--rcfile', '/cygdrive/' + drive_letter + '/win_env/broadcast-mywindow.sh']
  shell_proc = subprocess.Popen(shell_open_command, cwd=drive_letter + ':\\cygwin\\bin\\')
  shell_hwnd = 0
  while shell_hwnd == 0:
    shell_hwnd = win32gui.FindWindow(None, findwindow_rxvt_title)

shell_is_open = False
findwindow_rxvt_title = "/tmp/this_window_name_is_unique"

byref = ctypes.byref
user32 = ctypes.windll.user32
HOTKEY_ACTION_TOGGLE_SHELL = 1
HOTKEYS = {
  HOTKEY_ACTION_TOGGLE_SHELL : win32con.VK_F5
}
shell_proc = None
shell_hwnd = 0

print("Waiting for shell toggle hotkey")

for id, vk in HOTKEYS.items ():
  print "Registering id", id, "for key", vk
  if not user32.RegisterHotKey (None, id, None, vk):
    print "Unable to register id", id

try:
  msg = wintypes.MSG ()
  while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
    if msg.message == win32con.WM_HOTKEY:
      if msg.wParam == HOTKEY_ACTION_TOGGLE_SHELL:
        toggle_shell()

    user32.TranslateMessage (byref (msg))
    user32.DispatchMessageA (byref (msg))

finally:
  for id in HOTKEYS.keys ():
    user32.UnregisterHotKey (None, id)


