import os
from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="tritium-remote-py",
    version=read("VERSION").strip(),
    description="Tritium remote interaction.",
    long_description=read("README.rst"),
    license="GPL",
    keywords="tritium robotics",
    url="http://wiki.engineeredarts.co.uk/tritium",
    author="Engineered Arts Ltd",
    author_email="tritium@engineeredarts.co.uk",
    install_requires=["websockets>=15,<16"],
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Environment :: No Input/Output (Daemon)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Framework :: Robot Framework :: Library",
    ],
    setup_requires=["setuptools"],
)
