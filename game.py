import pygame
from random import randint

pygame.init()
run = True

# Display settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PySpaceWars')
background = pygame.image.load('assets/images/background.jpg')

# Frame settings
clock = pygame.time.Clock()
FPS = 60


# Spaceship parent class for enemy's ship and player
class Ship(pygame.sprite.Sprite):
    def __init__(self, character):
        super().__init__()
        self.static_frame_timer = pygame.time.get_ticks()
        self.static_frame_index = 1
        self.static_frames = [pygame.image.load(f'assets/images/{character}/{i}.png') for i in range(1, 7)]

        self.image = pygame.image.load(f'assets/images/{character}/1.png')  # Initial frame
        self.rect = self.image.get_rect()

    def update_frame(self):
        current_time = pygame.time.get_ticks()
        # Update frame every 50 milliseconds
        if current_time - self.static_frame_timer >= 50:
            self.static_frame_index += 1
            self.image = self.static_frames[self.static_frame_index]
            self.static_frame_timer = current_time
            if self.static_frame_index == 5:
                self.static_frame_index = 1

    def draw(self):
        # Draw player to screen
        screen.blit(self.image, self.rect)


class Enemy(Ship):
    def __init__(self):
        super().__init__('enemy')
        self.rect.center = (randint(0, WIDTH), 0)  # Initial position
        self.x_vel = 0
        self.y_vel = 5
        self.x_accel = 0
        self.y_accel = 0.01

    def move(self):
        if self.rect.centery == HEIGHT:
            self.rect.centery = 0
            self.rect.centerx = randint(0, WIDTH)
        self.rect.centery += self.y_vel


class Player(Ship):
    def __init__(self):
        super().__init__('player')
        self.rect.center = (400, 500)  # Initial position

        self.x_vel = 5
        self.y_vel = 5
        self.is_moving = False
        self.k_right = False
        self.k_left = False
        self.k_up = False
        self.k_down = False

    def move(self):
        # Teleport Xpos of player when out of boundaries
        if self.rect.centerx < 0:
            self.rect.centerx = WIDTH
        if self.rect.centerx > WIDTH:
            self.rect.centerx = 0
        if self.k_up:
            self.rect.centery -= self.y_vel
        elif self.k_down:
            self.rect.centery += self.y_vel
        if self.k_left:
            self.rect.centerx -= self.x_vel
        elif self.k_right:
            self.rect.centerx += self.x_vel


# Create game objects
player = Player()
enemy = Enemy()

# Pygame main loop
while run:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    # Player movements
    player.draw()
    player.move()
    player.update_frame()

    # Enemy movements
    enemy.draw()
    enemy.move()
    enemy.update_frame()

    player.rect.colliderect(enemy)
    for event in pygame.event.get():
        # Exit game
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
                break
            # Check Player movements
            if event.key == pygame.K_LEFT:
                player.k_left = True
            if event.key == pygame.K_RIGHT:
                player.k_right = True
            if event.key == pygame.K_UP:
                player.k_up = True
            if event.key == pygame.K_DOWN:
                player.k_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player.k_left = False
            if event.key == pygame.K_RIGHT:
                player.k_right = False
            if event.key == pygame.K_UP:
                player.k_up = False
            if event.key == pygame.K_DOWN:
                player.k_down = False

    pygame.display.flip()
pygame.quit()
quit()
