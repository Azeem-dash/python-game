#!/usr/bin/env python3
"""
Run script for Enhanced Finger Pointer Game.
This game features improved hand isolation from surroundings,
advanced fingertip detection, and exciting gameplay elements.
"""

import os
import subprocess
import sys


def main():
    """Run the enhanced finger pointer game."""
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
        print("=" * 60)
        print("ENHANCED FINGER POINTER GAME - DELUXE EDITION")
        print("=" * 60)
        print("\n🌟 NEW FEATURES:")
        print("  • Improved hand isolation from backgrounds")
        print("  • Background subtraction for better tracking")
        print("  • Enhanced fingertip detection algorithms")
        print("  • New power-ups and special effects")
        print("  • Particle effects and visual enhancements")

        print("\n🎮 GAMEPLAY:")
        print("  1. Point your finger to control the blue ball")
        print("  2. Collect targets to increase your score:")
        print("     - Green circles (1 point)")
        print("     - Yellow circles (3 points)")
        print("     - Cyan circles (Speed boost)")
        print("     - Gold circles (Shield power-up)")
        print("     - Magenta circles (Magnet power-up)")
        print("  3. Avoid obstacles (brown squares)")
        print("  4. Power-ups provide special abilities:")
        print("     - Speed Boost: Move faster for 5 seconds")
        print("     - Shield: Protection from obstacles for 8 seconds")
        print("     - Magnet: Attract nearby targets for 10 seconds")

        print("\n📹 HAND TRACKING TIPS:")
        print("  - Hold your hand with index finger extended")
        print("  - Keep your hand well-lit and against a contrasting background")
        print(
            "  - Stay still for a few seconds at the beginning to train the background model"
        )
        print("  - The game will show a yellow circle at your detected fingertip")
        print("  - A green line shows the direction the game is using")

        print("\n⌨️ CONTROLS:")
        print("  - Press 'q' to quit the camera window")
        print("  - Press 'ESC' to quit the game")
        print("  - Press 'SPACE' to restart after game over")
        print("  - Press 'b' to manually recalibrate the background model")

        print("\nStarting game... Please wait while background model initializes...")
        print("-" * 60)

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
