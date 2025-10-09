import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

from fastpusher import __version__

# Package meta-data.
NAME = "fastpusher"
DESCRIPTION = "A simple FastAPI factory for creating FastAPI applications."
URL = "https://github.com/fastpusheruz/fastpusher_client"
EMAIL = "fastpusheruz@gmail.com"
AUTHOR = "FastPusher devs"
REQUIRES_PYTHON = ">=3.9.0"
VERSION = __version__

# What packages are required for this module to be executed?
REQUIRED = [
    "click==8.1.8",
    "fastapi[all]==0.115.8",
    "uvicorn[standard]==0.34.0",
    "alembic==1.14.1",
    "sqlalchemy[asyncio]==2.0.38",
    "passlib==1.7.4",
    "requests==2.32.3",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()


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

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

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
        "Bug Reports": "https://github.com/fastpusheruz/fastpusher/issues",
        "Source": "https://github.com/fastpusheruz/fastpusher",
        "Documentation": "https://github.com/fastpusheruz/fastpusher/wiki",
    },
    # $ setup.py upload support.
    cmdclass={
        "upload": UploadCommand,
        "testupload": TestUploadCommand,
    },
)
