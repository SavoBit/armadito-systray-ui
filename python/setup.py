#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# to combine autotools and setuptools, see:
# https://blog.kevin-brown.com/programming/2014/09/24/combining-autotools-and-setuptools.html
# Thank you!

import os
import shutil
import stat
from setuptools import setup
from setuptools.command.install import install as _install
#from babel.messages import frontend as babel

def do_install_file(file, install_dir):
    print("Installing %s in %s..." % (file, install_dir))
    try:
        os.makedirs(install_dir, mode = 0o755, exist_ok = True)
    except OSError:
        print("WARNING: cannot create directory %s" % install_dir)
        return
    try:
        shutil.copy(file, install_dir)
    except IOError:
        print("WARNING: cannot copy file %s" % (file,))
    mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
    try:
        base_file = os.path.basename(file)
        os.chmod(install_dir + '/' + base_file, mode)
    except IOError:
        print("WARNING: cannot chmod %s" % (base_file,))

def do_edit_file(in_file, out_file, from_str, to_str):
    in_content = open(in_file).read()
    out_content = in_content.replace(from_str, to_str)
    open(out_file, 'w').write(out_content)
    
class install(_install):
    def run(self):
        _install.run(self)
        do_edit_file('bin/indicator-armadito.in', 'bin/indicator-armadito', '@PREFIX@', self.prefix)
        do_install_file('bin/indicator-armadito', self.prefix + '/bin')
        print("Done!")

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name = "Armadito antivirus indicator",
    version = "0.10.0",
    author = "François Déchelle",
    author_email = "fdechelle@teclib.com",
    description = ("Application indicator for the Armadito antivirus"),
    license = "GPLv3",
    keywords = "antivirus indicator",
    url = "https://github.com/armadito/armadito-systray-ui",
    long_description = read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3 License",
    ],
    packages = ['armadito'],
    scripts = ['bin/indicator-armadito'],
    data_files = [('share/icons/hicolor/scalable/apps', [
        'icons/scalable/indicator-armadito-dark.svg',
        'icons/scalable/indicator-armadito-desactive.svg',
        'icons/scalable/indicator-armadito-down.svg',
        'icons/scalable/indicator-armadito-missing.svg',
        'icons/scalable/indicator-armadito.svg'])],
#    cmdclass = {"install": install}
)

#
#
# reminder: for user local installation
# ./setup.py install --user
# ./setup.py install_data --install-dir=/home/fdechelle/.local
#
#
