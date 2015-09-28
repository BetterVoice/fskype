from xvfbwrapper import Xvfb
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as et

class SkypOpenModule(object):
  def __init__(self, *args, **kwargs):
    self.displays = dict()
    self.paths = {
      'fs': kwargs.get('fs_path', '/usr/local/freeswitch'),
      'fs_src': kwargs.get('fs_src_path', '/usr/src/freeswitch')
      'mod': kwargs.get('mod_path', '/usr/local/freeswitch/skypopen'),
      'share': kwargs.get('share_path', '/usr/share/skype')
    }

  def __cleanup_interfaces__(self, config):
    names = self.__get_interface_names__(config)
    for key in self.displays.keys():
      if not key in names:
        self.displays[key].stop()

  def __create_interface__(self, config):
    name = config.attrib.get('name')
    # Create the symbolic link to the Skype executable.
    symlinks_dir = 'skype-clients-symlinks-dir'
    source_path = os.path.join(self.paths['mod'], symlinks_dir, 'skype')
    link_path = os.path.join(self.paths['mod'], symlinks_dir, name)
    if not os.path.exists(link_path):
      os.symlink(source_path, link_path)
    # Create the Skype configuration folder.
    config_dir = 'skype-clients-configuration-dir'
    config_path = os.path.join(self.paths['mod'], config_dir, name)
    if not os.path.exists(config_path):
      os.makedirs(config_path)
      # Copy necessary files into configuration folder.
      templates_path = os.path.join(self.paths['fs_src'], 'src', 'mod',
                                    'endpoints', 'mod_skypopen', 'configs',
                                    'skype-client-configuration-dir-template',
                                    'skypeclient01')
      for file in os.listdir(templates_path):
        if file.startswith('shared'):
          shutil.copy(file, config_path)
      shutil.copytree(os.path.join(templates_path, 'skypenameA'),
                      os.path.join(config_path, 'skypenameA'))

  def __create_interfaces__(self, config):
    for interface in config.iter('interface'):
      name = interface.attrib.get('name')
      if not self.displays.has_key(name):
        self.__create_interface__(interface)

  def __destroy_interfaces__(self):
    for key in self.displays.keys():
      # Remove the symbolic link to the Skype executable.
      symlinks_dir = 'skype-clients-symlinks-dir'
      link_path = os.path.join(self.paths['mod'], symlinks_dir, key)
      os.remove(link_path)
      # Remove the Skype configuration folder.
      config_dir = 'skype-clients-configuration-dir'
      config_path = os.path.join(self.paths['mod'], config_dir, key)
      shutil.rmtree(config_path)

  def __get_interface_names__(self, config):
    return [c.attrib.get('name') for c in config.iter('interface')]

  def __get_skype_cmd__(self, user, password, display_num, interface_name):
    # Pipe the user name and password to the Skype client.
    cmd = ['/bin/echo']
    cmd.append('\'%s' % user)
    cmd.append('%s\'' % password)
    cmd.append('|')
    # Set the virtual display to use.
    cmd.append('DISPLAY=%s' % display_num)
    # Set the Skype executable path.
    symlinks_dir = 'skype-clients-symlinks-dir'
    link_path = os.path.join(self.paths['mod'], symlinks_dir, interface_name)
    cmd.append(link_path)
    # Set the Skype configuration path.
    config_dir = 'skype-clients-configuration-dir'
    config_path = os.path.join(self.paths['mod'], config_dir, interface_name)
    cmd.append('--dbpath=%s' % config_path)
    # Tell Skype the login info will be piped.
    cmd.append('--pipelogin')

  def __start_skype__(self, config):
    for interface in config.iter('interface'):
      name = interface.attrib.get('name')
      if not self.displays.has_key(name):
        for param in interface.findall('param'):
          if param.attrib.get('name') == 'X11-display':
            display_num = param.attrib.get('value')
          elif param.attrib.get('name') == 'skype_user':
            skype_user = param.attrib.get('value')
          elif param.attrib.get('name') == 'skype_password':
            skype_password = param.attrib.get('value')
        # Start the virtual display.
        display = Xvfb(display_num, '-ac', '-nolisten', 'tcp')
        display.start()
        # Start the Skype client.
        subprocess.call(self.__get_skype_cmd__(skype_user, skype_password,
                                               display_num, name),
                        shell = True)
        self.displays.update({ name: display })
        time.sleep(7)

  def __stop_skype__(self):
    for key in self.displays.keys():
      self.displays[key].stop()

  def __write_fs_config__(self, config):
    path = os.path.join(self.paths['fs'], 'conf', 'autoload_configs',
                        'skypopen.conf.xml')
    with open(path, 'w') as output:
      output.write(config)

  def configure(self, xml):
    config = et.fromstring(xml).getroot()
    self.__cleanup_interfaces__(config)
    self.__create_interfaces__(config)
    self.__write_fs_config__(xml)
    self.__start_skype__()

  def shutdown(self):
    self.__stop_skype__()
    self.__destroy_interfaces__()
