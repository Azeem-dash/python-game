# Hand Motion Game Instructions

## Overview

This project contains multiple versions of a hand motion game that uses computer vision to track your hand and control a ball in a game environment. The primary goal is to collect targets while avoiding obstacles.

## Versions Available

### 1. Original Hand Tracking Game
- Uses OpenCV for basic hand detection
- Control a ball using hand position

### 2. Finger Pointer Game (Recommended)
- Uses your index finger pointing direction to control ball movement
- **Enhanced**: Now with improved fingertip detection for more precise control
- Tracks the tip of your index finger for more intuitive pointing
- **Note**: Fixed issues with `np.int0` on newer NumPy versions

### 3. Hand Orientation Game
- Uses the orientation of your entire hand to control ball movement
- Works on Apple Silicon Macs

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- PyGame

## Setup Instructions

1. Make sure you have Python installed on your system
2. Install the required dependencies:
   ```
   pip install -r simplified_requirements.txt
   ```

## Running the Game

### Option 1: Using the Run Scripts (Recommended)

For the finger pointer game (best option):
```
python run_hand_orientation_game.py
```

For the hand orientation game:
```
python run_improved_game.py
```

### Option 2: Running Game Files Directly

For the finger pointer game:
```
python finger_pointer_game.py
```

For the hand orientation game:
```
python hand_orientation_game.py
```

For the simplified game:
```
python simplified_game.py
```

## How to Play with Finger Pointing

1. Start the finger pointer game using one of the methods above
2. Position yourself in front of your webcam
3. For the best finger pointing control:
   - Hold your hand up with your index finger extended and other fingers curled
   - Point your index finger clearly in the direction you want the ball to move
   - Make sure your fingertip is clearly visible to the camera
   - If finger detection struggles, the game will fall back to hand orientation
   - Point your finger in different directions:
     * Finger pointing right: Ball moves right
     * Finger pointing left: Ball moves left
     * Finger pointing up: Ball moves up
     * Finger pointing down: Ball moves down
4. Collect targets (colored circles) to increase your score:
   - Green circles: 1 point
   - Yellow circles: 3 points
   - Cyan circles: Speed boost
5. Avoid brown obstacles
6. The game ends if you hit an obstacle

## Controls

- Press `q` to quit the camera window
- Press `ESC` to quit the game
- Press `SPACE` to restart after game over

## Troubleshooting

### Camera Issues
- Make sure your webcam is properly connected
- Check if the camera is being used by another application
- Try plugging the camera into a different USB port

### Finger Detection Issues
- Ensure good lighting conditions for better finger detection
- Position your hand with extended index finger clearly in the camera view
- Keep a plain background behind your hand if possible
- Try to make a clear pointing gesture with your index finger extended
- If fingertip detection isn't working well, try the hand orientation mode instead

### Game Issues
- If the game crashes or has performance issues, try the simplified version
- If you encounter an error with `np.int0`, use the improved game version which fixes this issue

### NumPy Version Issues
- If you encounter errors with NumPy integer types, update NumPy to the latest version:
  ```
  pip install numpy --upgrade
  ```

## Advanced: Creating Your Own Version

You can create your own version of the game by:
1. Copy one of the existing game files as a starting point
2. Modify the hand detection logic to use different gestures or controls
3. Add new game features (different obstacles, power-ups, etc.)
4. Create a new run script to launch your custom version 