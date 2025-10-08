"""
This module provides a command-line tool that reads a text file, counts number of characters,
and outputs the result to another file.
"""

import argparse
import logging
import os.path

from app.decorators import log

@log
def main():
    """
    Command-line tool that reads a text file, counts number of characters in text file,
    and outputs the result to another file.
    """
    logging.basicConfig(
        filename="logs",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Takes file an reads it")
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Path to the source text file")
    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Path to the destination file")

    args = parser.parse_args()
    SOURCE_FILE_NAME = args.input
    DESTINATION_FILE_NAME = args.output

    logger = logging.getLogger("main")

    if not os.path.exists(SOURCE_FILE_NAME):
        print("File does not exist")
        logger.error("File does not exist: %s", SOURCE_FILE_NAME)
        return "File does not exist"

    if not SOURCE_FILE_NAME.endswith(".txt"):
        print("Only text files are allowed")
        logger.error("Only text files are allowed: %s", SOURCE_FILE_NAME)
        return "Only text files are allowed"

    try:
        with open(SOURCE_FILE_NAME, "r", encoding="utf-8") as f, open(
                DESTINATION_FILE_NAME, "w", encoding="utf-8"
        ) as d:
            content = f.read()
            symbol_count = len(content)
            d.write(f"Text has {symbol_count} characters")
            print(f"Success. Please check {DESTINATION_FILE_NAME}")
            logger.info(
                "Data is successfully written to %s", DESTINATION_FILE_NAME
            )
            return "Success"
    except FileNotFoundError:
        print("File is not found")
        logger.error("File is not found: %s", SOURCE_FILE_NAME)
        return "File is not found"
    except Exception as e:
        print("An unexpected error occurred:", str(e))
        logger.exception("Unexpected error")
        return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    main()
