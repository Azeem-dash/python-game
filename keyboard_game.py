#!/usr/bin/env python3
"""
Hand Motion Adventure Game - Keyboard Version
This version uses keyboard controls instead of webcam tracking.
"""

import math
import os
import random
import sys
import time

import pygame


class Character:
    """Game character controlled by keyboard."""

    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.velocity = [0, 0]
        self.max_speed = 5
        self.speed = 0
        self.color = (50, 50, 255)  # Blue
        self.is_attacking = False
        self.attack_cooldown = 0

    def update(self, delta_time, keys):
        """Update character position based on keyboard input."""
        # Handle key input
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx /= 1.414
            dy /= 1.414

        # Set speed based on shift key (sprint)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.max_speed * 1.5
        else:
            self.speed = self.max_speed

        # Apply movement
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep character within screen bounds
        self.x = max(self.size // 2, min(self.x, 800 - self.size // 2))
        self.y = max(self.size // 2, min(self.y, 600 - self.size // 2))

        # Handle attack (space key)
        if keys[pygame.K_SPACE] and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_cooldown = 0.5  # 0.5 second cooldown
        else:
            self.is_attacking = False

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time

    def get_rect(self):
        """Get character collision rectangle."""
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )

    def draw(self, screen):
        """Draw the character."""
        # Draw character
        pygame.draw.circle(
            screen, self.color, (int(self.x), int(self.y)), self.size // 2
        )

        # Draw attack effect
        if self.is_attacking:
            pygame.draw.circle(
                screen, (255, 200, 0), (int(self.x), int(self.y)), self.size, 3
            )


class Target:
    """Target object that the player needs to collect."""

    def __init__(self, x, y, size=30, value=1, target_type="standard"):
        self.x = x
        self.y = y
        self.size = size
        self.value = value
        self.type = target_type
        self.collected = False
        self.animation_time = 0

        # Choose color based on target type
        self.colors = {
            "standard": (0, 255, 0),  # Green
            "bonus": (255, 255, 0),  # Yellow
            "special": (255, 0, 255),  # Magenta
            "negative": (255, 0, 0),  # Red
        }

    def update(self, delta_time):
        """Update target animation."""
        self.animation_time += delta_time

    def draw(self, screen):
        """Draw the target."""
        if self.collected:
            return

        # Get color based on type
        color = self.colors.get(self.type, (0, 255, 0))

        # Apply pulsing effect
        pulse = math.sin(self.animation_time * 5) * 0.1 + 1
        size = int(self.size // 2 * pulse)

        # Draw target
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

    def get_rect(self):
        """Get target collision rectangle."""
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


class Obstacle:
    """Obstacle that the player needs to avoid."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (150, 75, 0)  # Brown

    def update(self, delta_time):
        """Update obstacle state."""
        pass

    def draw(self, screen):
        """Draw the obstacle."""
        pygame.draw.rect(
            screen, self.color, (int(self.x), int(self.y), self.width, self.height)
        )

    def get_rect(self):
        """Get obstacle collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class KeyboardGame:
    """Game class using keyboard controls."""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Set up display
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Motion Game - Keyboard Version")

        # Set up clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.delta_time = 0
        self.last_time = time.time()

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

        # Game timers
        self.target_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.target_spawn_delay = 1.5  # seconds
        self.obstacle_spawn_delay = 5.0  # seconds

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

        # Ensure target doesn't overlap with obstacles
        overlap = True
        attempts = 0

        while overlap and attempts < 10:
            overlap = False
            for obstacle in self.obstacles:
                # Check if target would overlap with obstacle
                if (
                    abs(x - (obstacle.x + obstacle.width / 2))
                    < (30 + obstacle.width) / 2
                    and abs(y - (obstacle.y + obstacle.height / 2))
                    < (30 + obstacle.height) / 2
                ):
                    overlap = True
                    x = random.randint(margin, self.width - margin)
                    y = random.randint(margin, self.height - margin)
                    break
            attempts += 1

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

        # Ensure obstacle doesn't spawn on player
        char_rect = self.character.get_rect()
        obstacle_rect = pygame.Rect(x, y, width, height)

        if obstacle_rect.colliderect(char_rect):
            # Move obstacle away from player
            if x < self.width // 2:
                x = margin
            else:
                x = self.width - width - margin

            if y < self.height // 2:
                y = margin
            else:
                y = self.height - height - margin

        # Create obstacle
        self.obstacles.append(Obstacle(x, y, width, height))

    def update(self):
        """Update game state."""
        # Calculate delta time
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time

        # Get keyboard state
        keys = pygame.key.get_pressed()

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
            self.character.update(self.delta_time, keys)

            # Update targets
            for target in self.targets:
                target.update(self.delta_time)

            # Update obstacles
            for obstacle in self.obstacles:
                obstacle.update(self.delta_time)

            # Check for collisions
            self.check_collisions()

            # Check for level completion (all targets collected)
            if len(self.targets) == 0:
                self.level_up()
        elif self.game_state == "title":
            # Start game with Enter key
            if keys[pygame.K_RETURN]:
                self.game_state = "playing"
        elif self.game_state == "game_over":
            # Restart game with R key
            if keys[pygame.K_r]:
                self.reset_game()

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

                # Play sound effect (if we had one)

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

        # Move character away from obstacles
        for obstacle in self.obstacles:
            obs_rect = obstacle.get_rect()
            char_rect = self.character.get_rect()

            if char_rect.colliderect(obs_rect):
                # Calculate direction to move character
                dx = self.character.x - (obstacle.x + obstacle.width / 2)
                dy = self.character.y - (obstacle.y + obstacle.height / 2)

                # Normalize direction
                dist = max(1, math.sqrt(dx * dx + dy * dy))
                dx /= dist
                dy /= dist

                # Move character away from obstacle
                self.character.x += dx * 20
                self.character.y += dy * 20

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

        # Draw keyboard version notice
        keyboard_text = self.font_medium.render("Keyboard Version", True, self.YELLOW)
        self.screen.blit(
            keyboard_text,
            (self.width // 2 - keyboard_text.get_width() // 2, self.height // 3 + 50),
        )

        # Draw instructions
        instructions = [
            "Use arrow keys or WASD to move",
            "Hold SHIFT to move faster",
            "Press SPACE to attack",
            "Collect targets and avoid obstacles",
            "Press ENTER to start",
        ]

        y_offset = self.height // 2
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.WHITE)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

    def draw_playing_screen(self):
        """Draw the main gameplay screen."""
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw targets
        for target in self.targets:
            target.draw(self.screen)

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
        restart_text = self.font_medium.render("Press R to Restart", True, self.YELLOW)
        self.screen.blit(
            restart_text,
            (self.width // 2 - restart_text.get_width() // 2, self.height * 3 // 4),
        )

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
            pygame.quit()


def main():
    """Main entry point for the game."""
    print("=" * 50)
    print("Hand Motion Game - Keyboard Version")
    print("=" * 50)
    print("This version uses keyboard controls instead of camera tracking.")
    print("Starting game...")

    try:
        # Check for pygame
        try:
            import pygame
        except ImportError:
            import pip

            print("Installing pygame...")
            pip.main(["install", "pygame"])
            import pygame

        game = KeyboardGame()
        game.run()
        return 0
    except Exception as e:
        print(f"Error running game: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
