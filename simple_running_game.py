import os
import random
import sys
import time

import cv2
import numpy as np


class SimpleRunningGame:
    def __init__(self):
        # Game window setup
        self.width = 800
        self.height = 600
        self.window = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Game state
        self.game_over = False
        self.score = 0
        self.speed = 5
        self.lane_width = self.width // 3
        self.lanes = [
            self.lane_width // 2,
            self.width // 2,
            self.width - self.lane_width // 2,
        ]
        self.current_lane = 1  # Start in middle lane

        # Player
        self.player_width = 50
        self.player_height = 80
        self.player_y = self.height - self.player_height - 20

        # Obstacles
        self.obstacles = []
        self.obstacle_types = ["barrier", "hole"]
        self.obstacle_width = 60
        self.obstacle_height = 60
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_delay = 60  # frames

        # Coins
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_spawn_delay = 30  # frames

        # Game elements
        self.background = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.draw_road()

        # Hand tracking
        self.prev_hand_x = None
        self.movement_threshold = 50

    def draw_road(self):
        # Draw road
        cv2.rectangle(
            self.background, (0, 0), (self.width, self.height), (50, 50, 50), -1
        )

        # Draw lane markers
        for i in range(1, 3):
            x = i * self.lane_width
            for y in range(0, self.height, 40):
                cv2.rectangle(
                    self.background, (x - 2, y), (x + 2, y + 20), (255, 255, 255), -1
                )

    def spawn_obstacle(self):
        lane = random.randint(0, 2)
        obstacle_type = random.choice(self.obstacle_types)
        self.obstacles.append(
            {
                "x": self.lanes[lane] - self.obstacle_width // 2,
                "y": -self.obstacle_height,
                "type": obstacle_type,
                "lane": lane,
            }
        )

    def spawn_coin(self):
        lane = random.randint(0, 2)
        self.coins.append({"x": self.lanes[lane] - 15, "y": -30, "lane": lane})

    def update_obstacles(self):
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle["y"] += self.speed
            if obstacle["y"] > self.height:
                self.obstacles.remove(obstacle)
                self.score += 1

        # Spawn new obstacles
        self.obstacle_spawn_timer += 1
        if self.obstacle_spawn_timer >= self.obstacle_spawn_delay:
            self.spawn_obstacle()
            self.obstacle_spawn_timer = 0

    def update_coins(self):
        # Update coins
        for coin in self.coins[:]:
            coin["y"] += self.speed
            if coin["y"] > self.height:
                self.coins.remove(coin)

        # Spawn new coins
        self.coin_spawn_timer += 1
        if self.coin_spawn_timer >= self.coin_spawn_delay:
            self.spawn_coin()
            self.coin_spawn_timer = 0

    def check_collisions(self):
        player_rect = {
            "x": self.lanes[self.current_lane] - self.player_width // 2,
            "y": self.player_y,
            "width": self.player_width,
            "height": self.player_height,
        }

        # Check obstacle collisions
        for obstacle in self.obstacles:
            if (
                abs(obstacle["x"] - player_rect["x"]) < self.obstacle_width
                and abs(obstacle["y"] - player_rect["y"]) < self.obstacle_height
            ):
                self.game_over = True
                return

        # Check coin collisions
        for coin in self.coins[:]:
            if (
                abs(coin["x"] - player_rect["x"]) < 30
                and abs(coin["y"] - player_rect["y"]) < 30
            ):
                self.coins.remove(coin)
                self.score += 5

    def process_hand_movement(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply threshold to detect hand
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            # Get the largest contour (assumed to be the hand)
            largest_contour = max(contours, key=cv2.contourArea)

            # Get the center of the hand
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                hand_x = int(M["m10"] / M["m00"])

                if self.prev_hand_x is not None:
                    movement = hand_x - self.prev_hand_x

                    # Change lane based on movement
                    if abs(movement) > self.movement_threshold:
                        if movement > 0 and self.current_lane < 2:  # Move right
                            self.current_lane += 1
                        elif movement < 0 and self.current_lane > 0:  # Move left
                            self.current_lane -= 1

                self.prev_hand_x = hand_x
            else:
                self.prev_hand_x = None
        else:
            self.prev_hand_x = None

    def draw_game(self):
        # Draw background
        self.window = self.background.copy()

        # Draw player
        player_x = self.lanes[self.current_lane] - self.player_width // 2
        cv2.rectangle(
            self.window,
            (player_x, self.player_y),
            (player_x + self.player_width, self.player_y + self.player_height),
            (0, 255, 0),
            -1,
        )

        # Draw obstacles
        for obstacle in self.obstacles:
            color = (0, 0, 255) if obstacle["type"] == "barrier" else (0, 0, 0)
            cv2.rectangle(
                self.window,
                (obstacle["x"], obstacle["y"]),
                (
                    obstacle["x"] + self.obstacle_width,
                    obstacle["y"] + self.obstacle_height,
                ),
                color,
                -1,
            )

        # Draw coins
        for coin in self.coins:
            cv2.circle(
                self.window, (coin["x"] + 15, coin["y"] + 15), 15, (0, 255, 255), -1
            )

        # Draw score
        cv2.putText(
            self.window,
            f"Score: {self.score}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        if self.game_over:
            cv2.putText(
                self.window,
                "GAME OVER",
                (self.width // 2 - 100, self.height // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 0, 255),
                3,
            )

    def run(self):
        # Get camera index from environment variable or use default
        try:
            camera_index = int(os.environ.get("GAME_CAMERA_INDEX", 0))
            print(f"Using camera index: {camera_index}")
        except ValueError:
            camera_index = 0
            print(f"Invalid camera index format. Using default: {camera_index}")

        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(
                f"Error: Could not open camera {camera_index}. Trying fallback to camera 0..."
            )
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Could not open any camera.")
                return

        print("Running the Simple Running Game...")
        print("Move your hand left/right to change lanes")
        print("Press 'q' to quit")

        while cap.isOpened() and not self.game_over:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip frame horizontally
            frame = cv2.flip(frame, 1)

            # Process hand movement
            self.process_hand_movement(frame)

            # Update game state
            self.update_obstacles()
            self.update_coins()
            self.check_collisions()

            # Draw game
            self.draw_game()

            # Show game window
            cv2.imshow("Running Game", self.window)

            # Show camera feed
            cv2.imshow("Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    game = SimpleRunningGame()
    game.run()
