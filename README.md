# Hand Motion Adventure Game

A Python-based game that uses computer vision to track hand movements and gestures to control gameplay.

## Features

- **Real-time hand tracking** using MediaPipe for precise gesture recognition
- **Multiple gesture controls** (open palm, closed fist, pointing, victory sign, thumbs up)
- **Physics-based character movement** controlled by your hand position
- **Progressive difficulty** with multiple levels
- **Particle effects** for visual feedback
- **Collision detection** with obstacles and collectibles

## Simplified Version for Apple Silicon Macs

A simplified version of the game is available that uses only OpenCV (without MediaPipe) for hand tracking. This version is compatible with Apple Silicon Macs and other systems where MediaPipe may not work correctly.

### Hand Orientation Control Game

This version uses the orientation of your entire hand to control the ball's movement:

1. Run the game:
   ```
   python finger_pointer_game.py
   ```
2. Hold your hand up with fingers extended
3. Rotate your hand to point in different directions:
   - Hand pointing right: Ball moves right
   - Hand pointing left: Ball moves left
   - Hand pointing up: Ball moves up
   - Hand pointing down: Ball moves down
4. Collect targets to increase your score
5. Avoid obstacles

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe (not needed for simplified version)
- PyGame
- NumPy
- Pillow

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   For simplified version without MediaPipe:
   ```
   pip install -r simplified_requirements.txt
   ```
3. Ensure you have a working webcam connected to your computer

## How to Play

1. Run the game:
   ```
   python src/game.py
   ```
   
   For the simplified version:
   ```
   python simplified_game.py
   ```
   
   For the finger pointer version:
   ```
   python finger_pointer_game.py
   ```
2. Position yourself in front of your webcam
3. Use the following hand gestures:
   - **Open Palm**: Normal movement, wave to start/restart game
   - **Closed Fist**: Slow down
   - **Pointing**: Move faster
   - **Victory Sign**: Wave to start/restart game
   - **Thumbs Up**: Activate special attack

## Game Controls

- **Move your hand** to control the character's position
- **Make different gestures** to trigger special abilities
- Press **Esc** to exit the game
- Press **Space** to start from the title screen
- Press **R** to restart after game over

## Project Structure

- `src/` - Source code files
  - `main.py` - Entry point
  - `game.py` - Main game logic
  - `hand_gestures.py` - Hand gesture recognition
  - `game_objects.py` - Game object classes
- `assets/` - Images and sound effects
- `requirements.txt` - Required Python packages

## Customization

You can add your own images to the `assets/` folder:
- `character.png` - Main character image
- `character_[gesture].png` - Character with specific gestures
- `target_[type].png` - Different target types
- `obstacle.png` - Obstacle image
- `background.png` - Game background
- `title_screen.png` - Title screen background
- `game_over.png` - Game over screen background

Sound effects (`*.wav` files):
- `collect.wav` - Collecting targets
- `hit.wav` - Taking damage
- `level_up.wav` - Advancing to next level
- `game_over.wav` - Game over sound

## Technical Details

The game uses MediaPipe's hand tracking technology to detect hand landmarks in real-time. It then uses these landmarks to recognize different hand gestures and determine the hand position.

The game is built with PyGame for rendering and game logic, while OpenCV handles the camera input and initial image processing.

## Performance Tips

- Ensure good lighting for better hand detection
- Position your hand clearly in view of the camera
- If experiencing lag, try reducing the window size or lowering the resolution in the game settings

## Troubleshooting

- **Camera not working**: Make sure your webcam is properly connected and not in use by another application
- **Poor tracking**: Improve lighting conditions and ensure your hand is clearly visible
- **Game crashes**: Check that all required dependencies are installed correctly 