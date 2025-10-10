"""
The module contains several general util functions with no
specific technology or SDK binding (e.g., Google SDK)
"""

# Import Standard Libraries
import logging
import pathlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def read_file_from_path(file_path: pathlib.Path, root_path: pathlib.Path) -> str:
    """
    Read a file from local path

    Args:
        file_path (pathlib.Path): Local file path
        root_path (pathlib.Path): Local root path

    Returns:
        file_read (String): Read file
    """

    # Check if the root_path exists
    if not root_path.exists():
        logging.error(f"🚨 Root path {root_path.as_posix()} does not exist")
        raise EnvironmentError("The root path does not exist")

    # Update the file_path with the project root directory
    file_path = root_path / file_path

    # Check if the file_path exists
    if file_path.exists():
        logging.info(f"📖 Reading file from {file_path.as_posix()}")

        # Read file
        with open(file_path, "r", encoding="utf-8") as file:
            file_read = file.read()
    else:
        raise FileNotFoundError(f"❌ Unable to locate file: {file_path.as_posix()}")

    return file_read
