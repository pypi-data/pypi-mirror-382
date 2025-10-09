import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

from fastpusher import __version__

# Package meta-data.
NAME = "fastpusher"
DESCRIPTION = "A fast and efficient push notification library"
URL = "https://github.com/fastpusheruz/fastpusher"
EMAIL = "fastpusheruz@gmail.com"
AUTHOR = "FastPusherUZ"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = __version__

# What packages are required for this module to be executed?
REQUIRED = [
    "requests>=2.25.0",
]

# What packages are optional?
EXTRAS = {
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
        "black>=21.0.0",
        "flake8>=3.8.0",
    ],
    "publishing": [
        "setuptools>=61.0",
        "wheel>=0.37.0",
        "twine>=4.0.0",
        "build>=0.8.0",
    ],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's version
about = {"__version__": VERSION}


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel distribution…")
        os.system("{0} -m build".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


class TestUploadCommand(Command):
    """Support setup.py testupload."""

    description = "Build and publish the package to Test PyPI."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel distribution…")
        os.system("{0} -m build".format(sys.executable))

        self.status("Uploading the package to Test PyPI via Twine…")
        os.system("twine upload --repository testpypi dist/*")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    author=AUTHOR,
    author_email=EMAIL,
    license="MIT",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="push notification messaging api rest",
    project_urls={
        "Bug Reports": "https://github.com/fastpusheruz/fastpusher_client/issues",
        "Source": "https://github.com/fastpusheruz/fastpusher_client",
        "Documentation": "https://github.com/fastpusheruz/fastpusher_client/wiki",
    },
    cmdclass={
        "upload": UploadCommand,
        "testupload": TestUploadCommand,
    },
)
