import math
import os
import random

import pygame


class Character:
    """Game character controlled by hand gestures."""

    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 0
        self.max_speed = 10
        self.velocity = [0, 0]
        self.target_position = (x, y)
        self.gesture = None
        self.image = None
        self.rotation = 0
        self.health = 100
        self.power = 0
        self.is_attacking = False
        self.attack_cooldown = 0

        # Load character images for different gestures
        self.images = {}
        self.load_images()

    def load_images(self):
        """Load character images for different gestures."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        assets_dir = os.path.join(project_root, "assets")

        # Default image if others can't be loaded
        try:
            self.image = pygame.image.load(os.path.join(assets_dir, "character.png"))
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.images["default"] = self.image

            # Try to load gesture-specific images
            gestures = ["open_palm", "closed_fist", "pointing", "victory", "thumbs_up"]
            for gesture in gestures:
                try:
                    img = pygame.image.load(
                        os.path.join(assets_dir, f"character_{gesture}.png")
                    )
                    self.images[gesture] = pygame.transform.scale(
                        img, (self.size, self.size)
                    )
                except (pygame.error, FileNotFoundError):
                    # If specific gesture image not found, use default
                    self.images[gesture] = self.image
        except (pygame.error, FileNotFoundError):
            # If no images can be loaded, we'll use a shape in the draw method
            self.image = None

    def update(self, delta_time):
        """Update character position and state.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Apply velocity to position with smoothing
        if self.gesture == "closed_fist":
            # When fist is closed, slow down gradually
            self.velocity[0] *= 0.9
            self.velocity[1] *= 0.9
        else:
            # Move toward target position
            dx = self.target_position[0] - self.x
            dy = self.target_position[1] - self.y

            # Calculate distance to target
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 5:  # Only move if we're not already close enough
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance

                # Set velocity based on gesture
                target_speed = self.max_speed
                if self.gesture == "pointing":
                    target_speed = self.max_speed * 1.5  # Faster when pointing
                elif self.gesture == "open_palm":
                    target_speed = self.max_speed * 0.8  # Slower with open palm

                # Apply acceleration toward target speed
                acceleration = 0.2
                self.velocity[0] += dx * acceleration * target_speed
                self.velocity[1] += dy * acceleration * target_speed

                # Limit max speed
                speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
                if speed > target_speed:
                    self.velocity[0] = self.velocity[0] / speed * target_speed
                    self.velocity[1] = self.velocity[1] / speed * target_speed

        # Apply velocity to position
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time

    def set_gesture(self, gesture):
        """Set the character's current gesture.

        Args:
            gesture: String name of the gesture
        """
        self.gesture = gesture

        # Special gesture handling
        if gesture == "thumbs_up" and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_cooldown = 1.0  # 1 second cooldown
        else:
            self.is_attacking = False

    def set_target_position(self, position):
        """Set the target position to move toward.

        Args:
            position: (x, y) tuple of the target position
        """
        self.target_position = position

    def draw(self, screen):
        """Draw the character on the screen.

        Args:
            screen: Pygame screen surface to draw on
        """
        # Choose image based on gesture
        if self.gesture and self.gesture in self.images:
            current_image = self.images[self.gesture]
        elif self.image:
            current_image = self.image
        else:
            # If no image is available, draw a circle
            pygame.draw.circle(
                screen, (0, 0, 255), (int(self.x), int(self.y)), self.size // 2
            )
            return

        # Draw the character image
        if current_image:
            # Calculate rotation based on velocity direction
            if abs(self.velocity[0]) > 1 or abs(self.velocity[1]) > 1:
                self.rotation = math.degrees(
                    math.atan2(self.velocity[1], self.velocity[0])
                )

            # Rotate image
            rotated_image = pygame.transform.rotate(current_image, -self.rotation - 90)
            new_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, new_rect.topleft)

            # Draw attack effect if attacking
            if self.is_attacking:
                pygame.draw.circle(
                    screen,
                    (255, 200, 0, 128),
                    (int(self.x), int(self.y)),
                    self.size * 1.5,
                    5,
                )

    def get_rect(self):
        """Get the character's collision rectangle.

        Returns:
            pygame.Rect: Rectangle for collision detection
        """
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


class Target:
    """Target object that the player needs to collect."""

    def __init__(self, x, y, size=30, value=1, type="standard"):
        self.x = x
        self.y = y
        self.size = size
        self.value = value
        self.type = type
        self.collected = False
        self.animation_time = 0
        self.speed = random.uniform(0.5, 2.0)
        self.direction = random.uniform(0, 2 * math.pi)
        self.velocity = [
            math.cos(self.direction) * self.speed,
            math.sin(self.direction) * self.speed,
        ]

        # Choose color based on target type
        self.colors = {
            "standard": (0, 255, 0),
            "bonus": (255, 255, 0),
            "special": (255, 0, 255),
            "negative": (255, 0, 0),
        }

        # Load image if available
        self.image = None
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            assets_dir = os.path.join(project_root, "assets")

            image_path = os.path.join(assets_dir, f"target_{self.type}.png")
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except (pygame.error, FileNotFoundError):
            # If image can't be loaded, we'll draw a shape
            self.image = None

    def update(self, delta_time, screen_width, screen_height):
        """Update target position and animation.

        Args:
            delta_time: Time elapsed since last update in seconds
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        if self.collected:
            return

        # Update animation time
        self.animation_time += delta_time

        # Move the target if it's a moving type
        if self.type in ["bonus", "special"]:
            self.x += self.velocity[0]
            self.y += self.velocity[1]

            # Bounce off edges
            if self.x - self.size // 2 < 0 or self.x + self.size // 2 > screen_width:
                self.velocity[0] *= -1
            if self.y - self.size // 2 < 0 or self.y + self.size // 2 > screen_height:
                self.velocity[1] *= -1

    def draw(self, screen):
        """Draw the target on the screen.

        Args:
            screen: Pygame screen surface to draw on
        """
        if self.collected:
            return

        if self.image:
            # Draw with image
            # Apply pulsing effect based on animation time
            scale_factor = 1.0 + 0.1 * math.sin(self.animation_time * 5)
            scaled_size = int(self.size * scale_factor)
            scaled_image = pygame.transform.scale(
                self.image, (scaled_size, scaled_size)
            )

            screen.blit(
                scaled_image, (self.x - scaled_size // 2, self.y - scaled_size // 2)
            )
        else:
            # Draw a circle with pulsing size
            color = self.colors.get(self.type, (0, 255, 0))
            pulse = int(20 * math.sin(self.animation_time * 5) + 235)
            pygame.draw.circle(
                screen,
                color,
                (int(self.x), int(self.y)),
                int(self.size // 2 * (1 + 0.1 * math.sin(self.animation_time * 5))),
            )

    def get_rect(self):
        """Get the target's collision rectangle.

        Returns:
            pygame.Rect: Rectangle for collision detection
        """
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


class Obstacle:
    """Obstacle that the player needs to avoid."""

    def __init__(self, x, y, width, height, speed=0, moving=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.moving = moving
        self.direction = 1  # 1 for right/down, -1 for left/up
        self.vertical = random.choice([True, False]) if moving else False
        self.distance = 0
        self.max_distance = random.randint(100, 300) if moving else 0

        # Load image if available
        self.image = None
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            assets_dir = os.path.join(project_root, "assets")

            self.image = pygame.image.load(os.path.join(assets_dir, "obstacle.png"))
            self.image = pygame.transform.scale(self.image, (width, height))
        except (pygame.error, FileNotFoundError):
            # If image can't be loaded, we'll draw a rectangle
            self.image = None

    def update(self, delta_time):
        """Update obstacle position if it's moving.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.moving:
            return

        move_amount = self.speed * delta_time * self.direction

        if self.vertical:
            self.y += move_amount
        else:
            self.x += move_amount

        self.distance += abs(move_amount)

        if self.distance >= self.max_distance:
            self.direction *= -1
            self.distance = 0

    def draw(self, screen):
        """Draw the obstacle on the screen.

        Args:
            screen: Pygame screen surface to draw on
        """
        if self.image:
            screen.blit(self.image, (int(self.x), int(self.y)))
        else:
            # Draw a rectangle
            pygame.draw.rect(
                screen,
                (150, 75, 0),
                (int(self.x), int(self.y), self.width, self.height),
            )

    def get_rect(self):
        """Get the obstacle's collision rectangle.

        Returns:
            pygame.Rect: Rectangle for collision detection
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Particle:
    """Particle effect for visual feedback."""

    def __init__(self, x, y, color, size=5, life=1.0, speed=2.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.5, speed)
        self.velocity = [
            math.cos(self.angle) * self.speed,
            math.sin(self.angle) * self.speed,
        ]

    def update(self, delta_time):
        """Update particle position and life.

        Args:
            delta_time: Time elapsed since last update in seconds

        Returns:
            bool: True if the particle is still alive, False if it should be removed
        """
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= delta_time

        # Gradually slow down
        self.velocity[0] *= 0.95
        self.velocity[1] *= 0.95

        # Gradually reduce size
        self.size = max(0, self.size * (self.life / self.max_life))

        return self.life > 0

    def draw(self, screen):
        """Draw the particle on the screen.

        Args:
            screen: Pygame screen surface to draw on
        """
        # Calculate alpha based on remaining life
        alpha = int(255 * (self.life / self.max_life))

        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface(
            (int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA
        )

        # Draw the particle on the new surface
        pygame.draw.circle(
            particle_surface,
            (self.color[0], self.color[1], self.color[2], alpha),
            (int(self.size), int(self.size)),
            int(self.size),
        )

        # Blit the new surface onto the screen
        screen.blit(
            particle_surface, (int(self.x - self.size), int(self.y - self.size))
        )


class ParticleSystem:
    """System for managing multiple particles."""

    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color, size=5, life=1.0, speed=2.0):
        """Add a new particle to the system.

        Args:
            x, y: Position of the particle
            color: (r, g, b) color tuple
            size: Size of the particle
            life: Lifetime of the particle in seconds
            speed: Base speed of the particle
        """
        self.particles.append(Particle(x, y, color, size, life, speed))

    def add_explosion(self, x, y, color, count=20, size=5, life=1.0, speed=3.0):
        """Add an explosion effect (multiple particles).

        Args:
            x, y: Position of the explosion
            color: (r, g, b) color tuple
            count: Number of particles
            size: Size of each particle
            life: Base lifetime of particles in seconds
            speed: Base speed of particles
        """
        for _ in range(count):
            # Randomize parameters slightly
            particle_size = random.uniform(size * 0.5, size * 1.5)
            particle_life = random.uniform(life * 0.5, life * 1.5)
            particle_speed = random.uniform(speed * 0.5, speed * 1.5)

            self.add_particle(x, y, color, particle_size, particle_life, particle_speed)

    def update(self, delta_time):
        """Update all particles in the system.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(delta_time)]

    def draw(self, screen):
        """Draw all particles in the system.

        Args:
            screen: Pygame screen surface to draw on
        """
        for particle in self.particles:
            particle.draw(screen)
