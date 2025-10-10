import sys
import os
import platform
import importlib.util
import subprocess
import glob
import shutil
import pkg_resources



def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources
   so_file = os.path.join(os.path.dirname(__file__),f"seekerdemo.cpython-312-linux.so")
   spec = importlib.util.spec_from_file_location("seekerdemo", so_file)
   mylib = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(mylib)

   
def copy_license_to_cwd():
   global __bootstrap__, __loader__, __file__
   # Get the path to the license file relative to your package
   license_file = pkg_resources.resource_filename(__name__, 'demolicense.sio')
   # Copy the file to the current directory
   if os.path.abspath(license_file) != os.path.abspath('./demolicense.sio'):
      shutil.copy(license_file, '.')

# First, copy the license file to the current working directory
copy_license_to_cwd()

# Then, load the shared library
__bootstrap__()
