from setuptools import setup, find_packages


setup(
    name='QGISLibrary',
    version='1.7.5',
    packages=find_packages(),
    install_requires=['robotframework', 'pywinauto', 'PyAutoGUI', 'pillow'],
)