#!/usr/bin/python

from distutils.core import setup

setup(name = 'ubuntustudio-controls',
  version = '0.1',
  author = 'Ubuntu Studio Development Team',
  author_email = 'ubuntu-studio-devel@lists.ubuntu.com',
  url = 'https://wiki.ubuntu.com/UbuntuStudio/SettingsApp',
  license = 'GPL v2',
  package_dir = {'':'src'},
  py_modules = ['changesettings', 'meminfo_total'],
  scripts = ['src/ubuntustudio-controls'],
  data_files = [('share/ubuntustudio-controls', ['src/gui.glade', 'src/ubuntustudio-controls.svg'])],
  classifiers = ['License :: OSI Approved :: GNU General Public License (GPL)'])

