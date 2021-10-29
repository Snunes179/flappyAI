import os
import pygame
import neat
import time
import random
pygame.font.init()

# define global variables
WINDOW_WIDTH = 500 # window width size
WINDOW_HEIGHT = 800 # window height size

GEN = 0

BIRD_IMGS = [ # load every bird image in the 'imgs' folder and scale 2x
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
    ]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png'))) # load the pipe img and scale 2x
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png'))) # load the base img and scale 2x
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'background.png'))) # load the background img and scale 2x
STAT_FONT = pygame.font.SysFont("comicsans", 50)

# bird object class
class Bird:
    IMGS = BIRD_IMGS # load bird imgs inside the class
    MAX_ROTATION = 25 # controls the rotation of the bird as like the nose up when jumps, and etc..
    ROTATION_VELOCITY = 20 # controls the rotation of the bird
    ANIMATION_TIME = 5 # controls the switching imgs to make the flapping wing animation

    def __init__(self, x, y):
        self.x = x # define where the player is in the X axis
        self.y = y # define where the player is in the Y axis
        self.tilt = 0 
        self.tick_count = 0 # define the counter for every key pressed, like how many times the moved since the last jump
        self.velocity = 0 # define velocity of the bird
        self.height = self.y # defien the height of the bird
        self.img_count = 0 
        self.img = self.IMGS[0] # loads the bird imsg to init

    def jump(self):
        self.velocity = -10.5   # set the velocity on jump to move higher 
                                # on pygame, or python itself, plus velocity in Y axis
                                # means the player is going down as you are adding the velocity to its pixels
                                # otherwise, when you have minus Y axis velocity, you are subtracting form pixels
        self.tick_count = 0 # return to zero every time a key is pressed, like how many times the moved since the last jump
        self.height = self.y # define height

    def move(self): # move the bird horizontaly
        self.tick_count += 1 # tracking the movement of the bird, like how many times the moved since the last jump
        displacement_var = (self.velocity*self.tick_count + 1.5*self.tick_count**2)  # how many pixels we are moving up or down in this frame
                        # (self.velocity*self.tick_count + 1.5*self.tick_count**2) is a exponencial physic formula to calculate the movement of the bird

        if displacement_var >= 16: # setting up a temrinal velocity
            displacement_var = 16

        if displacement_var < 0: # controls the extra up moving on jump
            displacement_var -= 2

        self.y = self.y + displacement_var # change the Y axis position based on displacement variable

        # checking the position to set the tilting of the bird
        if displacement_var < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION: # just to not tilt the bird backwards or other crazy direction
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90: # tilting the bird downward
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, win):
        self.img_count += 1 # keeping track of how many times the main game loop is executed
                            # animation purpose

        # setting up the bird animation based on what img has to be shown on the current img count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # rotate the image on the screen
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # drwing the bird on screen
        win.blit(rotated_image, new_rectangle.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
# pipe object class
class Pipe:
    GAP = 200 # this is the spacing between pipes, just the place where the bird must pass
    VELOCITY = 5 # this is how fiast the pipes will move in the screen
    
    def __init__(self, x): # initializes the pipe
        self.x = x # define the pipe position on the screen
        self.height = 0 # define it's height
        self.gap = 100 # define the gap where the bird must pass
        
        self.top = 0 # define position that the flipped pipe must be
        self.bottom = 0 # define position that the pipe must be
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # flip the pipe, to make the upside down pipe
        self.PIPE_BOTTOM = PIPE_IMG # get the img for the normal pipe placed ate the bottom
        
        self.passed = False # check if the bird passes the pipe without collide
        self.set_height() # set the pipe height and the gap
        
    def set_height(self): # set the height of the pipes and calculates the GAP of it
        self.height =  random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self): # move the pipe foward to the bird
        self.x -= self.VELOCITY
        
    def draw(self, win): # draw the pipes on the screen
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird): # check the collide between the bird and the pipe
        bird_mask = bird.get_mask() # get the bird mask from it's image
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # get the mask from the upside down pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # get the mask from the normal pipe
        
        top_offset = (self.x - bird.x, self.top - round(bird.y)) # get the distance between the bird and the top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # get the distance between the bird and the bottom pipe
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) # check the pixels for collision between bird and the bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset) # check the pixels for collision between bird and the top pipe
        
        if t_point or b_point: # if the collisions is not none, we set the collision as True
            #print("COLLISION DETECTED!!!!!")
            return True

        return False # if not collision is False
    
# base object class
class Base:
    VELOCITY = 5 # set the velocity that the base will move
    WIDTH = BASE_IMG.get_width() # set the width of the base img
    IMG = BASE_IMG # get the base img
    
    def __init__(self, y): # initializes the base image
        self.y = y # define the position of the base
        self.x1 = 0 # define the width of the first base image
        self.x2 = self.WIDTH # define the width of the second base image
        
    def move(self): # function that will move the base on the screen
        self.x1 -= self.VELOCITY # modify the velocity of the base for the first image
        self.x2 -= self.VELOCITY # modify the velocity of the base for the second image
        
        if self.x1 + self.WIDTH < 0: # if the first image go outside of the screen, it will go to after the  second image
                                     # that will create the efect of infinite base image, or at least a very very very large image
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, win): # function that will draw our images inside the screen
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        
# draw the background image and the bird
def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BACKGROUND_IMG, (0,0)) # draw the background with the topleft corner as the initial point
    
    for pipe in pipes: # for each pipe inside our object
        pipe.draw(win) # this will draw the pipes
    
    text = STAT_FONT.render("Score:" + str(score), 1, (255,255,255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    
    text = STAT_FONT.render("Gen:" + str(gen), 1, (255,255,255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 60))
    text = STAT_FONT.render("Pop:" + str(len(birds)), 1, (255,255,255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 110))    
    base.draw(win) # draw the base on the screen
    
    for bird in birds:
        bird.draw(win) # call the draw method on bird object
    
    pygame.display.update() # update the screen

# main function is the one that really run the game looping
def fitnessFunction(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = [] # make the bird object
    fps = 30
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    score = 0
    clock = pygame.time.Clock() # create a clock type object that will control the game fps
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # set the main window
    run = True # set the main loop condition variable

    while run: # initializes the loop
        clock.tick(fps) # set the frame to 30fps
        for event in pygame.event.get(): # for each event(like mouse click, etc...) on game
            if event.type == pygame.QUIT: # if the event is that user click the big red X on top right corner
                run = False # set the loop condition variable to false and ends the loop
                pygame.quit() # quit the game
                quit() # qui the window

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
                
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump()

        #bird.move() # move the bird
        add_pipe = False
        rem = []
        for pipe in pipes: # cause we want at least more than one pipe on the screen
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    #birds.remove(bird)
            
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            pipe.move()
        
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            next_pipe_position = random.randint(490, 600)
            print("======================== IN GAME STATS ========================")
            print("CURRENT SCORE:", score)
            print("NEXT PIPE:", next_pipe_position)
            print("GAME VELOCITY: " + str(fps) + "fps")
            print("====================================================================")
            pipes.append(Pipe(next_pipe_position))
            
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):  
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        if score >= 50:
            break
        
        base.move() # move the base
        draw_window(win, birds, pipes, base, score, GEN) # draw the bird movement on the screen



#main()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    birds_population = neat.Population(config)
    
    birds_population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    birds_population.add_reporter(stats)
    
    winner = birds_population.run(fitnessFunction, 30)
    print("======================>  WINNER!!  <======================")
    print("Winner:", winner)
    print("==========================================================")

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedfoward.txt")
    run(config_path)