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

# Audio settings
pygame.mixer.init()
# Background music
pygame.mixer.music.load('assets/audios/air-combat.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0, 0)
# Audio effects
shooting_sound = pygame.mixer.Sound('assets/audios/laser-gun-shot.wav')
shooting_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound('assets/audios/arcade-game-explosion-echo.wav')
shooting_sound.set_volume(0.5)

# Font settings
font = pygame.font.SysFont('calibri', 15)
font1 = pygame.font.SysFont('comicsansms', 100)
game_over_text = font1.render('Game Over', 0, 'red')
game_over_text_rect = game_over_text.get_rect()
game_over_text_rect.center = (WIDTH / 2, HEIGHT / 2)

# Game settings
SCORELEVEL = 10000
LEVEL = pygame.time.get_ticks()
# Enemies setting
ENEMY_SPAWN_TIME = 1000   # Spawn 2 enemy per second
LAST_SPAWN = 0  # Track Enemy Spawn Time
DEFEAT_ENEMY = 0
enemies = pygame.sprite.Group()
# Bullet settings
BULLET_COOLDOWN = 100  # 1 bullet every 0.1 s
bullet_image = pygame.image.load('assets/images/bullet/bullet.png')
bullets = pygame.sprite.Group()
last_shooting = 0
# Meteor setting
meteor_image = pygame.image.load('assets/images/meteor/meteor.png')


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


class Enemy(Ship):
    def __init__(self):
        super().__init__('enemy')
        self.rect.center = (randint(0, WIDTH), 0)  # Initial position
        self.x_vel = 0
        self.y_vel = 5
        self.x_accel = 0
        self.y_accel = 0.01

    def move(self):
        if self.rect.centery > WIDTH + 10:
            self.kill()
        self.rect.centery += self.y_vel


class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = meteor_image
        self.rect = self.image.get_rect()
        self.rect.center = (randint(0, WIDTH), 0)
        self.y_vel = 3

    def move(self):
        if self.rect.centery > WIDTH + 10:
            self.kill()
        self.rect.centery += self.y_vel


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.y_vel = -10

    def move(self):
        if self.rect.centery < -10:
            self.kill()
        self.rect.centery += self.y_vel


def spawn_enemy():
    global LAST_SPAWN
    current_time = pygame.time.get_ticks()
    if (current_time - LAST_SPAWN >= ENEMY_SPAWN_TIME) or len(enemies) == 0:
        spawn = randint(0, 1)
        # Random spawn
        if spawn:
            e = Enemy()
        else:
            e = Meteor()
        enemies.add(e)
        LAST_SPAWN = current_time


def update_enemies():
    # Update frames and enemies movements
    for e in enemies:
        if type(e) is not Meteor:
            e.update_frame()
        e.move()


def create_bullet(pos):
    global last_shooting
    current_time = pygame.time.get_ticks()
    # Check cooldown so player cannot spam
    if current_time - last_shooting > BULLET_COOLDOWN:
        bullet = Bullet(pos)
        shooting_sound.play()
        # print(bullet)
        bullets.add(bullet)
        last_shooting = current_time
        # print(last_shooting)


def update_bullets():
    for bullet in bullets:
        # Remove bullet from bullets if passed screen height
        if bullet.rect.centery <= -10:
            bullets.remove(bullet)
        bullet.move()


def display_info():
    # Display information: score, destroyed ships, etc
    info = [
        ['Score', round(pygame.time.get_ticks(), 1)],
        ['Dead Enemy', DEFEAT_ENEMY]
    ]
    space = 20
    for title, data in info:
        text = font.render(f'{title}: {data}', 0, 'white')
        screen.blit(text, (30, 10 + space))
        space += space


def level_up():
    global LEVEL
    global ENEMY_SPAWN_TIME
    current_time = pygame.time.get_ticks()
    # When level up: add speed to sprites and add one sprite to all sprites
    if current_time - LEVEL >= SCORELEVEL:
        # Add speed
        for e in enemies:
            e.y_vel += 1
        # Get more spawn in less time
        ENEMY_SPAWN_TIME = ENEMY_SPAWN_TIME / 2
        LEVEL = current_time


def game_over():
    # Game over when player collide
    pygame.mixer.music.stop()
    explosion_sound.play()
    screen.fill('black')
    screen.blit(game_over_text, game_over_text_rect)
    pygame.display.update()
    pygame.time.delay(1500)


# Create player
player = Player()

# Pygame main loop
while run:
    clock.tick(FPS)
    screen.blit(background, (0, 0))
    display_info()
    level_up()

    # Enemy Spawn
    spawn_enemy()

    # Player movements
    player.draw()
    player.move()
    player.update_frame()

    # Enemy movements
    update_enemies()
    # Draw all enemies on screen
    enemies.draw(screen)

    # Bullet movements
    update_bullets()
    # Draw all bullet on screen
    bullets.draw(screen)

    # Check bullet and enemy collision
    if pygame.sprite.groupcollide(bullets, enemies, True, True):
        DEFEAT_ENEMY += 1

    # Check if player collides to any enemy
    if pygame.sprite.spritecollide(player, enemies, True):
        game_over()
        run = False
        break

    for event in pygame.event.get():
        # Exit game
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
                break
            # Player shooting
            if event.key == pygame.K_SPACE:
                create_bullet((player.rect.centerx, player.rect.top))
            # Check Player movements
            if event.key == pygame.K_LEFT:
                player.k_left = True
            elif event.key == pygame.K_RIGHT:
                player.k_right = True
            if event.key == pygame.K_UP:
                player.k_up = True
            elif event.key == pygame.K_DOWN:
                player.k_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player.k_left = False
            elif event.key == pygame.K_RIGHT:
                player.k_right = False
            if event.key == pygame.K_UP:
                player.k_up = False
            elif event.key == pygame.K_DOWN:
                player.k_down = False

    pygame.display.flip()
pygame.quit()
quit()
