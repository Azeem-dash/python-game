import math
import random

import pygame


class Particle:
    """Simple particle for visual effects."""

    def __init__(self, x, y, color, velocity, size=3, lifespan=30):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]
        self.size = size
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        """Update particle position and age."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.age += 1
        # Make particle shrink as it ages
        self.size = max(1, self.size * (1 - self.age / self.lifespan))
        return self.age < self.lifespan

    def draw(self, screen):
        """Draw particle on screen."""
        # Fade color as particle ages
        alpha = 255 * (1 - self.age / self.lifespan)
        color = (
            self.color[0],
            self.color[1],
            self.color[2],
            int(alpha) if len(self.color) == 4 else 255,
        )
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))


class ParticleSystem:
    """System to manage multiple particles."""

    def __init__(self):
        self.particles = []

    def add_explosion(self, x, y, color, count=20, speed=3):
        """Add an explosion of particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed_factor = random.uniform(0.5, 1.0) * speed
            velocity = (math.cos(angle) * speed_factor, math.sin(angle) * speed_factor)
            size = random.randint(2, 5)
            lifespan = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity, size, lifespan))

    def add_trail(self, x, y, color, direction, count=5):
        """Add a trail of particles behind an object."""
        for _ in range(count):
            # Opposite direction of travel with some random variation
            angle = (
                math.atan2(direction[1], direction[0])
                + math.pi
                + random.uniform(-0.5, 0.5)
            )
            speed = random.uniform(0.5, 2.0)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.randint(2, 4)
            lifespan = random.randint(10, 20)
            # Slightly offset starting position
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            self.particles.append(
                Particle(x + offset_x, y + offset_y, color, velocity, size, lifespan)
            )

    def update(self):
        """Update all particles."""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)


class PowerUp:
    """Base class for power-ups."""

    def __init__(self, x, y, radius, color, duration=5, value=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.duration = duration  # in seconds
        self.value = value
        self.collected = False
        self.start_time = None
        self.active = False
        self.particle_system = ParticleSystem()

    def update(self, delta_time):
        """Update power-up state."""
        if not self.active:
            return

        # Update particles
        self.particle_system.update()

        # Check if power-up expired
        elapsed = pygame.time.get_ticks() / 1000 - self.start_time
        if elapsed >= self.duration:
            self.active = False
            return False

        return True

    def collect(self):
        """Collect the power-up."""
        self.collected = True
        self.start_time = pygame.time.get_ticks() / 1000
        self.active = True
        return self.value

    def draw(self, screen):
        """Draw power-up on screen."""
        if self.collected:
            return

        # Draw power-up with pulsing effect
        t = pygame.time.get_ticks() / 1000
        pulse = 0.2 * math.sin(t * 5) + 1.0  # Pulsating between 0.8 and 1.2

        pygame.draw.circle(
            screen, self.color, (int(self.x), int(self.y)), int(self.radius * pulse)
        )

    def draw_effects(self, screen):
        """Draw any special effects."""
        if self.active:
            self.particle_system.draw(screen)


class SpeedBoost(PowerUp):
    """Speed boost power-up."""

    def __init__(self, x, y, radius=15):
        super().__init__(x, y, radius, (0, 255, 255), duration=5, value=1)
        self.speed_multiplier = 1.5

    def apply(self, ball):
        """Apply speed boost to ball."""
        if self.active:
            return self.speed_multiplier
        return 1.0

    def draw_effects(self, screen, ball_pos, ball_velocity):
        """Draw trail effects behind ball."""
        if self.active:
            # Normalize velocity for direction
            velocity_length = math.sqrt(ball_velocity[0] ** 2 + ball_velocity[1] ** 2)
            if velocity_length > 0:
                direction = (
                    ball_velocity[0] / velocity_length,
                    ball_velocity[1] / velocity_length,
                )
                self.particle_system.add_trail(
                    ball_pos[0], ball_pos[1], (0, 200, 255), direction
                )

            # Draw existing particles
            super().draw_effects(screen)


class ShieldPowerUp(PowerUp):
    """Shield power-up for obstacle protection."""

    def __init__(self, x, y, radius=15):
        super().__init__(x, y, radius, (255, 215, 0), duration=8, value=2)  # Gold color

    def apply(self, ball_pos, ball_radius):
        """Check if shield is active."""
        return self.active

    def draw_effects(self, screen, ball_pos, ball_radius):
        """Draw shield around ball."""
        if self.active:
            # Draw shield circle around ball
            shield_radius = ball_radius * 1.5

            # Pulsating effect
            t = pygame.time.get_ticks() / 1000
            pulse = 0.1 * math.sin(t * 8) + 1.0

            # Draw semi-transparent shield
            shield_surface = pygame.Surface(
                (shield_radius * 2 + 4, shield_radius * 2 + 4), pygame.SRCALPHA
            )
            pygame.draw.circle(
                shield_surface,
                (255, 215, 0, 100),  # Semi-transparent gold
                (shield_radius + 2, shield_radius + 2),
                shield_radius * pulse,
            )

            # Draw shield border
            pygame.draw.circle(
                shield_surface,
                (255, 215, 0, 180),  # More opaque gold
                (shield_radius + 2, shield_radius + 2),
                shield_radius * pulse,
                2,  # border width
            )

            # Position shield at ball
            shield_pos = (
                int(ball_pos[0] - shield_radius - 2),
                int(ball_pos[1] - shield_radius - 2),
            )
            screen.blit(shield_surface, shield_pos)

            # Occasionally add particles around shield perimeter
            if random.random() < 0.2:
                angle = random.uniform(0, 2 * math.pi)
                x = ball_pos[0] + math.cos(angle) * shield_radius
                y = ball_pos[1] + math.sin(angle) * shield_radius
                self.particle_system.add_explosion(
                    x, y, (255, 215, 0), count=3, speed=1
                )

            # Update and draw particles
            self.particle_system.update()
            self.particle_system.draw(screen)


class MagnetPowerUp(PowerUp):
    """Magnet power-up to attract targets."""

    def __init__(self, x, y, radius=15):
        super().__init__(
            x, y, radius, (255, 0, 255), duration=10, value=2
        )  # Magenta color
        self.attraction_radius = 150

    def apply(self, ball_pos, targets):
        """Move targets toward ball if they're within attraction radius."""
        if not self.active:
            return

        for target in targets:
            dx = ball_pos[0] - target["x"]
            dy = ball_pos[1] - target["y"]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.attraction_radius:
                # Calculate attraction strength (stronger as targets get closer)
                strength = (
                    0.05 * (self.attraction_radius - distance) / self.attraction_radius
                )

                # Move target toward ball
                target["x"] += dx * strength
                target["y"] += dy * strength

                # Add visual effect to show attraction
                if random.random() < 0.1:
                    # Add particles between target and ball
                    mid_x = (ball_pos[0] + target["x"]) / 2
                    mid_y = (ball_pos[1] + target["y"]) / 2
                    self.particle_system.add_explosion(
                        mid_x, mid_y, (255, 0, 255), count=2, speed=1
                    )

    def draw_effects(self, screen, ball_pos):
        """Draw magnet field around ball."""
        if self.active:
            # Draw attraction radius with semi-transparency
            attraction_surface = pygame.Surface(
                (self.attraction_radius * 2, self.attraction_radius * 2),
                pygame.SRCALPHA,
            )
            pygame.draw.circle(
                attraction_surface,
                (255, 0, 255, 30),  # Very transparent magenta
                (self.attraction_radius, self.attraction_radius),
                self.attraction_radius,
            )

            # Draw field lines
            t = pygame.time.get_ticks() / 1000
            rotation = t % (2 * math.pi)

            for i in range(8):
                angle = rotation + i * math.pi / 4
                r1 = self.attraction_radius * 0.4
                r2 = self.attraction_radius * 0.9
                x1 = self.attraction_radius + math.cos(angle) * r1
                y1 = self.attraction_radius + math.sin(angle) * r1
                x2 = self.attraction_radius + math.cos(angle) * r2
                y2 = self.attraction_radius + math.sin(angle) * r2

                pygame.draw.line(
                    attraction_surface,
                    (255, 0, 255, 150),  # Semi-transparent magenta
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    2,
                )

            # Position field at ball
            field_pos = (
                int(ball_pos[0] - self.attraction_radius),
                int(ball_pos[1] - self.attraction_radius),
            )
            screen.blit(attraction_surface, field_pos)

            # Update and draw particles
            self.particle_system.update()
            self.particle_system.draw(screen)
