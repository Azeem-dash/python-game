import os
import random
import sys
import time

import cv2
import numpy as np
import pygame
from game_objects import Character, Obstacle, ParticleSystem, Target
from hand_gestures import HandGestureRecognizer


class HandMotionGame:
    """Main game class that integrates hand tracking with gameplay."""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width, self.height = 1024, 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Motion Adventure")

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

        # Set up hand gesture recognizer
        self.hand_recognizer = HandGestureRecognizer()

        # Game state
        self.running = True
        self.game_state = "title"  # title, playing, game_over
        self.score = 0
        self.level = 1
        self.lives = 3
        self.time_remaining = 60  # seconds
        self.invulnerable_time = 0

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
        self.hand_landmarks = None
        self.prev_hand_position = None
        self.current_hand_position = None
        self.current_gesture = None

        # Load assets
        self.load_assets()

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

    def load_assets(self):
        """Load game assets like images and sounds."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        assets_dir = os.path.join(project_root, "assets")

        # Load background image
        try:
            self.background = pygame.image.load(
                os.path.join(assets_dir, "background.png")
            )
            self.background = pygame.transform.scale(
                self.background, (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # Create a simple gradient background if image can't be loaded
            self.background = self.create_gradient_background(
                (20, 20, 50), (50, 50, 100)
            )

        # Load title screen image
        try:
            self.title_screen = pygame.image.load(
                os.path.join(assets_dir, "title_screen.png")
            )
            self.title_screen = pygame.transform.scale(
                self.title_screen, (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # Use background as title screen if image can't be loaded
            self.title_screen = self.background

        # Load game over screen image
        try:
            self.game_over_screen = pygame.image.load(
                os.path.join(assets_dir, "game_over.png")
            )
            self.game_over_screen = pygame.transform.scale(
                self.game_over_screen, (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # Use background as game over screen if image can't be loaded
            self.game_over_screen = self.background

        # Load sound effects
        try:
            pygame.mixer.init()
            self.sounds = {
                "collect": pygame.mixer.Sound(os.path.join(assets_dir, "collect.wav")),
                "hit": pygame.mixer.Sound(os.path.join(assets_dir, "hit.wav")),
                "level_up": pygame.mixer.Sound(
                    os.path.join(assets_dir, "level_up.wav")
                ),
                "game_over": pygame.mixer.Sound(
                    os.path.join(assets_dir, "game_over.wav")
                ),
            }
        except (pygame.error, FileNotFoundError):
            # Create empty sounds dict if sounds can't be loaded
            self.sounds = {}

    def create_gradient_background(self, color1, color2):
        """Create a simple gradient background."""
        background = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            # Calculate the gradient ratio
            ratio = y / self.height
            # Interpolate colors
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            # Draw line with calculated color
            pygame.draw.line(background, (r, g, b), (0, y), (self.width, y))
        return background

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

        # Play level up sound if not first level
        if level > 1 and "level_up" in self.sounds:
            self.sounds["level_up"].play()

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

        # Determine if obstacle should move based on level
        moving = random.random() < 0.2 * self.level
        speed = random.uniform(50, 100) if moving else 0

        # Create obstacle
        self.obstacles.append(Obstacle(x, y, width, height, speed, moving))

    def process_hand_tracking(self):
        """Process webcam input and track hands."""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Flip the frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)

        # Resize for display
        display_frame = cv2.resize(frame, (320, 240))

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe (in hand_recognizer)
        import mediapipe as mp

        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as hands:
            results = hands.process(rgb_frame)

            # Draw hand landmarks on the frame
            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        display_frame,
                        hand_landmark,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style(),
                    )

                # Store the first hand landmarks
                self.hand_landmarks = results.multi_hand_landmarks[0]

                # Get hand position
                self.prev_hand_position = self.current_hand_position
                self.current_hand_position = self.hand_recognizer.get_hand_position(
                    self.hand_landmarks, frame.shape[1], frame.shape[0]
                )

                # Recognize gesture
                self.current_gesture = self.hand_recognizer.recognize_gesture(
                    self.hand_landmarks
                )

                # Update character based on hand tracking
                if self.current_hand_position:
                    # Map hand coordinates to screen coordinates
                    screen_x = int(
                        self.current_hand_position[0] * self.width / frame.shape[1]
                    )
                    screen_y = int(
                        self.current_hand_position[1] * self.height / frame.shape[0]
                    )

                    # Update character target position
                    self.character.set_target_position((screen_x, screen_y))

                # Update character gesture
                if self.current_gesture:
                    self.character.set_gesture(self.current_gesture)
            else:
                self.hand_landmarks = None
                self.current_gesture = None

        # Display the processed frame
        cv2.imshow("Hand Tracking", display_frame)
        cv2.moveWindow("Hand Tracking", 0, 0)

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
            if self.invulnerable_time > 0:
                self.invulnerable_time -= self.delta_time
            else:
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

                # Create particle effect
                color = target.colors.get(target.type, (0, 255, 0))
                self.particle_system.add_explosion(target.x, target.y, color, count=15)

                # Play sound effect
                if "collect" in self.sounds:
                    self.sounds["collect"].play()

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
        self.invulnerable_time = 2.0  # 2 seconds of invulnerability

        # Create particle effect at character position
        self.particle_system.add_explosion(
            self.character.x, self.character.y, self.RED, count=30, size=8, life=1.5
        )

        # Play hit sound
        if "hit" in self.sounds:
            self.sounds["hit"].play()

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

        # Play game over sound
        if "game_over" in self.sounds:
            self.sounds["game_over"].play()

    def draw(self):
        """Draw the game state to the screen."""
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
        # Draw background
        self.screen.blit(self.title_screen, (0, 0))

        # Draw title
        title_text = self.font_large.render("Hand Motion Adventure", True, self.WHITE)
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
        # Draw background
        self.screen.blit(self.background, (0, 0))

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
        # Draw background
        self.screen.blit(self.game_over_screen, (0, 0))

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


if __name__ == "__main__":
    game = HandMotionGame()
    game.run()
