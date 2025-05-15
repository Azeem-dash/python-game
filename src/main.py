#!/usr/bin/env python3
"""
Hand Motion Adventure Game
A game that uses computer vision to track hand movements for controlling gameplay.
"""

import os
import sys
import time

# Add the parent directory to sys.path so we can import the modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


def main():
    """Main entry point for the game."""
    # Display welcome message
    print("=" * 50)
    print("Hand Motion Adventure Game")
    print("=" * 50)
    print("Initializing...")

    # Check for required packages
    missing_packages = check_dependencies()
    if missing_packages:
        print("\nError: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        return 1

    print("All dependencies found!")

    # Import game module
    print("Loading game modules...")
    try:
        from src.game import HandMotionGame
    except ImportError as e:
        print(f"Error importing game modules: {e}")
        return 1

    # Check for camera
    print("Checking camera...")
    if not check_camera():
        print("Warning: Could not detect a working camera.")
        response = input("Continue anyway? (y/n): ").lower()
        if response != "y":
            return 1

    print("Starting game...")
    time.sleep(1)

    # Start the game
    try:
        game = HandMotionGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        return 1

    return 0


def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = ["pygame", "cv2", "mediapipe", "numpy", "PIL"]
    missing_packages = []

    for package in required_packages:
        try:
            if package == "cv2":
                # OpenCV is imported as cv2
                import cv2
            elif package == "PIL":
                # Pillow is imported as PIL
                import PIL
            else:
                # Try to import the package
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    return missing_packages


def check_camera():
    """Check if a camera is available."""
    try:
        import cv2

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        cap.release()
        return ret
    except:
        return False


if __name__ == "__main__":
    sys.exit(main())
