import pygame
import sys
import random
import math

pygame.init()

# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
SIM_WIDTH = 600  # simulation panel width
CONTROL_WIDTH = WIDTH - SIM_WIDTH  # control panel width

BG_COLOR = (30, 30, 30)
SIM_BG_COLOR = (0, 0, 0)
CONTROL_BG_COLOR = (50, 50, 50)

# Scatter is fixed at 0.5
SCATTER_PROB = 0.5
# Fission + Capture = 0.5
# We'll let the user adjust fission (x) from 0.0 to 0.5 via a slider,
# and capture = 0.5 - x

# Neutron parameters
NEUTRON_RADIUS = 5
NEUTRON_SPEED = 5  # base speed
NEUTRON_COLOR = (0, 255, 255)

# Distance threshold before a neutron attempts an interaction
DISTANCE_BEFORE_REACTION = 100

# Slider parameters
SLIDER_X = SIM_WIDTH + 20
SLIDER_Y = 100
SLIDER_WIDTH = CONTROL_WIDTH - 40
SLIDER_HEIGHT = 20

# --------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------
class Neutron:
    """
    Represents a neutron traveling in 2D space.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Random direction & speed factor
        angle = random.uniform(0, 2 * math.pi)
        speed_factor = random.uniform(0.5, 1.0)
        velocity = pygame.math.Vector2(NEUTRON_SPEED * speed_factor, 0).rotate_rad(angle)
        self.vx = velocity.x
        self.vy = velocity.y

        # Track how far this neutron has traveled since last interaction
        self.distance_since_interaction = 0.0

    def update_position(self):
        """
        Moves the neutron one frame, bounces on boundaries, and
        returns the distance traveled in this update.
        """
        old_x, old_y = self.x, self.y
        self.x += self.vx
        self.y += self.vy

        # Bounce off boundaries in the simulation panel
        if self.x < NEUTRON_RADIUS or self.x > SIM_WIDTH - NEUTRON_RADIUS:
            self.vx = -self.vx
        if self.y < NEUTRON_RADIUS or self.y > HEIGHT - NEUTRON_RADIUS:
            self.vy = -self.vy

        # Actual distance traveled this frame
        dx = self.x - old_x
        dy = self.y - old_y
        dist = math.hypot(dx, dy)
        return dist

    def scatter(self):
        """ Randomize direction (scatter). """
        angle = random.uniform(0, 2 * math.pi)
        speed_factor = random.uniform(0.5, 1.0)
        velocity = pygame.math.Vector2(NEUTRON_SPEED * speed_factor, 0).rotate_rad(angle)
        self.vx = velocity.x
        self.vy = velocity.y
        self.distance_since_interaction = 0.0  # reset distance

    def draw(self, surface):
        pygame.draw.circle(surface, NEUTRON_COLOR, (int(self.x), int(self.y)), NEUTRON_RADIUS)


class Slider:
    """
    A basic horizontal slider for fission probability (x).
    Range: 0.0 to 0.5
    """
    def __init__(self, x, y, width, height, min_val=0.0, max_val=0.5, initial_val=0.25):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_width = 10
        self.handle_rect = pygame.Rect(0, y, self.handle_width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.grabbed = False
        # Position the handle based on initial_val
        self._update_handle_position()

    def _update_handle_position(self):
        fraction = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.x = int(self.rect.x + fraction * (self.rect.width - self.handle_width))

    def set_value_from_pos(self, mouse_x):
        # Constrain handle between slider bounds
        clamped_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width - self.handle_width))
        self.handle_rect.x = clamped_x
        fraction = (clamped_x - self.rect.x) / float(self.rect.width - self.handle_width)
        self.value = self.min_val + fraction * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION:
            if self.grabbed:
                self.set_value_from_pos(event.pos[0])

    def draw(self, surface):
        # Draw the slider track
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        # Fill in the 'active' region for visualization
        active_rect = self.rect.copy()
        active_rect.width = self.handle_rect.x + self.handle_width - self.rect.x
        pygame.draw.rect(surface, (100, 200, 100), active_rect)
        # Draw the slider handle
        pygame.draw.rect(surface, (255, 0, 0), self.handle_rect)

# --------------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monte Carlo Radiation Simulation")

clock = pygame.time.Clock()

# Create some initial neutrons
neutrons = [Neutron(random.randint(50, SIM_WIDTH - 50),
                    random.randint(50, HEIGHT - 50)) for _ in range(10)]

# Create the slider for fission probability x
# range is [0.0, 0.5], so capture = 0.5 - x
fission_slider = Slider(SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT,
                        min_val=0.0, max_val=0.5, initial_val=0.25)

# Separate counters for different interaction types
scatter_count = 0
fission_count = 0
capture_count = 0

# --------------------------------------------------------------------------------
# Main Loop
# --------------------------------------------------------------------------------
running = True
while running:
    clock.tick(60)  # limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle slider events
        fission_slider.handle_event(event)

    # Current fission/capture probabilities based on slider
    x = fission_slider.value  # fission
    y = 0.5 - x               # capture

    new_neutrons = []
    remove_neutrons = set()

    # Update each neutron
    for i, neutron in enumerate(neutrons):
        # Move neutron, accumulate traveled distance
        dist_traveled = neutron.update_position()
        neutron.distance_since_interaction += dist_traveled

        # If neutron has traveled enough distance, attempt an interaction
        if neutron.distance_since_interaction >= DISTANCE_BEFORE_REACTION:
            # Reset distance traveled
            neutron.distance_since_interaction = 0.0

            # The total probability of "some absorption or scatter" is 1 in this toy model
            # But we randomize which event occurs: scatter, fission, or capture.
            r = random.random()  # in [0,1)
            if r < SCATTER_PROB:
                # Scatter
                neutron.scatter()
                scatter_count += 1
            elif r < SCATTER_PROB + x:
                # Fission
                fission_count += 1
                remove_neutrons.add(i)
                # produce 2 new neutrons at the same location
                for _ in range(2):
                    new_n = Neutron(neutron.x, neutron.y)
                    new_neutrons.append(new_n)
            else:
                # Capture
                capture_count += 1
                remove_neutrons.add(i)

    # Remove neutrons that fissioned or were captured
    neutrons = [n for i, n in enumerate(neutrons) if i not in remove_neutrons]
    # Add newly produced (fission) neutrons
    neutrons.extend(new_neutrons)

    # If all neutrons disappear, spawn one in the center
    if not neutrons:
        neutrons.append(Neutron(SIM_WIDTH // 2, HEIGHT // 2))

    # --------------------------------------------------------------------------------
    # Drawing
    # --------------------------------------------------------------------------------
    screen.fill(BG_COLOR)

    # Simulation panel
    sim_rect = pygame.Rect(0, 0, SIM_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIM_BG_COLOR, sim_rect)

    # Draw neutrons
    for neutron in neutrons:
        neutron.draw(screen)

    # Show interaction tallies (top-left corner in the simulation area)
    font = pygame.font.SysFont(None, 24)
    scatter_text = font.render(f"Scatters: {scatter_count}", True, (255, 255, 255))
    fission_text = font.render(f"Fissions: {fission_count}", True, (255, 255, 255))
    capture_text = font.render(f"Captures: {capture_count}", True, (255, 255, 255))

    screen.blit(scatter_text, (10, 10))
    screen.blit(fission_text, (10, 30))
    screen.blit(capture_text, (10, 50))

    # Control panel
    control_rect = pygame.Rect(SIM_WIDTH, 0, CONTROL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, CONTROL_BG_COLOR, control_rect)

    # Draw slider
    fission_slider.draw(screen)

    # Display fission/capture probabilities
    info_text1 = font.render(f"Fission (x): {x:.2f}", True, (255, 255, 255))
    info_text2 = font.render(f"Capture (y): {y:.2f}", True, (255, 255, 255))
    screen.blit(info_text1, (SLIDER_X, SLIDER_Y - 30))
    screen.blit(info_text2, (SLIDER_X, SLIDER_Y + 30))

    # --- NEW: Neutron count below the slider ---
    neutron_count_text = font.render(f"Power: {len(neutrons)}", True, (255, 255, 255))
    screen.blit(neutron_count_text, (SLIDER_X, SLIDER_Y + 60))

    # --- NEW: k_eff below the neutron count ---
    # Simple 0D estimate: k_eff = 2 * x / (x + y) = 4 * x, since x + y = 0.5
    if (x + y) > 0:
        k_eff = 2.0 * x / (x + y)  # or simply 4*x if x+y=0.5
    else:
        k_eff = 0.0
    keff_text = font.render(f"k_eff: {k_eff:.2f}", True, (255, 255, 255))
    screen.blit(keff_text, (SLIDER_X, SLIDER_Y + 90))

    pygame.display.flip()

pygame.quit()
sys.exit()
