from __future__ import print_function
import sys
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    INSTALL_REQUIRES = [l.strip() for l in f.readlines() if l]


try:
    import numpy
except ImportError:
    print('numpy is required during installation')
    sys.exit(1)

try:
    import scipy
except ImportError:
    print('scipy is required during installation')
    sys.exit(1)

setup(name='rbclassifier',
      version='0.9',
      description='Feature relevance interval method',
      author='Lukas Pfannschmidt',
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      author_email='lpfannschmidt@techfak.uni-bielefeld.de',
      )
