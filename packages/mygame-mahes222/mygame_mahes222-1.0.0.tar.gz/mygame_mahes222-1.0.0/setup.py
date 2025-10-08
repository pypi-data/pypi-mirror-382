from setuptools import setup, find_packages  # THIS LINE IS CRUCIAL

setup(
    name="mygame-mahes222",  # change to a unique name
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],  # add dependencies like ['pygame'] if needed
    entry_points={
        "console_scripts": [
            "play-game=mygame.main:main",
        ],
    },
    author="Mahes",
    description="A fun terminal-based Python game made by Mahes.",
    python_requires=">=3.7",
)

