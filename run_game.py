#!/usr/bin/env python3
"""
Run script for Hand Motion Adventure Game.
"""

import os
import subprocess
import sys


def main():
    """Run the game from the project root."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the script directory to sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Check if dependencies are installed
    try:
        import pip

        requirements_file = os.path.join(script_dir, "requirements.txt")
        if os.path.exists(requirements_file):
            print("Checking and installing dependencies...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file]
            )
    except ImportError:
        print("Warning: pip not found. Cannot check dependencies.")
    except subprocess.CalledProcessError:
        print("Warning: Failed to install some dependencies.")

    # Run the main script
    try:
        from src.main import main as run_game

        return run_game()
    except ImportError as e:
        print(f"Error: Failed to import game: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
