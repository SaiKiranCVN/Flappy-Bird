import pygame as pg
import sys
import random

pg.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512) # To avoid sound latency
pg.init()


screen = pg.display.set_mode((576, 1024))  # Since images are half the size, we can easily scale them
clock = pg.time.Clock()  # For FPS
game_font = pg.font.Font('04b19.ttf',40)


# Game Variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = 0
game_over_surface = pg.transform.scale2x(pg.image.load('./sprites/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (288,512))

flap_sound = pg.mixer.Sound('./audio/wing.wav')
death_sound = pg.mixer.Sound('./audio/hit.wav')
score_sound = pg.mixer.Sound('./audio/point.wav')
score_count_down = 100


bg_surface = pg.image.load(
    './sprites/background-day.png').convert()  # Convert is not needed, but it converts image so that it runs fastly on pygame
bg_surface = pg.transform.scale2x(bg_surface)  # Scale twice


floor_surface = pg.image.load('./sprites/base.png').convert()
floor_surface = pg.transform.scale2x(floor_surface)
floor_x_pos = 0


bird_downflap = pg.transform.scale2x(pg.image.load('./sprites/yellowbird-downflap.png').convert())
bird_midflap = pg.transform.scale2x(pg.image.load('./sprites/yellowbird-midflap.png').convert())
bird_upflap = pg.transform.scale2x(pg.image.load('./sprites/yellowbird-upflap.png').convert())
bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (100,512))
BIRDFLAP = pg.USEREVENT + 1
pg.time.set_timer(BIRDFLAP,200)

# bird_surface = pg.image.load('./sprites/yellowbird-midflap.png').convert()
# bird_surface = pg.transform.scale2x(bird_surface)
# bird_rect = bird_surface.get_rect(center=(100, 512))  # For easy bird movement


pipe_surface = pg.image.load('./sprites/pipe-green.png').convert()
pipe_surface = pg.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pg.USEREVENT
pg.time.set_timer(SPAWNPIPE,1200) # Event triggered every 1.2s
pipe_height = [400,600,800]


# Title and Caption Icon - 32x32
pg.display.set_caption('Flappy Bird')
icon = pg.image.load('favicon.ico')
pg.display.set_icon(icon)



def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 912))
    screen.blit(floor_surface, (floor_x_pos + 576, 912))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes

def draw_pipes(pipes):
    for pipe in pipe_list:
        if pipe.bottom >= 1024: # Only bottom pipe can go below the screen
            screen.blit(pipe_surface,pipe)
        else:
            flip_pipe = pg.transform.flip(pipe_surface,False,True) # False in X direction, True in Y direction
            screen.blit(flip_pipe,pipe)

def check_collisions(pipes):
    if bird_rect.top <= -80 or bird_rect.bottom >= 912:
        #print('Collision')
        return False
    for pipe in pipes:
        if  bird_rect.colliderect(pipe):
            #print('Collision')
            if game_active:
                death_sound.play()
            return False
    return True


def rotate_bird(bird):
    new_bird = pg.transform.rotate(bird,-bird_movement*3)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100,bird_rect.centery)) # Use the y of previous bird
    return new_bird,new_bird_rect


def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)),True, (255,255,255)) # True is Anti-Aliasing on, (255,255,255) - white
        score_rect = score_surface.get_rect(center = (288,100))
        screen.blit(score_surface,score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score : {int(score)}',True, (255,255,255)) # True is Anti-Aliasing on, (255,255,255) - white
        score_rect = score_surface.get_rect(center = (288,100))
        screen.blit(score_surface,score_rect)

        high_score_surface = game_font.render(f'High Score : {int(high_score)}',True, (255,255,255)) # True is Anti-Aliasing on, (255,255,255) - white
        high_score_rect = high_score_surface.get_rect(center = (288,850))
        screen.blit(high_score_surface,high_score_rect)



while True:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 12
                flap_sound.play()
            if event.key == pg.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100,512)
                bird_movement = 0
                score = 0
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == SPAWNPIPE:
            bird_index = (bird_index + 1) % 3
            bird_surface,bird_rect = bird_animation()


    # Background
    screen.blit(bg_surface, (0, 0))
    game_active = check_collisions(pipe_list)

    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface) # Creating new surface for rotation as rotating in pygame results in loss in quality of the image
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        score += 0.01
        score_display('main_game')
        score_count_down -= 1
        if score_count_down == 0:
            score_sound.play()
            score_count_down = 100
    else:
        screen.blit(game_over_surface,game_over_rect)
        high_score = max(score,high_score)
        score_display('game_over')

    # Floor
    floor_x_pos -= 1
    draw_floor()
    # screen.blit(floor_surface, (floor_x_pos, 912))
    if floor_x_pos <= -576:
        floor_x_pos = 0
    pg.display.update()
    clock.tick(120)  # 120 FPS

