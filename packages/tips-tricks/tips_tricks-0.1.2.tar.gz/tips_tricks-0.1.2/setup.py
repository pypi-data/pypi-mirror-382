from setuptools import setup, find_packages

setup(
    name="tips-tricks",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "tips-cli = app.cli:main",
        ]
    },
    author="Katsiaryna Shymko",
    description="CLI tool for processing text files and counting characters",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
