import os
import pygame
import neat
import time
import random


# define global variables
WINDOW_WIDTH = 570 # window width size
WINDOW_HEIGHT = 700 # window height size


BIRD_IMGS = [ # load every bird image in the 'imgs' folder and scale 2x
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
    ]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png'))) # load the pipe img and scale 2x
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png'))) # load the base img and scale 2x
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'background.png'))) # load the background img and scale 2x

# bird class
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

# draw the background image and the bird
def draw_window(win, bird):
    win.blit(BACKGROUND_IMG, (0,0)) # draw the background with the topleft corner as the initial point
    bird.draw(win) # call the draw method on bird object
    pygame.display.update() # update the screen

# main function is the one that really run the game looping
def main():
    clock = pygame.time.Clock() # create a clock type object that will control the game fps
    bird = Bird(200, 200) # make the bird object
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # set the main window
    run = True # set the main loop condition variable

    while run: # initializes the loop
        clock.tick(60) # set the frame to 30fps
        for event in pygame.event.get(): # for each event(like mouse click, etc...) on game
            if event.type == pygame.QUIT: # if the event is that user click the big red X on top right corner
                run = False # set the loop condition variable to false and ends the loop

        bird.move() # move the bird
        draw_window(win, bird) # draw the bird movement on the screen

    pygame.quit() # quit the game
    quit() # qui the window

main()