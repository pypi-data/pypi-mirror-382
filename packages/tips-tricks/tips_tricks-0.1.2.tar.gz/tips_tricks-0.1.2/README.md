# Text File Character Counter

A command-line utility that reads a text file, counts the number of characters, and writes the result to an output file. It also logs actions and execution time using a custom decorator.

# Installation

pip install tips-tricks==0.1.1

# Usage

To run the program, use the following command:

python cli.py input.txt output.txt

input.txt — the name of the input text file
output.txt — the name of the output file where the result will be saved

Example:
python cli.py --input input.txt --output output.txt

## Virtual Environment

It is recommended to create a virtual environment before installing the package to avoid conflicts with global Python packages.

### Create and activate a virtual environment:

**On Windows:**

python -m venv .venv
.venv\Scripts\activate

**On macOS/Linux:**

python3 -m venv .venv
source .venv/bin/activate

