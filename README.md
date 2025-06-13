# Hand Motion Adventure Game

A Python-based game collection that uses computer vision and traditional controls for gameplay.

## Sample Gameplay

![Sample Gameplay 1](assets/sample1.png)
![Sample Gameplay 2](assets/sample2.png)

## Games Available

1. **Platformer Game** - A classic platform game with jumping and obstacles. See `PLATFORMER_README.md` for more details.
2. **Simplified Game** - A simplified version that uses basic controls
3. **Simple Running Game** - A running game where you collect objects and avoid obstacles

## Requirements

- Python 3.7+
- OpenCV
- PyGame
- NumPy
- Pillow

## Installation

1. Clone this repository or download the source code:
   ```bash
   git clone https://github.com/yourusername/hand_motion_game.git
   cd hand_motion_game
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have a working webcam connected to your computer (for games that use camera input)

## Community Testing Guide

We welcome community testing! Here's how you can test the games:

1. **Setup**:
   - Make sure you have Python 3.7+ installed
   - Install all dependencies from requirements.txt
   - Connect a webcam to your computer

2. **Testing Steps**:
   - Run the main launcher: `python3 run_game.py`
   - Try each game mode
   - Test with different lighting conditions
   - Test with different hand positions

3. **Reporting Issues**:
   - If you encounter any bugs, please open an issue with:
     - Your operating system
     - Python version
     - Steps to reproduce
     - Screenshots if possible

4. **Feedback**:
   - Share your experience
   - Suggest improvements
   - Report any performance issues

## How to Play

You can run each game individually or use the main launcher to select a game and camera:

### Using the Main Launcher

Run the main launcher to select a game and camera:
```bash
python3 run_game.py
```

The launcher will:
1. Let you select which game to play
2. Detect available cameras on your system
3. Let you choose which camera to use (useful if you have multiple cameras)
4. Launch the selected game with the chosen camera

### Running Games Individually

1. To run the platformer game:
   ```bash
   python3 run_platformer_game.py
   ```
   
2. To run the simplified game:
   ```bash
   python3 simplified_game.py
   ```
   
3. To run the simple running game:
   ```bash
   python3 simple_running_game.py
   ```

## Game Controls

Each game has its own specific controls. Please refer to in-game instructions or the specific game's section.

## Project Structure

- `run_game.py` - Main launcher for all games with camera selection
- `run_platformer_game.py` - Entry point for the platformer game
- `platformer_game.py` - Core logic for the platformer game
- `simplified_game.py` - The simplified game implementation
- `simple_running_game.py` - The simple running game implementation
- `simple_detection.py` - Hand detection module used by the games
- `assets/` - Images and sound effects

## Customization

You can add your own images to the `assets/` folder:
- `character.png` - Main character image
- `background.png` - Game background
- `title_screen.png` - Title screen background
- And other game-specific assets

## Performance Tips

- Ensure good lighting for better hand detection (for games that use camera)
- Position your hand clearly in view of the camera
- If experiencing lag, try reducing the window size or lowering the resolution in the game settings

## Troubleshooting

- **Camera not working**: Make sure your webcam is properly connected and not in use by another application. Use the camera selection feature to try different cameras.
- **Poor tracking**: Improve lighting conditions and ensure your hand is clearly visible
- **Game crashes**: Check that all required dependencies are installed correctly

## Contributing

We welcome contributions from the community! Here's how you can help:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License. 