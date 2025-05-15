# Hand Gesture Platformer Game

A simple side-scrolling platformer game controlled by hand gestures through your camera.

## Features

- Control a character with precise hand gestures
- Point your finger left/right to move in that direction
- Make a closed fist to jump
- Collect coins to increase your score
- Avoid obstacles and don't fall off platforms
- Simple but fun gameplay with parallax scrolling backgrounds

## Controls

- **Move left**: Point your finger to the left
- **Move right**: Point your finger to the right
- **Jump**: Make a closed fist (ball your hand)
- **Quit game**: Press 'ESC' or 'q' in the camera window
- **Restart game**: Press 'SPACE' after game over

## Requirements

- Python 3.6 or higher
- OpenCV (`opencv-python`)
- NumPy
- PyGame

All required packages are listed in the `simplified_requirements.txt` file and will be automatically installed when you run the game.

## How to Run

Simply run the `run_platformer_game.py` script:

```bash
python run_platformer_game.py
```

or

```bash
./run_platformer_game.py
```

## Hand Detection Tips

- Keep your hand well-lit and against a contrasting background
- Stay still for a few seconds at the beginning to train the background model
- Point your finger clearly in the direction you want to move
- Make a clear fist gesture when you want to jump
- Make sure your hand is clearly visible to the camera

## How It Works

The game uses OpenCV for hand tracking and gesture recognition. It detects your hand using skin color detection and background subtraction, then analyzes the contour of your hand to detect specific gestures and pointing directions. The orientation of your hand and your gesture type (pointing or closed fist) is translated into game controls.

The platformer itself is built with PyGame and features:
- Side-scrolling level with multiple platforms
- Collectible coins for points
- Moving obstacles to avoid
- Parallax scrolling background with clouds
- Game over handling with restart option

## Troubleshooting

If you encounter issues:

1. Make sure your camera is working and not being used by another application
2. Ensure proper lighting conditions for good hand detection
3. Try adjusting your distance from the camera
4. If the game crashes, check that all dependencies are properly installed

## Credits

This game was created as part of a hand motion tracking project using computer vision and Python. 