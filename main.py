'''Bouncing Box'''
__version__="04.02.2025"
__author__ = "Ryan Xue"

import pygame

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (75, 75, 255)
DARKBLUE = (0, 0, 25)

# Screen dimensions
SCREEN_WIDTH = 1152
SCREEN_HEIGHT = 648

position = 0.0

class MovingGrid:
    def __init__(self, screen_width, screen_height, grid_size=40):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = 120

        # Grid movement speed
        self.offset_x = 5
        self.offset_y = 5

        # Grid color
        self.color = (GREEN)

    def update(self, player_speed_x=0, player_speed_y=0):
        # Update grid offset based on player movement
        self.offset_x -= player_speed_x * 0.5
        self.offset_y -= player_speed_y * 0.5

        # Wrap around to create continuous movement
        self.offset_x %= self.grid_size
        self.offset_y %= self.grid_size

    def draw(self, screen):
        # Draw vertical lines
        for x in range(-self.grid_size, self.screen_width + self.grid_size, self.grid_size):
            adjusted_x = x + self.offset_x
            pygame.draw.line(screen, self.color,
                             (adjusted_x, 0),
                             (adjusted_x, self.screen_height), 1)

        # Draw horizontal lines
        for y in range(-self.grid_size, self.screen_height + self.grid_size, self.grid_size):
            adjusted_y = y + self.offset_y
            pygame.draw.line(screen, self.color,
                             (0, adjusted_y),
                             (self.screen_width, adjusted_y), 1)
class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an invisible hitbox
        self.rect = pygame.Rect(0, 0, 40, 40)  # Same size as your previous invisible surface

        # Load the cube image
        self.original_image = pygame.image.load('cube.png').convert_alpha()

        # Create a visual sprite that follows the hit box
        self.image = self.original_image

        # Initialize angle for potential rotation
        self.angle = 0

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None
        self.jump = False

    def update(self):
        """ Move the player. """
        # Gravity and movement (rest of your existing update method)
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # Collision detection (your existing code)
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        if len(pygame.sprite.spritecollide(self, self.level.enemy_list, False)) >= 1:
            screen = pygame.display.get_surface()
            # Center of the circle will be the player's center
            center_x, center_y = self.rect.center
            # Create a surface for the expanding circle
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            grid = MovingGrid(SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.mixer.Sound('death.ogg').play()

            for radius in range(0, 100, 10):
                screen.fill(BLACK)
                self.level.draw(screen, grid)
                # Create a new surface for the circle
                overlay.fill((0, 0, 0, 0))

                # Draw expanding circle
                pygame.draw.circle(overlay, (242, 190, 70), (center_x, center_y), radius, 5)

                # Blend the overlay
                screen.blit(overlay, (0, 0))

                # Update display
                pygame.display.flip()

                # Control speed of expansion
                pygame.time.delay(20)
            screen.fill(BLACK)
            self.level.draw(screen, grid)
            pygame.display.flip()
            # Quit the game
            pygame.time.delay(1000)
            pygame.quit()
            exit()
        # Move up/down
        self.rect.y += self.change_y

        # Vertical collision detection (your existing code)
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

        # Determine if on ground
        self.rect.y += 2
        on_ground = (len(pygame.sprite.spritecollide(self, self.level.platform_list, False)) > 0
                     or self.rect.bottom >= SCREEN_HEIGHT - 40)
        self.rect.y -= 2
        # Rotation logic
        if on_ground:
            # Snap to nearest 90 degrees when on ground
            self.angle = round(self.angle / 90) * 90
        else:
            if self.change_x < 0:
                self.angle += 5
            if self.change_x > 0:
                self.angle -= 5
        # Ensure the visual image follows the hitbox
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)

        # Create a new surface the size of the rect
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Calculate the position to blit the rotated image so it's centered
        x = (self.rect.width - rotated_image.get_width()) // 2
        y = (self.rect.height - rotated_image.get_height()) // 2

        # Blit the rotated image onto the surface
        self.image.blit(rotated_image, (x, y))


        if self.jump == True:
            self.rect.y += 2
            platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            self.rect.y -= 2

            # If it is ok to jump, set our speed upwards
            if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT - 40:
                self.change_y = -18

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 1.1

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT-40 - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT-40 - self.rect.height


    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(DARKBLUE)
        self.rect = pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 2)
class Coin(pygame.sprite.Sprite):
    def __init__(self, order):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        self.image = pygame.image.load('coin.png')
        self.rect = self.image.get_rect()
        self.collected = False
        self.velocity_y = -10  # Initial upward velocity
        self.played = False
        self.order = order
    def update(self):
        if self.collected:
            if self.played == False:
                pygame.mixer.Sound('coin.ogg').play()
            self.played = True
            self.rect.y += self.velocity_y
            self.velocity_y += 1
            if self.rect.bottom < 0:
                self.remove()







class Spike(pygame.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()

        # Create the surface
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)

        if direction == 1:  # Point up
            points = [(20, 1), (1, 39), (39, 39)]  # Adjusted points
        elif direction == 2:  # Point right
            points = [(1, 1), (1, 39), (39, 20)]  # Adjusted points
        elif direction == 3:  # Point down
            points = [(1, 1), (39, 1), (20, 39)]  # Adjusted points
        elif direction == 4:  # Point left
            points = [(39, 1), (39, 39), (1, 20)]  # Adjusted points

        # Draw the polygon
        pygame.draw.polygon(self.image, DARKBLUE, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)

        # Create rect
        self.rect = self.image.get_rect()


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player, coin_tracker):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.player = player
        self.coin_tracker = coin_tracker

        # How far this world has been scrolled left/right
        self.world_shift = 0

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
        self.coin_list.update()

        for coin in pygame.sprite.spritecollide(self.player, self.coin_list, False):
            coin.collected = True
            if coin.order not in self.coin_tracker.coins_collected:
                self.coin_tracker.coins_collected.append(coin.order)
    def draw(self, screen, grid=None):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(BLACK)
        if grid:
            grid.draw(screen)
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.coin_list.draw(screen)
        pygame.draw.rect(screen, DARKBLUE, pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        pygame.draw.rect(screen, WHITE, pygame.Rect(0-2, SCREEN_HEIGHT - 40, SCREEN_WIDTH+4, 42), 2)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for coin in self.coin_list:
            coin.rect.x += shift_x

class CoinTracker:
    def __init__(self):
        super().__init__()
        self.coins_collected = []
        self.coin_image = pygame.image.load('coin.png')
        self.coin_image = pygame.transform.scale(self.coin_image, (40, 40))  # Resize for UI

    def reset(self):
        self.coins_collected = []

# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """
    def __init__(self, player, coin_tracker):
        """ Create level 1. """
        Level.__init__(self, player, coin_tracker)
        level = [[-12, 1, 0],
                 [-12, 2, 0],
                 [-12, 3, 0],
                 [-12, 4, 0],
                 [-12, 5, 0],
                 [-12, 6, 0],
                 [-12, 7, 0],
                 [-12, 8, 0],
                 [-12, 9, 0],
                 [-12, 10, 0],
                 [-12, 11, 0],
                 [-12, 12, 0],
                 [-12, 13, 0],
                 [-12, 14, 0],
                 [-12, 15, 0],
                 [-12, 16, 0],
                 [15, 1, 1],
                 [19, 1, 1],
                 [20, 1, 1],
                 [24, 1, 1],
                 [25, 1, 1],
                 [28, 1, 0],
                 [29, 4, 0],
                 [28, 7, 0],
                 [24, 7, 0],
                 [23, 7, 0],
                 [22, 7, 0],
                 [22, 8, 1],
                 [21, 8, 1],
                 [21, 7, 0],
                 [20, 7, 0],
                 [20, 8, 1],
                 [19, 7, 0],
                 [18, 7, 0],
                 [15, 7, 0],
                 [14.75, 9.75, 5, 1],
                 [30, 1, 1],
                 [31, 1, 1],
                 [32, 1, 1],
                 [33, 1, 1],
                 [34, 1, 1],
                 [35, 1, 1],
                 [36, 1, 1],
                 [37, 1, 1],
                 [38, 1, 1],
                 [39, 1, 1],
                 [40, 1, 1],
                 [41, 1, 1],
                 [42, 1, 1],
                 [43, 1, 1],
                 [44, 1, 1],
                 [45, 1, 1],
                 [46, 1, 1],
                 [47, 1, 1],
                 [48, 1, 1],
                 [49, 1, 1],
                 [50, 1, 1],
                 [51, 1, 1],
                 [52, 1, 1],
                 [53, 1, 1],
                 [54, 1, 1],
                 [55, 1, 1],
                 [56, 1, 1],
                 [57, 1, 1],
                 [58, 1, 1],
                 [59, 1, 1],
                 [60, 1, 1],
                 [61, 1, 1],
                 [62, 1, 1],
                 [63, 1, 1],
                 [64, 1, 1],
                 [65, 1, 1],
                 [66, 1, 1],
                 [67, 1, 1],
                 [68, 1, 1],
                 [69, 1, 1],
                 [70, 1, 1],
                 [71, 1, 1],
                 [72, 1, 1],
                 [73, 1, 1],
                 [74, 1, 1],
                 [75, 1, 1],
                 [76, 1, 1],
                 [77, 1, 1],
                 [33, 5, 0],
                 [34, 5, 0],
                 [37, 3, 0],
                 [38, 3, 0],
                 [41, 4, 0],
                 [42, 4, 0],
                 [45, 6, 0],
                 [46, 6, 0],
                 [50, 6, 0],
                 [51, 6, 0],
                 [52, 6, 0],
                 [52, 7, 1],
                 [53, 6, 0],
                 [54, 6, 0],
                 [58, 4, 0],
                 [58, 7, 0],
                 [58, 10, 0],
                 [63, 10, 0],
                 [65, 11, 0],
                 [65, 12, 1],
                 [65, 10, 0],
                 [67, 10, 0],
                 [69.75, 11.75, 5, 2],
                 [58, 4, 0],
                 [61, 4, 0],
                 [64, 4, 0],
                 [67, 4, 0],
                 [70, 5, 0],
                 [71, 5, 0],
                 [75, 4, 0],
                 [79, 3, 0],
                 [85, 1, 1],
                 [86, 1, 1],
                 [76.25, 2.25, 5, 3],
                 [100, 1, 0],
                 [100, 2, 0],
                 [100, 3, 0],
                 [100, 4, 0],
                 [100, 5, 0],
                 [100, 6, 0],
                 [100, 7, 0],
                 [100, 8, 0],
                 [100, 9, 0],
                 [100, 10, 0],
                 [100, 11, 0],
                 [100, 12, 0],
                 [100, 13, 0],
                 [100, 14, 0],
                 [100, 15, 0],
                 [100, 16, 0],
                 ]
        for platform in level:
            if platform[2] == 0:
                block = Platform(40, 40)
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.platform_list.add(block)
            elif platform[2] == 5:
                block = Coin(platform[3])
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.coin_list.add(block)
            else:
                block = Spike(platform[2])
                block.rect.x = platform[0] * 40
                block.rect.y = SCREEN_HEIGHT - platform[1] * 40 - 40
                block.player = self.player
                self.enemy_list.add(block)

class Level_02(Level):
    """ Definition for level 1. """
    def __init__(self, player, coin_tracker):
        """ Create level 1. """
        Level.__init__(self, player, coin_tracker)
        level = [[-12, 1, 0],
                 [-12, 2, 0],
                 [-12, 3, 0],
                 [-12, 4, 0],
                 [-12, 5, 0],
                 [-12, 6, 0],
                 [-12, 7, 0],
                 [-12, 8, 0],
                 [-12, 9, 0],
                 [-12, 10, 0],
                 [-12, 11, 0],
                 [-12, 12, 0],
                 [-12, 13, 0],
                 [-12, 14, 0],
                 [-12, 15, 0],
                 [-12, 16, 0],
                 [10, 2, 0],
                 [11, 2, 0],
                 [15, 4, 0],
                 [100, 1, 0],
                 [100, 2, 0],
                 [100, 3, 0],
                 [100, 4, 0],
                 [100, 5, 0],
                 [100, 6, 0],
                 [100, 7, 0],
                 [100, 8, 0],
                 [100, 9, 0],
                 [100, 10, 0],
                 [100, 11, 0],
                 [100, 12, 0],
                 [100, 13, 0],
                 [100, 14, 0],
                 [100, 15, 0],
                 [100, 16, 0],
                 ]
        for platform in level:
            if platform[2] == 0:
                block = Platform(40, 40)
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.platform_list.add(block)
            elif platform[2] == 5:
                block = Coin(platform[3])
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.coin_list.add(block)
            else:
                block = Spike(platform[2])
                block.rect.x = platform[0] * 40
                block.rect.y = SCREEN_HEIGHT - platform[1] * 40 - 40
                block.player = self.player
                self.enemy_list.add(block)

class Level_03(Level):
    """ Definition for level 1. """
    def __init__(self, player, coin_tracker):
        """ Create level 1. """
        Level.__init__(self, player, coin_tracker)
        level = [[-12, 1, 0],
                 [-12, 2, 0],
                 [-12, 3, 0],
                 [-12, 4, 0],
                 [-12, 5, 0],
                 [-12, 6, 0],
                 [-12, 7, 0],
                 [-12, 8, 0],
                 [-12, 9, 0],
                 [-12, 10, 0],
                 [-12, 11, 0],
                 [-12, 12, 0],
                 [-12, 13, 0],
                 [-12, 14, 0],
                 [-12, 15, 0],
                 [-12, 16, 0],
                 [10, 2, 0],
                 [11, 2, 0],
                 [15, 4, 0],
                 [19, 1, 4],
                 [20, 2, 1],
                 [20, 1, 0],
                 [20, 5, 0],
                 [21, 1, 0],
                 [22, 1, 0],
                 [23, 1, 0],
                 [21, 2, 1],
                 [22, 2, 1],
                 [23, 2, 1],
                 [26, 5, 0],
                 [26, 8, 0],
                 [24, 1, 1],
                 [25, 1, 1],
                 [26, 1, 1],
                 [27, 1, 1],
                 [28, 1, 1],
                 [29, 1, 1],
                 [30, 1, 1],
                 [31, 1, 1],
                 [32, 1, 1],
                 [33, 1, 1],
                 [34, 1, 1],
                 [35, 1, 1],
                 [36, 1, 1],
                 [37, 1, 1],
                 [38, 1, 1],
                 [39, 1, 1],
                 [40, 1, 1],
                 [41, 1, 1],
                 [42, 1, 1],
                 [43, 1, 1],
                 [44, 1, 1],
                 [45, 1, 1],
                 [46, 1, 1],
                 [47, 1, 1],
                 [48, 1, 1],
                 [49, 1, 1],
                 [50, 1, 1],
                 [51, 1, 1],
                 [52, 1, 1],
                 [53, 1, 1],
                 [54, 1, 1],
                 [55, 1, 1],
                 [56, 1, 1],
                 [57, 1, 1],
                 [58, 1, 1],
                 [59, 1, 1],
                 [60, 1, 1],
                 [61, 1, 1],
                 [62, 1, 1],
                 [63, 1, 1],
                 [64, 1, 1],
                 [65, 1, 1],
                 [66, 1, 1],
                 [67, 1, 1],
                 [68, 1, 1],
                 [69, 1, 1],
                 [70, 1, 1],
                 [71, 1, 1],
                 [72, 1, 1],
                 [73, 1, 1],
                 [74, 1, 1],
                 [75, 1, 1],
                 [76, 1, 1],
                 [77, 1, 1],
                 [78, 1, 1],
                 [79, 1, 1],
                 [80, 1, 1],
                 [81, 1, 1],
                 [82, 1, 1],
                 [83, 1, 1],
                 [84, 1, 1],
                 [85, 1, 1],
                 [86, 1, 1],
                 [87, 1, 1],
                 [88, 1, 1],
                 [89, 1, 1],
                 [90, 1, 1],
                 [91, 1, 1],
                 [92, 1, 1],
                 [93, 1, 1],
                 [94, 1, 1],
                 [95, 1, 1],
                 [96, 1, 1],
                 [97, 1, 1],
                 [98, 1, 1],
                 [99, 1, 1],
                 [25, 5, 0],
                 [27, 5, 0],
                 [27, 6, 0],
                 [27, 7, 0],
                 [27, 8, 0],
                 [30, 6, 3],
                 [31, 6, 3],
                 [30, 9, 0],
                 [31, 9, 0],
                 [30, 10, 0],
                 [31, 10, 0],
                 [30, 8, 0],
                 [30, 7, 0],
                 [31, 8, 0],
                 [31, 7, 0],
                 [29, 12, 0],
                 [29, 8, 4],
                 [29, 7, 4],
                 [29, 9, 4],
                 [29, 10, 4],
                 [30, 11, 1],
                 [31, 11, 1],
                 [32, 10, 2],
                 [32, 9, 2],
                 [32, 8, 2],
                 [32, 7, 2],
                 [28, 3, 0],
                 [29, 3, 0],
                 [31, 3, 0],
                 [33, 3, 0],
                 [36, 3, 0],
                 [40, 4, 0],
                 [40, 7, 0],
                 [40, 10, 0],
                 [40, 14, 0],
                 [40, 13, 3],
                 [41, 7, 2],
                 [39, 10, 4],
                 [44, 10, 0],
                 [47, 10, 0],
                 [47, 7, 0],
                 [46, 7, 4],
                 [47, 13, 3],
                 [47, 14, 0],
                 [50, 10, 0],
                 [50, 11, 1],
                 [50, 4, 0],
                 [52, 4, 0],
                 [55, 4, 0],
                 [59, 4, 0],
                 [64, 4, 0],
                 [70, 4, 0],
                 [71, 4, 0],
                 [72, 4, 0],
                 [73, 4, 0],
                 [71, 5, 0],
                 [71, 6, 1],
                 [74, 4, 0],
                 [74, 5, 0],
                 [74, 6, 1],
                 [75, 4, 0],
                 [78, 6, 0],
                 [84, 11, 1],
                 [84, 10, 0],
                 [83, 9, 0],
                 [82, 9, 0],
                 [84, 9, 0],
                 [85, 9, 0],
                 [86, 9, 0],
                 [85, 10, 0],
                 [85, 11, 1],
                 [87, 9, 0],
                 [91, 9, 0],
                 [92, 9, 0],
                 [93, 9, 0],
                 [100, 1, 0],
                 [100, 2, 0],
                 [100, 3, 0],
                 [100, 4, 0],
                 [100, 5, 0],
                 [100, 6, 0],
                 [100, 7, 0],
                 [100, 8, 0],
                 [100, 9, 0],
                 [100, 10, 0],
                 [100, 11, 0],
                 [100, 12, 0],
                 [100, 13, 0],
                 [100, 14, 0],
                 [100, 15, 0],
                 [100, 16, 0],
                 [35, 11, 0],
                 [28.75, 14.75, 5, 1],
                 [49.75, 12.75, 5, 2],
                 [91.75, 11.75, 5, 3]
                 ]
        for platform in level:
            if platform[2] == 0:
                block = Platform(40, 40)
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.platform_list.add(block)
            elif platform[2] == 5:
                block = Coin(platform[3])
                block.rect.x = platform[0]*40
                block.rect.y = SCREEN_HEIGHT-platform[1]*40 - 40
                block.player = self.player
                self.coin_list.add(block)
            else:
                block = Spike(platform[2])
                block.rect.x = platform[0] * 40
                block.rect.y = SCREEN_HEIGHT - platform[1] * 40 - 40
                block.player = self.player
                self.enemy_list.add(block)

def main():
    global position
    """ Main Program """
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.Sound('stereomadness.ogg').play(-1)
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    coin_tracker = CoinTracker()

    pygame.display.set_caption("Geometry Dash")
    player = Player()

    levels = [Level_01(player, coin_tracker), Level_02(player, coin_tracker), Level_03(player, coin_tracker)]
    lno = 0
    active_sprite_list = pygame.sprite.Group()
    current_level = levels[lno]
    player.level = current_level

    player.rect.x = 40*8
    player.rect.y = SCREEN_HEIGHT - player.rect.height +40
    active_sprite_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    grid = MovingGrid(SCREEN_WIDTH, SCREEN_HEIGHT)
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.go_left()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.go_right()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.jump = True
                if event.key == pygame.K_p:
                    print(position)

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and player.change_x < 0:
                    player.stop()
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and player.change_x > 0:
                    player.stop()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.jump = False

        # Draw other game elements

        grid.update(player.change_x, player.change_y)
        current_level.draw(screen, grid)
        active_sprite_list.draw(screen)
        screen.blit(pygame.image.load('nocoin.png'), (20, 20))
        screen.blit(pygame.image.load('nocoin.png'), (70, 20))
        screen.blit(pygame.image.load('nocoin.png'), (120, 20))
        for i, coin_order in enumerate(coin_tracker.coins_collected):
            screen.blit(coin_tracker.coin_image, (20 + (int(coin_order)-1) * 50, 20))
        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()
        position = (player.rect.x - current_level.world_shift - 320) / 40

        if position < 78 and position > -10:
            # If the player gets near the right side, shift the world left (-x)
            if player.rect.right >= 600:
                diff = player.rect.right - 600
                player.rect.right = 600
                current_level.shift_world(-diff)

            # If the player gets near the left side, shift the world right (+x)
            if player.rect.left <= 400:
                diff = 400 - player.rect.left
                player.rect.left = 400
                current_level.shift_world(diff)
        if position > 85:
            if lno < len(levels) - 1:
                player.rect.x = 40 * 8
                lno += 1
                current_level = levels[lno]
                player.level = current_level
                coin_tracker.reset()



        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == "__main__":
    main()

# location 84 = win