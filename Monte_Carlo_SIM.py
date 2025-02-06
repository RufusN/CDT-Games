import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600  # Window size
RADIUS = WIDTH // 2        # Radius of the circle
CENTER = (WIDTH // 2, HEIGHT // 2)
POINT_RADIUS = 3           # Radius of the plotted points

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Green for inside points
RED = (255, 0, 0)    # Red for outside points
GRAY = (50, 50, 50)   # Dark gray for stats background

# Fonts
pygame.font.init()
FONT = pygame.font.SysFont('Arial', 18)

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for info
pygame.display.set_caption("Monte Carlo π Estimation with Pygame")

# Function to draw the circle and square
def draw_shapes():
    screen.fill(BLACK)  # Set background to black
    # Draw square border in white
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT), 2)
    # Draw inscribed circle in white
    pygame.draw.circle(screen, WHITE, CENTER, RADIUS, 2)

# Function to display statistics
def display_stats(points_inside, total_points, pi_estimate):
    stats_surface = pygame.Surface((WIDTH, 100))
    stats_surface.fill(GRAY)
    
    # Prepare text
    text_inside = FONT.render(f"Points Inside Circle: {points_inside}", True, WHITE)
    text_total = FONT.render(f"Total Points: {total_points}", True, WHITE)
    text_pi = FONT.render(f"π Estimate: {pi_estimate:.6f}", True, WHITE)
    
    # Blit texts
    stats_surface.blit(text_inside, (20, 20))
    stats_surface.blit(text_total, (20, 50))
    stats_surface.blit(text_pi, (20, 80))
    
    screen.blit(stats_surface, (0, HEIGHT))

def main():
    draw_shapes()
    pygame.display.flip()

    points_inside = 0
    total_points = 0
    points = []  # List to store all points
    pi_estimate = 0  # Initialize pi_estimate

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Generate random point
                x = random.uniform(0, 1)
                y = random.uniform(0, 1)

                # Scale to window size
                pos_x = int(x * WIDTH)
                pos_y = int(y * HEIGHT)

                # Calculate distance from center in normalized coordinates
                dx = x - 0.5
                dy = y - 0.5
                distance_squared = dx**2 + dy**2

                # Check if inside circle (radius 0.5 in normalized coordinates)
                if distance_squared <= 0.25:
                    points_inside += 1
                    color = GREEN  # Inside circle
                else:
                    color = RED    # Outside circle

                total_points += 1

                # Store the point and its status
                points.append((pos_x, pos_y, color))

        # Redraw shapes
        draw_shapes()

        # Draw all points
        for point in points:
            pos = (point[0], point[1])
            pygame.draw.circle(screen, point[2], pos, POINT_RADIUS)

        # Calculate π estimate
        if total_points == 0:
            pi_estimate = 0
        else:
            pi_estimate = 4 * (points_inside / total_points)

        # Update statistics
        display_stats(points_inside, total_points, pi_estimate)

        # Update the display
        pygame.display.flip()

        # Limit the frame rate
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
