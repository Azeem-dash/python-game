#!/usr/bin/env python3
"""
Run script for Platformer Game.
This game features a side-scrolling platformer controlled by hand gestures.
"""

import os
import subprocess
import sys


def main():
    """Run the platformer game."""
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

    # Create assets directory if it doesn't exist
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Run the game script
    try:
        print("=" * 60)
        print("PLATFORMER GAME - HAND CONTROLLED")
        print("=" * 60)
        print("\n🎮 GAMEPLAY:")
        print("  • Point your finger LEFT to move the character left")
        print("  • Point your finger RIGHT to move the character right")
        print("  • Make a CLOSED FIST to jump")
        print("  • Collect gold coins to earn points")
        print("  • Avoid red obstacles")
        print("  • Don't fall off the platforms!")

        print("\n👋 CONTROLS:")
        print("  • Point finger LEFT: Move character left")
        print("  • Point finger RIGHT: Move character right")
        print("  • Make a CLOSED FIST: Jump")
        print("  • Press 'q' to quit the camera window")
        print("  • Press 'ESC' to quit the game")
        print("  • Press 'SPACE' to restart after game over")

        print("\n📹 HAND TRACKING TIPS:")
        print("  • Hold your hand with fingers spread for detection")
        print("  • Point your index finger clearly when you want to jump")
        print("  • Keep your hand well-lit and against a contrasting background")
        print(
            "  • Stay still for a few seconds at the beginning to train the background model"
        )

        print("\nStarting game... Please wait while initializing...")
        print("-" * 60)

        # Execute the platformer game script
        platformer_script = os.path.join(script_dir, "platformer_game.py")
        if os.path.exists(platformer_script):
            if sys.platform.startswith("win"):
                # Windows
                os.system(f'python "{platformer_script}"')
            else:
                # Linux/Mac
                os.system(f'python3 "{platformer_script}"')
        else:
            print(f"Error: Could not find {platformer_script}")
            return 1
    except Exception as e:
        print(f"Error: Failed to run game: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
