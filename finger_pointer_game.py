#!/usr/bin/env python3
"""
Finger Pointer Game
Control a ball by pointing your finger in different directions.
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

# Import hand detector
try:
    from src.simple_detection import SimpleHandDetector
except ImportError:
    print("ERROR: Could not import SimpleHandDetector")
    sys.exit(1)


class FingerPointerGame:
    """Game controlled by pointing finger direction."""

    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Finger Direction Game")

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
        self.hand_detector = SimpleHandDetector()

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

        # Finger pointing properties
        self.pointing_direction = None

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
        """Process camera input to detect hand direction."""
        ret, frame = self.camera.read()
        if not ret:
            return None

        # Flip horizontally for selfie view
        frame = cv2.flip(frame, 1)

        # Create a copy for processing
        processing_frame = frame.copy()

        # FACE DETECTION DISABLED - Create a full mask (no areas excluded)
        face_mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255

        # Add note about disabled face detection
        cv2.putText(
            processing_frame,
            "Face detection disabled - focusing only on finger pointing",
            (10, processing_frame.shape[0] - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Process the frame with hand detector, passing the full mask
        hand_center, contour, processed_frame = self.hand_detector.process_frame(
            frame, face_mask
        )

        # Get current gesture
        gesture = self.hand_detector.get_gesture()

        # Initialize direction
        direction = None

        # Process if we have a hand contour
        if hand_center and contour is not None:
            try:
                # Find convex hull and defects for finger detection
                if cv2.contourArea(contour) > 3000:
                    # Get convex hull of hand contour
                    hull = cv2.convexHull(contour, returnPoints=False)

                    # Ensure hull is not empty
                    if len(hull) >= 3:
                        # Find convexity defects
                        defects = cv2.convexityDefects(contour, hull)

                        if defects is not None:
                            # Find the fingertip point (most extreme point from center)
                            finger_points = []
                            extreme_top = tuple(contour[contour[:, :, 1].argmin()][0])
                            extreme_bottom = tuple(
                                contour[contour[:, :, 1].argmax()][0]
                            )
                            extreme_left = tuple(contour[contour[:, :, 0].argmin()][0])
                            extreme_right = tuple(contour[contour[:, :, 0].argmax()][0])

                            # Draw extreme points for visualization
                            cv2.circle(processed_frame, extreme_top, 8, (0, 0, 255), -1)
                            cv2.circle(
                                processed_frame, extreme_bottom, 8, (255, 0, 0), -1
                            )
                            cv2.circle(
                                processed_frame, extreme_left, 8, (0, 255, 0), -1
                            )
                            cv2.circle(
                                processed_frame, extreme_right, 8, (255, 0, 255), -1
                            )

                            # Process defects to find fingertips
                            for i in range(defects.shape[0]):
                                s, e, f, d = defects[i, 0]
                                start = tuple(contour[s][0])
                                end = tuple(contour[e][0])
                                far = tuple(contour[f][0])

                                # Calculate angle between vectors
                                a = math.sqrt(
                                    (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
                                )
                                b = math.sqrt(
                                    (far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2
                                )
                                c = math.sqrt(
                                    (end[0] - far[0]) ** 2 + (end[1] - far[0]) ** 2
                                )

                                # Angle calculation
                                try:
                                    angle = math.acos(
                                        (b**2 + c**2 - a**2) / (2 * b * c)
                                    )
                                except:
                                    angle = math.pi

                                # If angle is small enough, it's likely a finger
                                if (
                                    angle <= math.pi / 2.5
                                ):  # Slightly stricter angle threshold
                                    # Add points if they're close to the extremes (more likely to be fingertips)
                                    dist_to_top = math.sqrt(
                                        (start[0] - extreme_top[0]) ** 2
                                        + (start[1] - extreme_top[1]) ** 2
                                    )
                                    if dist_to_top < 50:  # Close to top extreme point
                                        finger_points.append(start)

                                    dist_to_top = math.sqrt(
                                        (end[0] - extreme_top[0]) ** 2
                                        + (end[1] - extreme_top[1]) ** 2
                                    )
                                    if dist_to_top < 50:  # Close to top extreme point
                                        finger_points.append(end)

                            # If we didn't find good finger points, use extreme points
                            if not finger_points:
                                # Just use the extreme points as potential fingertips
                                finger_points = [
                                    extreme_top,
                                    extreme_right,
                                    extreme_left,
                                ]

                            # Find the point furthest from palm center (most likely to be pointing finger)
                            max_dist = 0
                            fingertip = None

                            for point in finger_points:
                                dist = math.sqrt(
                                    (point[0] - hand_center[0]) ** 2
                                    + (point[1] - hand_center[1]) ** 2
                                )
                                if dist > max_dist:
                                    max_dist = dist
                                    fingertip = point

                            if fingertip:
                                # Draw the fingertip with a larger, more visible circle
                                cv2.circle(
                                    processed_frame, fingertip, 12, (0, 255, 255), -1
                                )
                                cv2.putText(
                                    processed_frame,
                                    "Fingertip",
                                    (fingertip[0] + 10, fingertip[1]),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,
                                    (0, 255, 255),
                                    2,
                                )

                                # Calculate direction vector from hand center to fingertip
                                dx = fingertip[0] - hand_center[0]
                                dy = fingertip[1] - hand_center[1]

                                # Normalize
                                length = math.sqrt(dx**2 + dy**2)
                                if length > 0:
                                    direction = (dx / length, dy / length)

                                    # Draw the direction line with a thicker, more visible line
                                    end_point = (
                                        int(
                                            hand_center[0] + direction[0] * 150
                                        ),  # Longer line
                                        int(hand_center[1] + direction[1] * 150),
                                    )
                                    cv2.line(
                                        processed_frame,
                                        hand_center,
                                        end_point,
                                        (0, 255, 0),
                                        4,
                                    )  # Thicker green line
                                    cv2.arrowedLine(
                                        processed_frame,
                                        hand_center,
                                        fingertip,
                                        (255, 0, 255),
                                        3,
                                    )  # Add arrow for clarity

                    # If we couldn't get a direction from fingertip, fallback to hand orientation
                    if direction is None:
                        # Find rotated bounding rectangle
                        rect = cv2.minAreaRect(contour)
                        box = cv2.boxPoints(rect)
                        box = np.array(box, dtype=np.int32)

                        # Draw the rotated bounding box
                        cv2.drawContours(processed_frame, [box], 0, (0, 255, 0), 2)

                        # Get the angle of the rectangle
                        angle = rect[2]

                        # Convert rectangle angle to radians and get direction vector
                        # Note: OpenCV's angle is a bit unusual, we need to adjust it
                        if rect[1][0] < rect[1][1]:  # Width < Height
                            angle += 90

                        # Convert angle to radians
                        angle_rad = math.radians(angle)
                        direction = (math.cos(angle_rad), math.sin(angle_rad))

                        # Draw the direction line
                        line_length = 100
                        end_point = (
                            int(hand_center[0] + direction[0] * line_length),
                            int(hand_center[1] + direction[1] * line_length),
                        )
                        cv2.line(
                            processed_frame, hand_center, end_point, (255, 0, 255), 2
                        )
            except Exception as e:
                print(f"Error detecting finger direction: {e}")

        # Display information on frame
        gesture_text = f"Gesture: {gesture}" if gesture else "No gesture detected"
        cv2.putText(
            processed_frame,
            gesture_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        if direction:
            # Display the angle of hand in degrees for easier understanding
            angle = math.degrees(math.atan2(direction[1], direction[0]))
            # Convert from -180/180 to 0-360 format for clarity
            if angle < 0:
                angle += 360

            direction_text = f"Pointing Direction: {angle:.1f}°"
            cv2.putText(
                processed_frame,
                direction_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            # Add directional guidance
            direction_guide = ""
            if angle > 315 or angle < 45:
                direction_guide = "RIGHT"
            elif 45 <= angle < 135:
                direction_guide = "DOWN"
            elif 135 <= angle < 225:
                direction_guide = "LEFT"
            else:  # 225 <= angle < 315
                direction_guide = "UP"

            cv2.putText(
                processed_frame,
                direction_guide,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

        # Add user instructions
        cv2.putText(
            processed_frame,
            "Point your finger to control the ball direction",
            (10, processed_frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Display the frame
        cv2.namedWindow("Finger Pointing", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Finger Pointing", 640, 480)
        cv2.imshow("Finger Pointing", processed_frame)

        # Return direction
        return direction

    def update(self, delta_time):
        """Update game state."""
        # Process hand tracking to get pointing direction
        direction = self.process_hand_tracking()
        self.pointing_direction = direction

        # Update ball velocity based on pointing direction
        if direction:
            # Set ball velocity based on pointing direction
            self.ball_velocity[0] = direction[0] * self.ball_speed
            self.ball_velocity[1] = direction[1] * self.ball_speed
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
                # Collision
                # Bounce off obstacle
                if circle_dist_x <= obstacle["width"] / 2:
                    self.ball_velocity[1] *= -1
                else:
                    self.ball_velocity[0] *= -1

                # Move ball away from obstacle to prevent sticking
                norm = math.sqrt(
                    self.ball_velocity[0] ** 2 + self.ball_velocity[1] ** 2
                )
                if norm > 0:
                    self.ball_pos[0] += self.ball_velocity[0] / norm * 5
                    self.ball_pos[1] += self.ball_velocity[1] / norm * 5

    def draw(self):
        """Draw game elements."""
        # Clear screen
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
                (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]),
            )

        # Draw ball
        pygame.draw.circle(
            self.screen,
            self.ball_color,
            (int(self.ball_pos[0]), int(self.ball_pos[1])),
            self.ball_radius,
        )

        # Draw direction indicator if pointing
        if self.pointing_direction:
            # Calculate end point of direction line
            end_x = int(self.ball_pos[0] + self.pointing_direction[0] * 50)
            end_y = int(self.ball_pos[1] + self.pointing_direction[1] * 50)

            # Draw direction line
            pygame.draw.line(
                self.screen,
                self.YELLOW,
                (int(self.ball_pos[0]), int(self.ball_pos[1])),
                (end_x, end_y),
                3,
            )

        # Draw score
        score_text = self.font_small.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw instructions
        instructions = self.font_small.render(
            "Position your hand to direct the ball", True, self.WHITE
        )
        self.screen.blit(
            instructions, (self.width // 2 - instructions.get_width() // 2, 20)
        )

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        last_time = time.time()

        print("Game started! Show your hand to the camera to control the ball.")
        print(
            "The ball will move in the direction indicated by your hand's orientation."
        )
        print("Press 'q' in the camera window or ESC in the game window to quit.")

        try:
            while self.running:
                # Calculate delta time
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False

                # Update game state
                self.update(delta_time)

                # Draw game elements
                self.draw()

                # Cap frame rate
                self.clock.tick(self.fps)

                # Exit if 'q' is pressed in OpenCV window
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            # Clean up
            self.camera.release()
            cv2.destroyAllWindows()
            pygame.quit()
            print(f"Game ended. Final score: {self.score}")


def main():
    """Entry point for the game."""
    game = FingerPointerGame()
    game.run()


if __name__ == "__main__":
    main()
