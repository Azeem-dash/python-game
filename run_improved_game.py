#!/usr/bin/env python3
"""
Run script for Improved Hand Orientation Game.
This game uses the orientation of your hand to control a ball in a game.
"""

import os
import subprocess
import sys


def main():
    """Run the improved hand orientation game."""
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
        print("Starting Improved Hand Orientation Game...")
        print("Instructions:")
        print("  - Hold your hand up with fingers extended")
        print("  - Rotate your hand to point in different directions:")
        print("    * Hand pointing right: Ball moves right")
        print("    * Hand pointing left: Ball moves left")
        print("    * Hand pointing up: Ball moves up")
        print("    * Hand pointing down: Ball moves down")
        print("  - Collect targets (green/yellow circles) to increase your score")
        print("  - Avoid obstacles (brown squares)")
        print("  - Game ends if you hit an obstacle")
        print("\nControls:")
        print("  - Press 'q' to quit the camera window")
        print("  - Press 'ESC' to quit the game")
        print("  - Press 'SPACE' to restart after game over")

        # Execute the hand orientation game script
        orientation_game_script = os.path.join(script_dir, "hand_orientation_game.py")
        if os.path.exists(orientation_game_script):
            if sys.platform.startswith("win"):
                # Windows
                os.system(f'python "{orientation_game_script}"')
            else:
                # Linux/Mac
                os.system(f'python3 "{orientation_game_script}"')
        else:
            print(f"Error: Could not find {orientation_game_script}")
            return 1
    except Exception as e:
        print(f"Error: Failed to run game: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
