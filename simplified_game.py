#!/usr/bin/env python3
"""
Hand Motion Adventure Game - Simplified Version
This version uses basic OpenCV techniques instead of MediaPipe for hand tracking.
"""

import math
import os
import random
import sys
import time

import cv2
import numpy as np
import pygame

# Game-specific imports
try:
    # First try to import without src prefix (local files)
    from simple_detection import SimpleHandDetector
except ImportError:
    try:
        # Fallback to importing from src
        from src.simple_detection import SimpleHandDetector
    except ImportError:
        print("Error: Could not import hand detection module.")
        sys.exit(1)


# Classes needed but missing from removed src folder
class Character:
    """The player character that moves around the screen."""

    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.jump_strength = -10
        self.gravity = 0.5
        self.on_ground = False
        self.health = 100
        self.score = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False


class Obstacle:
    """A game obstacle that can damage the player."""

    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def check_collision(self, character):
        return (
            self.x < character.x + character.width
            and self.x + self.width > character.x
            and self.y < character.y + character.height
            and self.y + self.height > character.y
        )


class Target:
    """A target that the player can collect for points."""

    def __init__(self, x, y, radius, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.collected = False
        self.value = 0

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def check_collection(self, character):
        if not self.collected:
            if (
                self.x > character.x
                and self.x < character.x + character.width
                and self.y > character.y
                and self.y < character.y + character.height
            ):
                self.collected = True
                return True
        return False


class ParticleSystem:
    """A simple particle system for visual effects."""

    def __init__(self):
        self.particles = []

    def add_particles(self, x, y, color, count=5):
        for _ in range(count):
            particle = {
                "x": x,
                "y": y,
                "dx": random.uniform(-2, 2),
                "dy": random.uniform(-2, 2),
                "color": color,
                "size": random.randint(2, 5),
                "life": random.randint(10, 30),
            }
            self.particles.append(particle)

    def update(self):
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(
                screen,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )


class SimplifiedGame:
    """Main game class for the simplified game using OpenCV hand tracking."""

    def __init__(self):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simplified Hand Motion Game")

        # Set up clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.delta_time = 0
        self.last_time = time.time()

        # Set up webcam
        # Get camera index from environment variable or use default
        try:
            camera_index = int(os.environ.get("GAME_CAMERA_INDEX", 0))
            print(f"Using camera index: {camera_index}")
        except ValueError:
            camera_index = 0
            print(f"Invalid camera index format. Using default: {camera_index}")

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(
                f"Error: Could not open camera {camera_index}. Trying fallback to camera 0..."
            )
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open any camera.")
                sys.exit()

        # Set up hand detector
        self.hand_detector = SimpleHandDetector()

        # Game state
        self.running = True
        self.game_state = "title"  # title, playing, game_over
        self.score = 0
        self.level = 1
        self.lives = 3
        self.time_remaining = 60  # seconds

        # Game objects
        self.character = Character(self.width // 2, self.height // 2, 50, 50)
        self.targets = []
        self.obstacles = []
        self.particle_system = ParticleSystem()

        # Game timers
        self.target_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.target_spawn_delay = 1.5  # seconds
        self.obstacle_spawn_delay = 5.0  # seconds

        # Hand tracking variables
        self.hand_position = None
        self.current_gesture = None

        # Set up fonts
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)

        # Set up colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)

        # Initial level setup
        self.setup_level(self.level)

    def setup_level(self, level):
        """Set up a new level."""
        self.level = level
        self.targets = []
        self.obstacles = []

        # Adjust difficulty based on level
        self.target_spawn_delay = max(0.5, 1.5 - (level - 1) * 0.1)
        self.obstacle_spawn_delay = max(2.0, 5.0 - (level - 1) * 0.3)

        # Add initial targets
        for _ in range(5):
            self.spawn_target()

        # Add obstacles based on level
        num_obstacles = min(level, 8)
        for _ in range(num_obstacles):
            self.spawn_obstacle()

        # Reset timers
        self.target_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.time_remaining = max(30, 60 - (level - 1) * 5)  # Decrease time per level

    def spawn_target(self):
        """Create a new target at a random position."""
        # Generate random position
        x = random.randint(50, self.width - 50)
        y = random.randint(50, self.height - 50)

        # Target types with different values
        target_types = [
            {"type": "standard", "value": 1, "color": self.GREEN},
            {"type": "bonus", "value": 3, "color": self.YELLOW},
            {"type": "special", "value": 5, "color": self.BLUE},
        ]

        # Select a random target type
        target_info = random.choice(target_types)

        # Create target
        target = Target(x, y, 15, target_info["color"])
        target.value = target_info["value"]  # Add value attribute to the Target
        self.targets.append(target)

    def spawn_obstacle(self):
        """Spawn a new obstacle at a random position."""
        margin = 100

        # Randomize size based on level
        width = random.randint(30, 50 + self.level * 5)
        height = random.randint(30, 50 + self.level * 5)

        # Randomize position
        x = random.randint(margin, self.width - width - margin)
        y = random.randint(margin, self.height - height - margin)

        # Create obstacle
        self.obstacles.append(Obstacle(x, y, width, height, self.RED))

    def process_hand_tracking(self):
        """Process webcam input and track hands using simple OpenCV methods."""
        ret, frame = self.cap.read()
        if not ret:
            print("ERROR: Failed to read frame from camera")
            return

        # Flip the frame horizontally for more intuitive mirroring
        frame = cv2.flip(frame, 1)

        # Resize frame to be more manageable
        frame_height, frame_width = frame.shape[:2]
        target_width = 640  # Target display width
        if frame_width > target_width:
            scale = target_width / frame_width
            frame = cv2.resize(
                frame, (int(frame_width * scale), int(frame_height * scale))
            )

        # Process frame with simplified hand detector
        center, contour, processed_frame = self.hand_detector.process_frame(frame)

        # Get current gesture
        self.current_gesture = self.hand_detector.get_gesture()

        # Get hand position
        self.hand_position = center

        # Update character based on hand tracking
        if self.hand_position:
            # Map hand coordinates to screen coordinates
            screen_x = int(
                self.hand_position[0] * self.width / processed_frame.shape[1]
            )
            screen_y = int(
                self.hand_position[1] * self.height / processed_frame.shape[0]
            )

            # Update character target position
            self.character.x = screen_x
            self.character.y = screen_y

        # Update character gesture
        if self.current_gesture:
            self.character.color = self.WHITE
        else:
            self.character.color = self.RED

        # Add user instructions to the frame
        instruction = "Wave hand to start - Use hand gestures to control character"
        cv2.putText(
            processed_frame,
            instruction,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        if self.current_gesture:
            gesture_text = f"Detected: {self.current_gesture}"
            cv2.putText(
                processed_frame,
                gesture_text,
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        # Make window appear in the foreground
        cv2.namedWindow("Hand Tracking", cv2.WINDOW_NORMAL)
        cv2.imshow("Hand Tracking", processed_frame)
        cv2.moveWindow("Hand Tracking", 50, 50)

    def update(self):
        """Update game state."""
        # Calculate delta time
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time

        # Process hand tracking
        self.process_hand_tracking()

        if self.game_state == "playing":
            # Update timers
            self.time_remaining -= self.delta_time
            if self.time_remaining <= 0:
                self.game_over()

            # Spawn targets
            self.target_spawn_timer += self.delta_time
            if self.target_spawn_timer >= self.target_spawn_delay:
                self.spawn_target()
                self.target_spawn_timer = 0

            # Spawn obstacles
            self.obstacle_spawn_timer += self.delta_time
            if self.obstacle_spawn_timer >= self.obstacle_spawn_delay:
                self.spawn_obstacle()
                self.obstacle_spawn_timer = 0

            # Update character
            self.character.update()

            # Update targets
            for target in self.targets:
                if target.check_collection(self.character):
                    target.collected = True
                    self.score += target.value
                    self.targets.remove(target)

            # Update obstacles
            for obstacle in self.obstacles:
                if obstacle.check_collision(self.character):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over()

            # Update particles
            self.particle_system.update()

            # Check for level completion (all targets collected)
            if len(self.targets) == 0:
                self.level_up()

    def level_up(self):
        """Advance to the next level."""
        self.level += 1
        self.setup_level(self.level)

    def game_over(self):
        """Handle game over state."""
        self.game_state = "game_over"

    def draw(self):
        """Draw the game state to the screen."""
        # Fill background
        self.screen.fill(self.BLACK)

        if self.game_state == "title":
            self.draw_title_screen()
        elif self.game_state == "playing":
            self.draw_playing_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen()

        # Update display
        pygame.display.flip()

    def draw_title_screen(self):
        """Draw the title screen."""
        # Draw title
        title_text = self.font_large.render("Hand Motion Game", True, self.WHITE)
        self.screen.blit(
            title_text,
            (
                self.width // 2 - title_text.get_width() // 2,
                self.height // 3 - title_text.get_height() // 2,
            ),
        )

        # Draw instructions
        instructions = [
            "Control the character with your hand movements",
            "Use different hand gestures for special abilities",
            "Collect targets and avoid obstacles",
            "Wave your hand to start the game",
        ]

        y_offset = self.height // 2
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.WHITE)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

        # Draw "Start Game" text
        start_text = self.font_medium.render("Wave to Start", True, self.YELLOW)
        self.screen.blit(
            start_text,
            (self.width // 2 - start_text.get_width() // 2, self.height * 3 // 4),
        )

        # Check for wave gesture to start
        if self.current_gesture in ["open_palm", "victory"]:
            self.game_state = "playing"

    def draw_playing_screen(self):
        """Draw the main gameplay screen."""
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw targets
        for target in self.targets:
            target.draw(self.screen)

        # Draw particles
        self.particle_system.draw(self.screen)

        # Draw character
        self.character.draw(self.screen)

        # Draw UI elements
        self.draw_ui()

    def draw_ui(self):
        """Draw UI elements for the playing state."""
        # Draw score
        score_text = self.font_small.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw level
        level_text = self.font_small.render(f"Level: {self.level}", True, self.WHITE)
        self.screen.blit(level_text, (20, 60))

        # Draw lives
        lives_text = self.font_small.render(f"Lives: {self.lives}", True, self.WHITE)
        self.screen.blit(lives_text, (20, 100))

        # Draw time remaining
        time_text = self.font_small.render(
            f"Time: {int(self.time_remaining)}", True, self.WHITE
        )
        self.screen.blit(time_text, (20, 140))

        # Draw current gesture
        if self.current_gesture:
            gesture_text = self.font_small.render(
                f"Gesture: {self.current_gesture}", True, self.WHITE
            )
            self.screen.blit(
                gesture_text, (self.width - gesture_text.get_width() - 20, 20)
            )

    def draw_game_over_screen(self):
        """Draw the game over screen."""
        # Draw game over text
        game_over_text = self.font_large.render("Game Over", True, self.RED)
        self.screen.blit(
            game_over_text,
            (
                self.width // 2 - game_over_text.get_width() // 2,
                self.height // 3 - game_over_text.get_height() // 2,
            ),
        )

        # Draw final score
        score_text = self.font_medium.render(
            f"Final Score: {self.score}", True, self.WHITE
        )
        self.screen.blit(
            score_text,
            (
                self.width // 2 - score_text.get_width() // 2,
                self.height // 2 - score_text.get_height() // 2,
            ),
        )

        # Draw level reached
        level_text = self.font_medium.render(
            f"Level Reached: {self.level}", True, self.WHITE
        )
        self.screen.blit(
            level_text,
            (
                self.width // 2 - level_text.get_width() // 2,
                self.height // 2 + 50 - level_text.get_height() // 2,
            ),
        )

        # Draw restart instructions
        restart_text = self.font_medium.render("Wave to Restart", True, self.YELLOW)
        self.screen.blit(
            restart_text,
            (self.width // 2 - restart_text.get_width() // 2, self.height * 3 // 4),
        )

        # Check for wave gesture to restart
        if self.current_gesture in ["open_palm", "victory"]:
            self.reset_game()

    def reset_game(self):
        """Reset the game to the initial state."""
        self.game_state = "playing"
        self.score = 0
        self.level = 1
        self.lives = 3
        self.setup_level(self.level)

    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_state == "title":
                    self.game_state = "playing"
                elif event.key == pygame.K_r and self.game_state == "game_over":
                    self.reset_game()

    def run(self):
        """Main game loop."""
        try:
            while self.running:
                # Handle events
                self.handle_events()

                # Update game state
                self.update()

                # Draw everything
                self.draw()

                # Cap the frame rate
                self.clock.tick(self.fps)

        finally:
            # Clean up resources
            self.cap.release()
            cv2.destroyAllWindows()
            pygame.quit()


def main():
    """Main entry point for the game."""
    print("=" * 50)
    print("Hand Motion Game - Simplified Version")
    print("=" * 50)
    print("This version uses basic OpenCV for hand tracking instead of MediaPipe.")
    print("Starting game...")

    try:
        # Install required packages
        import pip

        for package in ["opencv-python", "numpy", "pygame"]:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                print(f"Installing {package}...")
                pip.main(["install", package])

        game = SimplifiedGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
