import os
import subprocess
import time

class Xvfb:
  def __init__(self, *args, width = 640, height = 480, color_depth = 8):
    self.cmd = ['/usr/bin/Xvfb']
    for arg in args:
      self.cmd.append(arg)
    self.cmd.extend(['-screen', '0'])
    self.cmd.append('%dx%dx%d' % (width, height, color_depth))

  def start(self):
    self.proc = subprocess.Popen(self.cmd,
                                 stdout = open(os.devnull),
                                 stderr = open(os.devnull))
    time.sleep(3)
    ret_code = self.proc.poll()
    if ret_code:
      print('Error: Xvfb did not start.')

  def stop(self):
    if self.proc is not None:
      self.proc.kill()
      self.proc.wait()
      self.proc = None