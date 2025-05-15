#!/usr/bin/env python3
"""
Run script for Improved Finger Pointer Game.
This game uses your index finger pointing direction to precisely control ball movement.
Face detection has been disabled to focus exclusively on finger tracking.
"""

import os
import subprocess
import sys


def main():
    """Run the improved finger pointer game."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the script directory to sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Check if dependencies are installed
    try:
        requirements_file = os.path.join(script_dir, "simplified_requirements.txt")
        if os.path.exists(requirements_file):
            print("Checking and installing dependencies...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_file]
                )
            except subprocess.CalledProcessError:
                print("Warning: Failed to install some dependencies.")
    except Exception as e:
        print(f"Warning: Error checking dependencies: {e}")

    # Run the game script
    try:
        print("=" * 50)
        print("IMPROVED FINGER POINTER GAME")
        print("=" * 50)
        print("\nKey Features:")
        print("  • Face detection disabled - focusing exclusively on finger tracking")
        print("  • Enhanced fingertip detection for more precise control")
        print("  • Visual guides showing exactly where your fingertip is detected")
        print("\nInstructions:")
        print("  1. Position yourself in front of your webcam")
        print(
            "  2. Hold your hand up with index finger extended and other fingers curled"
        )
        print(
            "  3. Point your index finger in the direction you want the ball to move:"
        )
        print("     - Point right: Ball moves right")
        print("     - Point left: Ball moves left")
        print("     - Point up: Ball moves up")
        print("     - Point down: Ball moves down")
        print("  4. Make sure your fingertip is clearly visible to the camera")
        print("  5. Collect colored targets to increase your score:")
        print("     - Green circles: 1 point")
        print("     - Yellow circles: 3 points")
        print("     - Cyan circles: Speed boost")
        print("  6. Avoid brown obstacles")
        print("\nControls:")
        print("  - Press 'q' to quit the camera window")
        print("  - Press 'ESC' to quit the game")
        print("  - Press 'SPACE' to restart after game over")
        print("\nTips for best finger detection:")
        print("  - Ensure good lighting on your hand")
        print("  - Keep a plain background behind your hand")
        print("  - Make a clear pointing gesture with index finger extended")
        print("  - The game now shows your detected fingertip with a yellow circle")
        print("  - A green line indicates the pointing direction the game is using")
        print("\nStarting game...")
        print("-" * 50)

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
