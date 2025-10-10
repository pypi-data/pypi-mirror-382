from setuptools import setup, find_packages

setup(
    name="cli_timer",
    version="1.0.3",
    packages=find_packages(),
    install_requires=[
        "pynput",
        "termcolor",
        "pyTwistyScrambler"
    ],
    entry_points={
        "console_scripts": [
            "timer = cli_timer.main:main"
        ]
    }
)