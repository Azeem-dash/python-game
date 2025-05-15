#!/usr/bin/env python3
"""
Platformer Game using Hand Detection
A simple side-scrolling platformer game controlled by hand gestures.
"""

import math
import os
import random
import sys
import time

import cv2
import numpy as np
import pygame

# Add the src directory to path for importing SimpleHandDetector
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "src"))

from simple_detection import SimpleHandDetector


class PlatformerGame:
    """A simple 2D platformer game controlled by hand gestures."""

    def __init__(self):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()

        # Game window settings
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Gesture Platformer")

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.gravity = 0.8
        self.ground_level = self.height - 100

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.SKY_BLUE = (135, 206, 235)
        self.GREEN = (0, 150, 0)
        self.BROWN = (101, 67, 33)
        self.RED = (255, 0, 0)
        self.GOLD = (255, 215, 0)

        # Player character
        self.player = {
            "x": 100,
            "y": self.ground_level,
            "width": 40,
            "height": 60,
            "vel_y": 0,
            "vel_x": 0,
            "is_jumping": False,
            "color": (0, 0, 255),  # Blue player
            "facing_right": True,
        }

        # Platforms - each platform has x, y, width, height
        self.platforms = [
            {
                "x": 0,
                "y": self.ground_level,
                "width": self.width * 3,
                "height": 100,
            },  # Ground
            {"x": 200, "y": 400, "width": 100, "height": 20},
            {"x": 400, "y": 350, "width": 120, "height": 20},
            {"x": 600, "y": 300, "width": 100, "height": 20},
            {"x": 300, "y": 250, "width": 80, "height": 20},
            {"x": 100, "y": 200, "width": 120, "height": 20},
        ]

        # Obstacles - moving enemies or hazards
        self.obstacles = [
            {
                "x": 300,
                "y": self.ground_level - 30,
                "width": 30,
                "height": 30,
                "vel_x": 2,
                "range": 200,
                "start_x": 300,
            },
            {
                "x": 500,
                "y": self.ground_level - 30,
                "width": 30,
                "height": 30,
                "vel_x": -2,
                "range": 150,
                "start_x": 500,
            },
        ]

        # Collectibles - coins, power-ups, etc.
        self.collectibles = []
        self._generate_collectibles(20)  # Generate 20 collectibles

        # Game world properties
        self.world_offset = 0  # For scrolling
        self.max_world_offset = 2000  # How far the world extends to the right

        # Camera and hand tracking
        self.camera_index = 0  # Default camera
        self.cap = cv2.VideoCapture(self.camera_index)
        self.hand_detector = SimpleHandDetector()

        # Gesture controls
        self.last_gesture = "unknown"
        self.jump_cooldown = 0
        self.last_center_x = None

        # Background elements for better aesthetics
        self.clouds = []
        self._generate_clouds(10)

        # Font for text display
        self.font = pygame.font.SysFont("Arial", 24)

        # Sound effects
        self._load_sounds()

    def _generate_collectibles(self, count):
        """Generate collectibles throughout the level."""
        self.collectibles = []
        for _ in range(count):
            x = random.randint(100, self.width * 2)  # Spread across the level
            y = random.randint(100, self.ground_level - 150)  # Above ground level
            self.collectibles.append(
                {
                    "x": x,
                    "y": y,
                    "width": 20,
                    "height": 20,
                    "collected": False,
                    "type": "coin",  # Default type
                    "color": self.GOLD,
                    "value": 10,
                }
            )

    def _generate_clouds(self, count):
        """Generate decorative clouds in the background."""
        self.clouds = []
        for _ in range(count):
            x = random.randint(0, self.width * 3)
            y = random.randint(50, 200)
            width = random.randint(60, 120)
            height = random.randint(30, 50)
            speed = random.uniform(0.2, 0.5)
            self.clouds.append(
                {"x": x, "y": y, "width": width, "height": height, "speed": speed}
            )

    def _load_sounds(self):
        """Load game sound effects."""
        self.sounds = {}
        try:
            self.sounds["jump"] = pygame.mixer.Sound(
                os.path.join(script_dir, "assets", "jump.wav")
            )
            self.sounds["coin"] = pygame.mixer.Sound(
                os.path.join(script_dir, "assets", "coin.wav")
            )
            self.sounds["game_over"] = pygame.mixer.Sound(
                os.path.join(script_dir, "assets", "game_over.wav")
            )

            # Set volume lower
            for sound in self.sounds.values():
                sound.set_volume(0.3)
        except:
            print(
                "Warning: Could not load sound files. Game will continue without sound."
            )

    def detect_hand(self):
        """Process camera input to detect hand and control the game."""
        ret, frame = self.cap.read()
        if not ret:
            return False

        # Flip horizontally for more intuitive controls
        frame = cv2.flip(frame, 1)

        # Process the frame to get hand position and gesture - explicitly pass None for face_mask to disable face detection
        hand_center, contour, processed_frame = self.hand_detector.process_frame(
            frame, face_mask=None
        )

        if hand_center and contour is not None:
            # Get the gesture
            gesture = self.hand_detector.get_gesture()

            # Get hand orientation for directional control
            orientation = self._detect_hand_orientation(contour, hand_center)

            # Draw orientation indicator on processed frame
            if orientation:
                direction, angle = orientation
                end_x = hand_center[0] + int(50 * math.cos(angle))
                end_y = hand_center[1] + int(50 * math.sin(angle))
                cv2.line(processed_frame, hand_center, (end_x, end_y), (0, 255, 0), 2)
                cv2.putText(
                    processed_frame,
                    f"Direction: {direction}",
                    (hand_center[0] - 50, hand_center[1] - 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

            # Control character based on hand orientation and gesture
            if orientation:
                direction, _ = orientation
                # Movement based on pointing direction, not hand position
                if direction == "left":
                    self.player["vel_x"] = -5  # Move left at constant speed
                    self.player["facing_right"] = False
                elif direction == "right":
                    self.player["vel_x"] = 5  # Move right at constant speed
                    self.player["facing_right"] = True
                elif direction == "up" or direction == "down":
                    # Gradually slow down when pointing up or down
                    self.player["vel_x"] *= 0.8

            # Use closed fist gesture for jumping
            if (
                gesture == "closed_fist"
                and not self.player["is_jumping"]
                and self.jump_cooldown <= 0
            ):
                self.player["vel_y"] = -15  # Jump velocity
                self.player["is_jumping"] = True
                self.jump_cooldown = 20  # Prevent jump spam
                if "jump" in self.sounds:
                    self.sounds["jump"].play()

            self.last_gesture = gesture

        # Display the processed frame with hand detection
        cv2.imshow("Hand Detection", processed_frame)

        # Check for 'q' key to quit
        key = cv2.waitKey(1)
        if key & 0xFF == ord("q"):
            return False

        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        return True

    def _detect_hand_orientation(self, contour, hand_center):
        """Detect the orientation of the hand based on its contour.

        Returns:
            tuple: (direction, angle) or None if can't determine
        """
        if contour is None or len(contour) < 5:
            return None

        try:
            # Find extreme points of contour
            leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
            rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
            topmost = tuple(contour[contour[:, :, 1].argmin()][0])
            bottommost = tuple(contour[contour[:, :, 1].argmax()][0])

            # Find fingertip (most likely to be the pointing finger)
            # First try to find it based on convexity defects
            fingertip = None

            # Get convex hull and convexity defects
            hull = cv2.convexHull(contour, returnPoints=False)
            if len(hull) >= 3:
                try:
                    defects = cv2.convexityDefects(contour, hull)

                    if defects is not None and len(defects) > 0:
                        # Find potential fingertips
                        finger_candidates = []

                        for i in range(defects.shape[0]):
                            s, e, f, d = defects[i, 0]
                            start = tuple(contour[s][0])
                            end = tuple(contour[e][0])
                            far = tuple(contour[f][0])

                            # Calculate distances
                            start_to_center = math.dist(start, hand_center)
                            end_to_center = math.dist(end, hand_center)

                            # Add points that are likely fingertips (far from center)
                            if start_to_center > 30:  # Threshold to avoid wrist points
                                finger_candidates.append((start, start_to_center))
                            if end_to_center > 30:
                                finger_candidates.append((end, end_to_center))

                        # Get the point furthest from center (most likely fingertip)
                        if finger_candidates:
                            fingertip, _ = max(finger_candidates, key=lambda x: x[1])
                except:
                    pass

            # If convexity defects method failed, use extreme points
            if fingertip is None:
                # Calculate distances from center to extreme points
                distances = [
                    (leftmost, math.dist(leftmost, hand_center)),
                    (rightmost, math.dist(rightmost, hand_center)),
                    (topmost, math.dist(topmost, hand_center)),
                    (bottommost, math.dist(bottommost, hand_center)),
                ]

                # Extreme point furthest from center is likely the fingertip
                fingertip, _ = max(distances, key=lambda x: x[1])

            # Calculate direction vector from center to fingertip
            dx = fingertip[0] - hand_center[0]
            dy = fingertip[1] - hand_center[1]

            # Calculate angle
            angle = math.atan2(dy, dx)

            # Determine direction based on angle
            # Divide the circle into 4 quadrants
            if -math.pi / 4 <= angle <= math.pi / 4:
                direction = "right"
            elif math.pi / 4 < angle <= 3 * math.pi / 4:
                direction = "down"
            elif -3 * math.pi / 4 <= angle < -math.pi / 4:
                direction = "up"
            else:  # angle > 3*math.pi/4 or angle < -3*math.pi/4
                direction = "left"

            return (direction, angle)

        except Exception as e:
            print(f"Error detecting hand orientation: {e}")
            return None

    def update(self):
        """Update game state."""
        # Update player
        self._update_player()

        # Update obstacles
        self._update_obstacles()

        # Update clouds
        self._update_clouds()

        # Check collisions
        self._check_collisions()

        # Update camera position (world scrolling)
        self._update_camera()

    def _update_player(self):
        """Update player position and state."""
        # Apply gravity
        self.player["vel_y"] += self.gravity

        # Update position
        self.player["x"] += self.player["vel_x"]
        self.player["y"] += self.player["vel_y"]

        # Horizontal bounds checking
        if self.player["x"] < 0:
            self.player["x"] = 0
        elif self.player["x"] > self.width - self.player["width"]:
            self.player["x"] = self.width - self.player["width"]

        # Apply friction
        self.player["vel_x"] *= 0.9

        # Bounds checking - if player falls below screen
        if self.player["y"] > self.height:
            self.game_over = True
            if "game_over" in self.sounds:
                self.sounds["game_over"].play()

    def _update_obstacles(self):
        """Update positions of moving obstacles."""
        for obstacle in self.obstacles:
            # Move obstacle back and forth
            obstacle["x"] += obstacle["vel_x"]

            # Check bounds and reverse direction if needed
            if (obstacle["x"] > obstacle["start_x"] + obstacle["range"]) or (
                obstacle["x"] < obstacle["start_x"] - obstacle["range"]
            ):
                obstacle["vel_x"] *= -1

    def _update_clouds(self):
        """Update cloud positions for parallax scrolling effect."""
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"]

            # Wrap clouds around when they go off screen
            if cloud["x"] + cloud["width"] < -self.world_offset:
                cloud["x"] = self.width + self.world_offset

    def _check_collisions(self):
        """Check for collisions with platforms, obstacles, and collectibles."""
        # Player rect for collision detection
        player_rect = pygame.Rect(
            self.player["x"] - self.world_offset,
            self.player["y"],
            self.player["width"],
            self.player["height"],
        )

        # Platform collisions
        self.player["is_jumping"] = True  # Assume in air until proven on platform
        for platform in self.platforms:
            platform_rect = pygame.Rect(
                platform["x"] - self.world_offset,
                platform["y"],
                platform["width"],
                platform["height"],
            )

            # Check if player is on top of platform
            if (
                player_rect.bottom >= platform_rect.top
                and player_rect.bottom
                <= platform_rect.top + 20  # Only detect top collisions
                and player_rect.right > platform_rect.left
                and player_rect.left < platform_rect.right
                and self.player["vel_y"] > 0
            ):  # Only when falling
                self.player["y"] = platform_rect.top - self.player["height"]
                self.player["vel_y"] = 0
                self.player["is_jumping"] = False

        # Obstacle collisions
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(
                obstacle["x"] - self.world_offset,
                obstacle["y"],
                obstacle["width"],
                obstacle["height"],
            )

            if player_rect.colliderect(obstacle_rect):
                self.game_over = True
                if "game_over" in self.sounds:
                    self.sounds["game_over"].play()

        # Collectible collisions
        for collectible in self.collectibles:
            if not collectible["collected"]:
                collectible_rect = pygame.Rect(
                    collectible["x"] - self.world_offset,
                    collectible["y"],
                    collectible["width"],
                    collectible["height"],
                )

                if player_rect.colliderect(collectible_rect):
                    collectible["collected"] = True
                    self.score += collectible["value"]
                    if "coin" in self.sounds:
                        self.sounds["coin"].play()

    def _update_camera(self):
        """Update the camera position for scrolling."""
        # Follow player but keep them in the 1/3 of the screen
        target_offset = max(0, self.player["x"] - self.width // 3)
        target_offset = min(target_offset, self.max_world_offset)

        # Smooth camera movement
        self.world_offset += (target_offset - self.world_offset) * 0.1

    def draw(self):
        """Draw the game elements."""
        # Fill background
        self.screen.fill(self.SKY_BLUE)

        # Draw clouds (background)
        for cloud in self.clouds:
            pygame.draw.ellipse(
                self.screen,
                self.WHITE,
                (
                    cloud["x"] - self.world_offset * 0.3,
                    cloud["y"],
                    cloud["width"],
                    cloud["height"],
                ),
            )

        # Draw ground and platforms
        for platform in self.platforms:
            platform_color = (
                self.GREEN if platform["y"] == self.ground_level else self.BROWN
            )
            pygame.draw.rect(
                self.screen,
                platform_color,
                (
                    platform["x"] - self.world_offset,
                    platform["y"],
                    platform["width"],
                    platform["height"],
                ),
            )

            # Add grass detail to ground
            if platform["y"] == self.ground_level:
                pygame.draw.rect(
                    self.screen,
                    (0, 180, 0),  # Brighter green for grass
                    (
                        platform["x"] - self.world_offset,
                        platform["y"],
                        platform["width"],
                        10,
                    ),
                )

        # Draw collectibles
        for collectible in self.collectibles:
            if not collectible["collected"]:
                pygame.draw.rect(
                    self.screen,
                    collectible["color"],
                    (
                        collectible["x"] - self.world_offset,
                        collectible["y"],
                        collectible["width"],
                        collectible["height"],
                    ),
                )

        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen,
                self.RED,
                (
                    obstacle["x"] - self.world_offset,
                    obstacle["y"],
                    obstacle["width"],
                    obstacle["height"],
                ),
            )

        # Draw player character
        pygame.draw.rect(
            self.screen,
            self.player["color"],
            (
                self.player["x"] - self.world_offset,
                self.player["y"],
                self.player["width"],
                self.player["height"],
            ),
        )

        # Draw simple face on player
        eye_size = 5
        eye_offset_x = 10 if self.player["facing_right"] else self.player["width"] - 15

        # Eyes
        pygame.draw.circle(
            self.screen,
            self.WHITE,
            (
                int(self.player["x"] - self.world_offset + eye_offset_x),
                int(self.player["y"] + 15),
            ),
            eye_size,
        )

        # Mouth
        mouth_offset = 5 if self.player["facing_right"] else -5
        pygame.draw.arc(
            self.screen,
            self.WHITE,
            (
                int(
                    self.player["x"]
                    - self.world_offset
                    + eye_offset_x
                    - 10
                    + mouth_offset
                ),
                int(self.player["y"] + 25),
                20,
                15,
            ),
            0,
            math.pi,
            2,
        )

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw gesture info
        gesture_text = self.font.render(
            f"Gesture: {self.last_gesture}", True, self.WHITE
        )
        self.screen.blit(gesture_text, (20, 50))

        # Game over screen
        if self.game_over:
            self._draw_game_over()

        # Update display
        pygame.display.flip()

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_font = pygame.font.SysFont("Arial", 64)
        game_over_text = game_over_font.render("GAME OVER", True, self.WHITE)
        self.screen.blit(
            game_over_text,
            (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 50),
        )

        # Score text
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        self.screen.blit(
            score_text,
            (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 20),
        )

        # Restart instructions
        restart_text = self.font.render("Press SPACE to restart", True, self.WHITE)
        self.screen.blit(
            restart_text,
            (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 60),
        )

    def reset_game(self):
        """Reset the game state."""
        self.game_over = False
        self.score = 0
        self.world_offset = 0

        # Reset player
        self.player["x"] = 100
        self.player["y"] = self.ground_level - self.player["height"]
        self.player["vel_x"] = 0
        self.player["vel_y"] = 0
        self.player["is_jumping"] = False

        # Reset collectibles
        self._generate_collectibles(20)

        # Reset obstacles to initial positions
        for obstacle in self.obstacles:
            obstacle["x"] = obstacle["start_x"]

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

    def run(self):
        """Main game loop."""
        print("=" * 50)
        print("PLATFORMER GAME - HAND CONTROLLED")
        print("=" * 50)
        print("\nCONTROLS:")
        print("- Point your finger LEFT: Move character left")
        print("- Point your finger RIGHT: Move character right")
        print("- Make a CLOSED FIST: Jump")
        print("- Press ESC or 'q' to quit")
        print("- Press SPACE to restart after game over")
        print("\nOBJECTIVE:")
        print("- Collect gold coins to score points")
        print("- Avoid red obstacles")
        print("- Don't fall off the platforms!")
        print("\nInitializing camera and hand tracking...")

        try:
            while self.running:
                # Process camera input
                if not self.detect_hand():
                    self.running = False
                    break

                # Handle pygame events
                self.handle_events()

                # Skip game updates if game over
                if not self.game_over:
                    self.update()

                # Draw everything
                self.draw()

                # Cap the frame rate
                self.clock.tick(self.fps)

        except Exception as e:
            print(f"Error in game loop: {e}")
        finally:
            # Clean up
            pygame.quit()
            cv2.destroyAllWindows()
            self.cap.release()


def main():
    """Run the platformer game."""
    # Create assets directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    game = PlatformerGame()
    game.run()


if __name__ == "__main__":
    main()
