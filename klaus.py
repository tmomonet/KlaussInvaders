import random
import gif_pygame
import pygame
from pygame import mixer

#initialize audio
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

pygame.font.init()

#fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Library Invaders')

# define fonts
font30 = pygame.font.SysFont('ComicSans', 30)
font40 = pygame.font.SysFont('ComicSans', 40)

# load sounds
explosion_fx = pygame.mixer.Sound("audio/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("audio/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("audio/laser.wav")
laser_fx.set_volume(0.25)

hello_fx = pygame.mixer.Sound("audio/hello_fellow_human.wav")
hello_fx.set_volume(0.15)

# define game variables
rows = 5
cols = 5
patron_cooldown = 750
last_patron_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0


#define colors
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)


# Load BG and gifs
victory_screen = gif_pygame.load("img/win.gif")
loss_screen = gif_pygame.load("img/game_over.gif", 0)

def load_random_bg():
    return pygame.image.load(f"img/bg{random.randint(1,4)}.png").convert()

bg = load_random_bg()

def draw_bg():
    screen.blit(bg, (0,0))

# define function for creating text
def draw_text(text, font, txt_color, x, y):
    img = font.render(text, True, txt_color)
    screen.blit(img, (x, y))

def draw_button(text, font, txt_color, btn_color, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, btn_color, rect, border_radius=10)
    pygame.draw.rect(screen, white, rect, 2, border_radius=10)  # outline

    label = font.render(text, True, txt_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect

def clear_groups():
    klauss_group.empty()
    bullets_group.empty()
    patrons_group.empty()
    patron_bullets_group.empty()
    explosion_group.empty()

def reset_game():
    global klauss, game_over, countdown, last_count, last_patron_shot, bg

    bg = load_random_bg()

    # clear everything
    clear_groups()
    draw_bg()
    # recreate patrons + player
    create_patrons()
    klauss = Klauss(int(screen_width/2), screen_height - 100, 3)
    klauss_group.add(klauss)

    # reset timers/state
    game_over = 0
    countdown = 3
    last_count = pygame.time.get_ticks()
    last_patron_shot = pygame.time.get_ticks()

def game_over_screen(game_over):
    if game_over == -1:
        clear_groups()
        loss_screen.render(screen, (0,0))
    if game_over == 1:
        victory_screen.render(screen, (0,0))

# create Klauss class
class Klauss(pygame.sprite.Sprite):
    def __init__(self, x , y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/klauss.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 8

        #set cooldown
        cooldown = 500 # milliseconds

        game_over = 0

        #get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        #record current time
        time_now = pygame.time.get_ticks()

        #shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullets_group.add(bullet)
            laser_fx.play()
            self.last_shot = time_now

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * self.health_remaining / self.health_start), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            explosion2_fx.play()
            self.kill()
            game_over = -1
        return game_over

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, patrons_group, True):
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            explosion_fx.play()

class Patrons(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/patron' + str(random.randint(1, 5))  + '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1


    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

class Patron_Bullets(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/patron_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 3
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, klauss_group, False, pygame.sprite.collide_mask):
            klauss.health_remaining -= 1
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            explosion_fx.play()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x , y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            self.image = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(self.image, (20, 20))
            if size == 2:
                img = pygame.transform.scale(self.image, (40, 40))
            if size == 3:
                img = pygame.transform.scale(self.image, (160, 160))
            self.images.append(img)
        self.index  = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #update explosion counter
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if animation is complete, delete
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# create sprite groups
klauss_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
patrons_group = pygame.sprite.Group()
patron_bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_patrons():
    # generate patrons
    for row in range(rows):
        for item in range(cols):
            patron = Patrons(100 + item * 100, 100 + row * 70)
            patrons_group.add(patron)

create_patrons()

#create player
klauss = Klauss(int (screen_width/2), screen_height - 100, 3)
klauss_group.add(klauss)

run = True
while run:

    clock.tick(fps)

    # draw background
    draw_bg()

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False

    if countdown == 0:

    # create random patron bullets
        time_now = pygame.time.get_ticks()
        # shoot
        if time_now - last_patron_shot > patron_cooldown and len(patron_bullets_group) <  7 and len(patrons_group) > 0:
            attacking_patron = random.choice(patrons_group.sprites())
            patron_bullets = Patron_Bullets(attacking_patron.rect.centerx, attacking_patron.rect.bottom)
            patron_bullets_group.add(patron_bullets)
            last_patron_shot = time_now

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    reset_game()
                elif quit_rect.collidepoint(event.pos):
                    run = False
        if countdown == 0 and game_over == 0:
            if len(patrons_group) == 0:
                game_over = 1
                clear_groups()  # clean end screen

        if game_over == 0:
            #update Klauss
            game_over = klauss.update()

            #update sprite groups
            bullets_group.update()
            patrons_group.update()
            patron_bullets_group.update()

        else:
            game_over_screen(game_over)
            # buttons
            play_rect = draw_button("Play Again", font30, white, green, int(screen_width / 2 - 120), int(screen_height / 2 + 200), 240, 60)
            quit_rect = draw_button("Quit", font30, white, red, int(screen_width / 2 - 120), int(screen_height / 2 + 275), 240, 60)

            # handle clicks (IMPORTANT: you still need to pump events here)
            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_rect.collidepoint(event.pos):
                        reset_game()
                    elif quit_rect.collidepoint(event.pos):
                        run = False

    if countdown > 0:
        draw_text("Hello, fellow human",font40, white, int(screen_width/2 - 190), int(screen_height/2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width/2 - 10), int(screen_height/2 + 100))
        if countdown == 1:
            hello_fx.play()
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    #update explosion group
    explosion_group.update()

    # draw sprite groups
    klauss_group.draw(screen)
    bullets_group.draw(screen)
    patrons_group.draw(screen)
    patron_bullets_group.draw(screen)
    explosion_group.draw(screen)

    pygame.display.update()

pygame.quit()