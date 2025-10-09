from setuptools import setup, find_packages

setup(
    name="mygame_mahes222",
    version="1.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "play-game=mygame_mahes222.main:main",
        ],
    },
    author="Mahes",
    description="A fun terminal-based Python game made by Mahes.",
    python_requires=">=3.7",
)

