#!/usr/bin/env python3
"""
Hand Orientation Game
Control a ball by rotating your hand in different directions.
"""

import math
import os
import random
import sys
import time

try:
    import cv2
    import numpy as np
    import pygame
except ImportError:
    print("ERROR: Required libraries not found. Install with:")
    print("python3 -m pip install opencv-python numpy pygame")
    sys.exit(1)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Import hand orientation detector
try:
    from src.hand_orientation_detector import HandOrientationDetector
except ImportError:
    print("ERROR: Could not import HandOrientationDetector")
    print("Make sure the file exists in the src directory.")
    sys.exit(1)


class HandOrientationGame:
    """Game controlled by hand orientation."""

    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Orientation Game")

        # Set up clock
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Set up camera
        print("Initializing camera...")
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            print("ERROR: Could not open camera")
            pygame.quit()
            sys.exit(1)

        # Set up hand detector
        self.hand_detector = HandOrientationDetector()

        # Game state
        self.running = True
        self.game_state = "playing"  # playing, game_over
        self.score = 0

        # Ball properties
        self.ball_pos = [self.width // 2, self.height // 2]
        self.ball_radius = 20
        self.ball_color = (50, 50, 255)  # Blue
        self.ball_speed = 5
        self.ball_velocity = [0, 0]  # x, y velocity

        # Target properties
        self.targets = []
        self.spawn_target_timer = 0
        self.spawn_target_delay = 2  # seconds

        # Obstacles properties
        self.obstacles = []
        self.spawn_obstacle_timer = 0
        self.spawn_obstacle_delay = 5  # seconds

        # Create initial targets and obstacles
        for _ in range(5):
            self.spawn_target()

        for _ in range(3):
            self.spawn_obstacle()

        # Hand orientation properties
        self.direction_vector = None

        # Set up fonts
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)

        # Set up colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.GREEN = (50, 255, 50)
        self.BLUE = (50, 50, 255)
        self.YELLOW = (255, 255, 50)

    def spawn_target(self):
        """Spawn a new target."""
        margin = 50
        radius = random.randint(15, 30)

        # Choose random position away from ball
        while True:
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)

            # Check distance from ball
            dx = x - self.ball_pos[0]
            dy = y - self.ball_pos[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Ensure target isn't too close to ball
            if distance > 100:
                break

        # Choose target type
        target_type = "standard"
        value = 1

        rand = random.random()
        if rand > 0.9:
            target_type = "bonus"
            value = 3
        elif rand > 0.95:
            target_type = "speed"
            value = 1

        # Create target
        self.targets.append(
            {
                "x": x,
                "y": y,
                "radius": radius,
                "type": target_type,
                "value": value,
                "collected": False,
                "color": (0, 255, 0)
                if target_type == "standard"
                else (255, 255, 0)
                if target_type == "bonus"
                else (0, 255, 255),  # speed boost
            }
        )

    def spawn_obstacle(self):
        """Spawn a new obstacle."""
        margin = 100
        width = random.randint(30, 80)
        height = random.randint(30, 80)

        # Choose random position away from ball
        while True:
            x = random.randint(margin, self.width - margin - width)
            y = random.randint(margin, self.height - margin - height)

            # Check distance from ball
            dx = (x + width // 2) - self.ball_pos[0]
            dy = (y + height // 2) - self.ball_pos[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Ensure obstacle isn't too close to ball
            if distance > 150:
                break

        # Create obstacle
        self.obstacles.append(
            {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "color": (150, 75, 0),  # Brown
            }
        )

    def process_hand_tracking(self):
        """Process camera input to detect hand orientation."""
        ret, frame = self.camera.read()
        if not ret:
            return None

        # Flip horizontally for selfie view
        frame = cv2.flip(frame, 1)

        # First, try to detect and exclude face areas
        try:
            # Load face cascade if available
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Create a mask to exclude face areas
            face_mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255

            # Mark face areas in the mask
            for x, y, w, h in faces:
                # Draw rectangle around the face (for visualization)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Add some padding to make sure we exclude the entire face
                padding = 10
                x_start = max(0, x - padding)
                y_start = max(0, y - padding)
                x_end = min(frame.shape[1], x + w + padding)
                y_end = min(frame.shape[0], y + h + padding)

                # Exclude face area from processing
                face_mask[y_start:y_end, x_start:x_end] = 0

            # Add text when face is detected
            if len(faces) > 0:
                cv2.putText(
                    frame,
                    "Face detected - excluding from hand tracking",
                    (10, frame.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )
        except Exception as e:
            # If face detection fails, continue without it
            face_mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255
            print(f"Face detection error: {e}")

        # Process the frame with hand detector, passing the face mask
        hand_center, contour, direction_vector, processed_frame = (
            self.hand_detector.process_frame(frame, face_mask)
        )

        # Get current direction
        direction = self.hand_detector.get_direction()

        # Add user instructions
        cv2.putText(
            processed_frame,
            "Rotate your hand to control the ball direction",
            (10, processed_frame.shape[0] - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Display the frame
        cv2.namedWindow("Hand Orientation", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Hand Orientation", 640, 480)
        cv2.imshow("Hand Orientation", processed_frame)

        # Return direction vector
        return direction_vector

    def update(self, delta_time):
        """Update game state."""
        # Process hand tracking to get direction vector
        direction_vector = self.process_hand_tracking()
        self.direction_vector = direction_vector

        # Update ball velocity based on hand orientation
        if direction_vector:
            # Set ball velocity based on hand orientation
            self.ball_velocity[0] = direction_vector[0] * self.ball_speed
            self.ball_velocity[1] = direction_vector[1] * self.ball_speed
        else:
            # Slow down if no direction (gradual stop)
            self.ball_velocity[0] *= 0.95
            self.ball_velocity[1] *= 0.95

        # Update ball position
        self.ball_pos[0] += self.ball_velocity[0]
        self.ball_pos[1] += self.ball_velocity[1]

        # Keep ball within screen bounds
        if self.ball_pos[0] < self.ball_radius:
            self.ball_pos[0] = self.ball_radius
            self.ball_velocity[0] *= -0.5  # Bounce with damping
        elif self.ball_pos[0] > self.width - self.ball_radius:
            self.ball_pos[0] = self.width - self.ball_radius
            self.ball_velocity[0] *= -0.5  # Bounce with damping

        if self.ball_pos[1] < self.ball_radius:
            self.ball_pos[1] = self.ball_radius
            self.ball_velocity[1] *= -0.5  # Bounce with damping
        elif self.ball_pos[1] > self.height - self.ball_radius:
            self.ball_pos[1] = self.height - self.ball_radius
            self.ball_velocity[1] *= -0.5  # Bounce with damping

        # Spawn targets timer
        self.spawn_target_timer += delta_time
        if self.spawn_target_timer >= self.spawn_target_delay:
            self.spawn_target()
            self.spawn_target_timer = 0

        # Spawn obstacles timer
        self.spawn_obstacle_timer += delta_time
        if self.spawn_obstacle_timer >= self.spawn_obstacle_delay:
            self.spawn_obstacle()
            self.spawn_obstacle_timer = 0

        # Check for collisions with targets
        for target in self.targets[:]:
            # Distance between ball and target
            dx = target["x"] - self.ball_pos[0]
            dy = target["y"] - self.ball_pos[1]
            distance = math.sqrt(dx**2 + dy**2)

            # If ball touches target
            if distance < self.ball_radius + target["radius"]:
                # Handle target collection
                if target["type"] == "speed":
                    # Speed boost
                    self.ball_speed = min(10, self.ball_speed + 1)
                else:
                    # Add score
                    self.score += target["value"]

                # Remove target
                self.targets.remove(target)

        # Check for collisions with obstacles
        for obstacle in self.obstacles:
            # Check if ball intersects with obstacle
            circle_dist_x = abs(
                self.ball_pos[0] - (obstacle["x"] + obstacle["width"] / 2)
            )
            circle_dist_y = abs(
                self.ball_pos[1] - (obstacle["y"] + obstacle["height"] / 2)
            )

            if circle_dist_x > (
                obstacle["width"] / 2 + self.ball_radius
            ) or circle_dist_y > (obstacle["height"] / 2 + self.ball_radius):
                # No collision
                continue

            if (
                circle_dist_x <= obstacle["width"] / 2
                or circle_dist_y <= obstacle["height"] / 2
            ):
                # Collision with obstacle edges
                self.game_state = "game_over"
                return

            # Check for collision with obstacle corners
            corner_dist = (circle_dist_x - obstacle["width"] / 2) ** 2 + (
                circle_dist_y - obstacle["height"] / 2
            ) ** 2

            if corner_dist <= (self.ball_radius**2):
                # Collision with obstacle corner
                self.game_state = "game_over"
                return

    def draw(self):
        """Draw game elements."""
        # Fill background
        self.screen.fill(self.BLACK)

        # Draw targets
        for target in self.targets:
            pygame.draw.circle(
                self.screen,
                target["color"],
                (int(target["x"]), int(target["y"])),
                target["radius"],
            )

        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen,
                obstacle["color"],
                (
                    int(obstacle["x"]),
                    int(obstacle["y"]),
                    int(obstacle["width"]),
                    int(obstacle["height"]),
                ),
            )

        # Draw ball
        pygame.draw.circle(
            self.screen,
            self.ball_color,
            (int(self.ball_pos[0]), int(self.ball_pos[1])),
            self.ball_radius,
        )

        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_state == "game_over":
            # Darken background
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(180)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))

            # Game over text
            game_over_text = self.font_large.render("Game Over", True, self.RED)
            score_text = self.font_medium.render(
                f"Score: {self.score}", True, self.WHITE
            )
            restart_text = self.font_small.render(
                "Press SPACE to restart", True, self.WHITE
            )

            # Position text
            game_over_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            score_rect = score_text.get_rect(
                center=(self.width // 2, self.height // 2 + 10)
            )
            restart_rect = restart_text.get_rect(
                center=(self.width // 2, self.height // 2 + 60)
            )

            # Draw text
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        last_time = time.time()

        while self.running:
            # Calculate delta time
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE and self.game_state == "game_over":
                        # Reset game
                        self.game_state = "playing"
                        self.score = 0
                        self.ball_pos = [self.width // 2, self.height // 2]
                        self.ball_velocity = [0, 0]
                        self.ball_speed = 5
                        self.targets = []
                        self.obstacles = []
                        for _ in range(5):
                            self.spawn_target()
                        for _ in range(3):
                            self.spawn_obstacle()

            # Update game state if playing
            if self.game_state == "playing":
                self.update(delta_time)

            # Draw game
            self.draw()

            # Set target frame rate
            self.clock.tick(self.fps)

            # Process key for OpenCV windows
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                self.running = False

        # Clean up
        self.camera.release()
        cv2.destroyAllWindows()
        pygame.quit()


def main():
    """Run the game."""
    game = HandOrientationGame()
    game.run()


if __name__ == "__main__":
    main()
