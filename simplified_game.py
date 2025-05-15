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

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.game_objects import Character, Obstacle, ParticleSystem, Target
    from src.simple_detection import SimpleHandDetector
except ImportError:
    # If src module not found, try importing from the local directory
    from simple_detection import SimpleHandDetector

    # Define minimal game objects if not available
    class Character:
        def __init__(self, x, y, size=50):
            self.x = x
            self.y = y
            self.size = size
            self.gesture = None
            self.velocity = [0, 0]
            self.max_speed = 10
            self.target_position = (x, y)
            self.is_attacking = False
            self.attack_cooldown = 0

        def update(self, delta_time):
            # Calculate direction to target
            dx = self.target_position[0] - self.x
            dy = self.target_position[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 5:
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance

                # Set velocity based on gesture
                target_speed = self.max_speed
                if self.gesture == "pointing":
                    target_speed = self.max_speed * 1.5
                elif self.gesture == "open_palm":
                    target_speed = self.max_speed * 0.8
                elif self.gesture == "closed_fist":
                    target_speed = self.max_speed * 0.3

                # Apply movement
                self.x += dx * target_speed
                self.y += dy * target_speed

            # Handle attack cooldown
            if self.attack_cooldown > 0:
                self.attack_cooldown -= delta_time

        def set_gesture(self, gesture):
            self.gesture = gesture

            # Special gesture handling
            if gesture == "thumbs_up" and self.attack_cooldown <= 0:
                self.is_attacking = True
                self.attack_cooldown = 1.0  # 1 second cooldown
            else:
                self.is_attacking = False

        def set_target_position(self, position):
            self.target_position = position

        def get_rect(self):
            return pygame.Rect(
                self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
            )

        def draw(self, screen):
            color = (50, 50, 255)  # Blue

            # Change color based on gesture
            if self.gesture == "open_palm":
                color = (50, 255, 50)  # Green
            elif self.gesture == "closed_fist":
                color = (255, 50, 50)  # Red
            elif self.gesture == "pointing":
                color = (255, 255, 50)  # Yellow
            elif self.gesture == "victory":
                color = (50, 255, 255)  # Cyan
            elif self.gesture == "thumbs_up":
                color = (255, 50, 255)  # Magenta

            # Draw the character
            pygame.draw.circle(
                screen, color, (int(self.x), int(self.y)), self.size // 2
            )

            # Draw attack effect if attacking
            if self.is_attacking:
                pygame.draw.circle(
                    screen,
                    (255, 200, 0, 128),
                    (int(self.x), int(self.y)),
                    self.size * 1.5,
                    5,
                )

    class Target:
        def __init__(self, x, y, size=30, value=1, type="standard"):
            self.x = x
            self.y = y
            self.size = size
            self.value = value
            self.type = type
            self.collected = False
            self.colors = {
                "standard": (0, 255, 0),
                "bonus": (255, 255, 0),
                "special": (255, 0, 255),
                "negative": (255, 0, 0),
            }

        def update(self, delta_time, screen_width, screen_height):
            pass

        def draw(self, screen):
            if self.collected:
                return

            color = self.colors.get(self.type, (0, 255, 0))
            pygame.draw.circle(
                screen, color, (int(self.x), int(self.y)), self.size // 2
            )

        def get_rect(self):
            return pygame.Rect(
                self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
            )

    class Obstacle:
        def __init__(self, x, y, width, height, speed=0, moving=False):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def update(self, delta_time):
            pass

        def draw(self, screen):
            pygame.draw.rect(
                screen,
                (150, 75, 0),
                (int(self.x), int(self.y), self.width, self.height),
            )

        def get_rect(self):
            return pygame.Rect(self.x, self.y, self.width, self.height)

    class ParticleSystem:
        def __init__(self):
            self.particles = []

        def add_explosion(self, x, y, color, count=20, size=5, life=1.0):
            pass

        def update(self, delta_time):
            pass

        def draw(self, screen):
            pass


class SimplifiedGame:
    """Simplified game class using basic OpenCV for hand tracking."""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Motion Game - Simplified")

        # Set up clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.delta_time = 0
        self.last_time = time.time()

        # Set up webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
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
        self.character = Character(self.width // 2, self.height // 2)
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
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 50, 50)
        self.GREEN = (50, 255, 50)
        self.BLUE = (50, 50, 255)
        self.YELLOW = (255, 255, 50)

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
        """Spawn a new target at a random position."""
        margin = 50
        x = random.randint(margin, self.width - margin)
        y = random.randint(margin, self.height - margin)

        # Choose target type based on probability
        target_type = "standard"
        rand = random.random()
        if rand > 0.9:
            target_type = "special"
            value = 5
        elif rand > 0.7:
            target_type = "bonus"
            value = 2
        elif rand > 0.95:
            target_type = "negative"
            value = -2
        else:
            value = 1

        # Create target
        self.targets.append(Target(x, y, 30, value, target_type))

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
        self.obstacles.append(Obstacle(x, y, width, height))

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
            self.character.set_target_position((screen_x, screen_y))

        # Update character gesture
        if self.current_gesture:
            self.character.set_gesture(self.current_gesture)

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
            self.character.update(self.delta_time)

            # Update targets
            for target in self.targets:
                target.update(self.delta_time, self.width, self.height)

            # Update obstacles
            for obstacle in self.obstacles:
                obstacle.update(self.delta_time)

            # Update particles
            self.particle_system.update(self.delta_time)

            # Check for collisions
            self.check_collisions()

            # Check for level completion (all targets collected)
            if len(self.targets) == 0:
                self.level_up()

    def check_collisions(self):
        """Check for collisions between game objects."""
        # Get character rectangle
        char_rect = self.character.get_rect()

        # Check for collisions with targets
        targets_to_remove = []
        for i, target in enumerate(self.targets):
            if not target.collected and char_rect.colliderect(target.get_rect()):
                # Handle collision with target
                target.collected = True
                targets_to_remove.append(i)

                # Update score
                self.score += target.value

        # Remove collected targets
        for i in sorted(targets_to_remove, reverse=True):
            del self.targets[i]

        # Check for collisions with obstacles
        for obstacle in self.obstacles:
            if char_rect.colliderect(obstacle.get_rect()):
                # Handle collision with obstacle
                self.handle_damage()
                break

    def handle_damage(self):
        """Handle character taking damage."""
        self.lives -= 1

        # Check for game over
        if self.lives <= 0:
            self.game_over()

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
