import sys

from pytest import Config


def find_intuned_browser_parent_folder(start_path: str) -> str:
    import os

    current_path = os.path.dirname(os.path.abspath(start_path))

    while True:
        # Check if 'intuned_browser' is in the current directory
        if "intuned_browser" in os.listdir(current_path):
            return current_path

        # Move up one directory
        parent_path = os.path.dirname(current_path)

        # If we've reached the root directory and haven't found it, return None
        if parent_path == current_path:
            raise Exception("intuned_browser folder not found")

        current_path = parent_path


# Get the project root directory
project_root = find_intuned_browser_parent_folder(__file__)

print(f"project_root: {project_root}")

sys.path.append(project_root)


def pytest_configure(config: Config):
    config.addinivalue_line("markers", "e2e: e2e tests")

    # Set logging level to INFO
    import logging

    logging.basicConfig(level=logging.INFO)
