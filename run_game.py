#!/usr/bin/env python3
"""
Main run script for all games.
This script lets you choose which game to run and which camera to use.
"""

import os
import subprocess
import sys

import cv2


def list_available_cameras(max_cameras=5):
    """List available cameras and return a list of valid indices."""
    available_cameras = []

    print("\nDetecting available cameras...")
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                camera_name = f"Camera {i}"
                if i == 0:
                    camera_name += " (Usually built-in)"
                elif i == 1:
                    camera_name += " (Usually external)"
                print(f"  {i}: {camera_name} - Available")
                available_cameras.append(i)
            cap.release()

    return available_cameras


def choose_camera():
    """Let the user choose which camera to use."""
    available_cameras = list_available_cameras()

    if not available_cameras:
        print("No cameras detected. Exiting.")
        return None

    if len(available_cameras) == 1:
        print(f"\nOnly one camera detected. Using camera index {available_cameras[0]}.")
        return available_cameras[0]

    while True:
        try:
            selection = input(
                "\nSelect camera by index (or press Enter for default camera 0): "
            )
            if selection == "":
                return 0

            selection = int(selection)
            if selection in available_cameras:
                return selection
            else:
                print(
                    f"Invalid selection. Please choose from available cameras: {available_cameras}"
                )
        except ValueError:
            print("Please enter a valid number.")


def select_game():
    """Let the user select which game to run."""
    games = [
        {"name": "Platformer Game", "script": "run_platformer_game.py"},
        {"name": "Simplified Game", "script": "simplified_game.py"},
        {"name": "Simple Running Game", "script": "simple_running_game.py"},
    ]

    print("\nAvailable games:")
    for i, game in enumerate(games):
        print(f"  {i + 1}: {game['name']}")

    while True:
        try:
            selection = input("\nSelect game (1-3): ")
            selection = int(selection)
            if 1 <= selection <= len(games):
                return games[selection - 1]
            else:
                print(
                    f"Invalid selection. Please choose a number between 1 and {len(games)}."
                )
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Main entry point for game selection and running."""
    print("=" * 60)
    print("Hand Motion Adventure Games")
    print("=" * 60)

    # Select a game
    game = select_game()
    print(f"\nSelected: {game['name']}")

    # Choose a camera
    camera_index = choose_camera()
    if camera_index is None:
        return 1

    # Set the camera selection as an environment variable
    os.environ["GAME_CAMERA_INDEX"] = str(camera_index)

    # Run the selected game
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), game["script"]
    )

    try:
        print(f"\nStarting {game['name']} with camera {camera_index}...")
        print("-" * 60)

        if sys.platform.startswith("win"):
            # Windows
            os.system(f'python "{script_path}"')
        else:
            # Linux/Mac
            os.system(f'python3 "{script_path}"')

    except Exception as e:
        print(f"Error running game: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
