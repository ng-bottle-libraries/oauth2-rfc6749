from setuptools import setup, find_packages
from rfc6749 import __version__, __author__

if __name__ == '__main__':
    project_name = 'rfc6749'
    setup(name=project_name,
          version=__version__,
          author=__author__,
          package_dir={project_name: project_name},
          license='MIT',
          packages=find_packages())
