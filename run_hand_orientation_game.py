#!/usr/bin/env python3
"""
Run script for Finger Pointing Game.
This game uses your finger pointing direction to control the ball's movement.
"""

import os
import subprocess
import sys


def main():
    """Run the finger pointing game."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the script directory to sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Check if dependencies are installed
    try:
        import pip

        requirements_file = os.path.join(script_dir, "simplified_requirements.txt")
        if os.path.exists(requirements_file):
            print("Checking and installing dependencies...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file]
            )
    except ImportError:
        print("Warning: pip not found. Cannot check dependencies.")
    except subprocess.CalledProcessError:
        print("Warning: Failed to install some dependencies.")

    # Run the game script
    try:
        print("Starting Finger Pointing Game...")
        print("Instructions:")
        print("  - Hold your hand up with index finger extended and pointing")
        print("  - Point your finger in different directions:")
        print("    * Finger pointing right: Ball moves right")
        print("    * Finger pointing left: Ball moves left")
        print("    * Finger pointing up: Ball moves up")
        print("    * Finger pointing down: Ball moves down")
        print("  - The game will track your fingertip to determine direction")
        print("  - Collect targets to increase your score")
        print("  - Avoid obstacles")
        print("\nPress 'q' to quit the game.")

        # Execute the finger pointer game script
        finger_pointer_script = os.path.join(script_dir, "finger_pointer_game.py")
        if os.path.exists(finger_pointer_script):
            if sys.platform.startswith("win"):
                # Windows
                os.system(f'python "{finger_pointer_script}"')
            else:
                # Linux/Mac
                os.system(f'python3 "{finger_pointer_script}"')
        else:
            print(f"Error: Could not find {finger_pointer_script}")
            return 1
    except Exception as e:
        print(f"Error: Failed to run game: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
