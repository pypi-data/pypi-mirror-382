from setuptools import setup, find_packages

setup(
    name="python_snake_game",
    version="1.0.4",
    description="A simple Snake game written in Python for the command-line interface (CLI). Control the snake with arrow keys, eat food to grow, and avoid running into yourself. Built entirely with Python's standard libraries-no third-party packages required.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="ramimK0bir",
    author_email="kobirbiddut81@gmail.com" ,  
    packages=find_packages() ,
    python_requires='>=3.7',

    classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "License :: OSI Approved :: MIT License",
],
)
