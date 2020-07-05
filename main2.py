import pygame as pg
import sys
import random
import os
import neat


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

#flap_sound = pg.mixer.Sound('./audio/wing.wav')
#death_sound = pg.mixer.Sound('./audio/hit.wav')
#score_sound = pg.mixer.Sound('./audio/point.wav')
score_count_down = 100


bg_surface = pg.image.load('./sprites/background-day.png').convert()  # Convert is not needed, but it converts image so that it runs fastly on pygame
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



pipe_surface = pg.image.load('./sprites/pipe-green.png').convert()
pipe_surface = pg.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pg.USEREVENT
pg.time.set_timer(SPAWNPIPE,2500) # Event triggered every 1.2s
pipe_height = [400,600,800]


# Title and Caption Icon - 32x32
pg.display.set_caption('Flappy Bird')
icon = pg.image.load('favicon.ico')
pg.display.set_icon(icon)


# Pipe points
pipe_top = (10**9,10**9)
pipe_bot = (10**9,10**9)


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
            pipe_bot = pipe.midtop
            print('top',pipe_bot)
            screen.blit(pipe_surface,pipe)
        else:
            flip_pipe = pg.transform.flip(pipe_surface,False,True) # False in X direction, True in Y direction
            pipe_top = pipe.midbottom
            print('bot',pipe_bot)
            screen.blit(flip_pipe,pipe)

def check_collisions(pipes,bird_rect):

    if bird_rect.top <= -80 or bird_rect.bottom >= 912:
        #print('Collision')
        return False
    for pipe in pipes:
        if  bird_rect.colliderect(pipe):
            return False
    return True


def rotate_bird(bird):
    #print(type(bird))
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


# Neat

birds = []

def fit_fn(genomes,config):
    nets = []
    ge = []
    birds = []
    global bird_index
    global screen
    global gravity
    global bird_movement
    global bird_frames
    global clock
    global score
    global high_score
    global score_count_down
    global BIRDFLAP
    global SPAWNPIPE
    global pipe_list
    global floor_x_pos






    for _,g in genomes: # id and object
        net = neat.nn.FeedForwardNetwork.create(g,config)
        bird_surface = bird_frames[bird_index]
        bird_rect = bird_surface.get_rect(center = (100,512))
        nets.append(net)
        birds.append([bird_surface,bird_rect])
        g.fitness = 0
        ge.append(g)



    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE: #and game_active:
                    bird_movement = 0
                    bird_movement -= 12
                    #flap_sound.play()
                # if event.key == pg.K_SPACE and game_active == False:
                #     game_active = True
                #     pipe_list.clear()
                #     bird_rect.center = (100,512)
                #     bird_movement = 0
                #     score = 0
            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe())
                if len(pipe_list)>=4:
                    pipe_list = pipe_list[2:]


            if event.type == BIRDFLAP:
                bird_index = (bird_index + 1) % 3
                for i,bird in enumerate(birds):
                    bird_surface,bird_rect = bird_animation()
                    birds[i] =  [bird_surface,bird_rect]


        # Background
        screen.blit(bg_surface, (0, 0))
        game_active = False # For last bird
        for i,bird in enumerate(birds):
            x = check_collisions(pipe_list,bird[1]) # 0 - surface, 1- rect , collision - False, not-collision - True
            #game_active = game_active or x
            if not x: 
                ge[i].fitness -= 1
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)
        # for g in ge:
        #     g.fitness += 5



        if len(birds)>0:
            # Bird
            for i,bird in enumerate(birds):
                bird_movement += gravity
                rotated_bird = rotate_bird(bird[0]) # Creating new surface for rotation as rotating in pygame results in loss in quality of the image
                bird[1].centery += bird_movement
                screen.blit(rotated_bird, bird[1])
                ge[i].fitness += 0.1

                output = nets[i].activate((bird[1].centery,(bird[1].centerx-pipe_top[0])**2 + (bird[1].centery - pipe_top[1])**2,(bird[1].centerx-pipe_bot[0])**2 + (bird[1].centery - pipe_bot[1])**2)) # its a list, here the list has only one element
                #a =  abs(bird[1].centery- pipe_top)
                #b = abs(bird[1].centery-pipe_bot)
                #output = nets[i].activate((bird[1].centery,abs(bird[1].centery- pipe_top),abs(bird[1].centery-pipe_bot)))
                if output[0] > 0.5:
                    newevent = pg.event.Event(pg.KEYDOWN, unicode=" ", key=pg.K_SPACE) #create the event
                    pg.event.post(newevent) #add the event to the queue

            # Pipes
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
            score += 0.01
            score_display('main_game')
            score_count_down -= 1
            if score_count_down == 0:
                #score_sound.play()
                score_count_down = 100
        else:
            #screen.blit(game_over_surface,game_over_rect)
            #high_score = max(score,high_score)
            #score_display('game_over')
            pipe_list.clear()
            bird_rect.center = (100,512)
            bird_movement = 0
            score = 0
            break


        # Floor
        floor_x_pos -= 1
        draw_floor()
        # screen.blit(floor_surface, (floor_x_pos, 912))
        if floor_x_pos <= -576:
            floor_x_pos = 0
        pg.display.update()
        clock.tick(60)  # 30 FPS








def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,neat.DefaultStagnation, config_path) # Load Population
    
    p = neat.Population(config) # Set Population
    
    # Display status about our each population
    p.add_reporter(neat.StdOutReporter(True))   
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(fit_fn,2500) # fitness Fn, 50 - number of generations to run for


if __name__ == "__main__":
    path = os.path.dirname(__file__)  # Get pwd
    config_path = os.path.join(path,'config.txt')
    run(config_path)
