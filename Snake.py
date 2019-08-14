import pygame
from pygame.locals import *
import random
import numpy as np
import math


# ---------- constants ---------- #
# size of each grid
TILE_SIZE = (10, 10)

# number of grid of the screen
SCREENTILES = (20, 20)

TILE_RECT = pygame.Rect(0, 0, TILE_SIZE[0], TILE_SIZE[1])
SCREENSIZE = ((SCREENTILES[0]+1)*TILE_SIZE[0], (SCREENTILES[1]+1)*TILE_SIZE[1])
SCREENRECT = pygame.Rect(0, 0, SCREENSIZE[0], SCREENSIZE[1])

# position of snake at start
START_TILE = (5, 5)
# lenght of snake at start
START_SEGMENTS = 4


SNAKE_HEAD_RADIUS = 13
SNAKE_SEGMENT_RADIUS = 17
FOOD_RADIUS = SNAKE_SEGMENT_RADIUS

CAPTION = 'MiniSnake'
FPS = 30

MOVE_RATE = 1  # how many frame per move
DIFFICULTY_INCREASE_RATE = .09
MOVE_THRESHOLD = 1  # when moverate counts up to this the snake moves
BLOCK_SPAWN_RATE = 2


SCREENTILES = (
    (SCREENSIZE[0] / TILE_SIZE[0]) - 1,
    (SCREENSIZE[1] / TILE_SIZE[1]) - 1
)

BACKGROUND_COLOR = (255, 255, 255)
SNAKE_HEAD_COLOR = (150, 0, 0)
SNAKE_SEGMENT_COLOR = (255, 0, 0)
FOOD_COLOR = (0, 255, 0)
BLOCK_COLOR = (0, 0, 150)
COLORKEY_COLOR = (255, 255, 0)

SCORE_COLOR = (0, 0, 0)
SCORE_POS = (20, 20)
ADDEDTEXT_POS = (20, 30)
SCORE_PREFIX = 'Score: '

STEPS_PREFIX = 'Steps: '
STEPS_POS = ( 140, 20 )

FITNESS_PREFIX = 'Fitnes: '
FITNESS_POS = ( 140, 30 )

LAST_FITNESS_PREFIX = 'Previous: '
LAST_FITNESS_POS = ( 140, 40 )

MOVE_VECTORS = {'left': (-1, 0),
                'right': (1, 0),
                'up': (0, -1),
                'down': (0, 1)
                }
MOVE_VECTORS_PIXELS = {'left': (-TILE_SIZE[0], 0),
                       'right': (TILE_SIZE[0], 0),
                       'up': (0, -TILE_SIZE[1]),
                       'down': (0, TILE_SIZE[1])
                       }


# ----------- game objects ----------- #
class snake_segment(pygame.sprite.Sprite):
    def __init__(self, tilepos, segment_groups, color=SNAKE_SEGMENT_COLOR, radius=SNAKE_SEGMENT_RADIUS):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.image = pygame.Surface(TILE_SIZE).convert()
        self.image.fill(COLORKEY_COLOR)
        self.image.set_colorkey(COLORKEY_COLOR)
        pygame.draw.circle(self.image, color, TILE_RECT.center, radius)
        
        self.tilepos = tilepos
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (tilepos[0] * TILE_SIZE[0], tilepos[1] * TILE_SIZE[1])
        
        self.segment_groups = segment_groups
        for group in segment_groups:
            group.add(self)
            
            self.behind_segment = None
            
            self.movedir = 'left'
            
    # this function adds a segment at the end of the snake
    def add_segment(self):

        seg = self
        while True:
            if seg.behind_segment == None:
                x = seg.tilepos[0]
                y = seg.tilepos[1]
                if seg.movedir == 'left':
                    x += 1
                elif seg.movedir == 'right':
                    x -= 1
                elif seg.movedir == 'up':
                    y += 1
                elif seg.movedir == 'down':
                    y -= 1
                seg.behind_segment = snake_segment((x, y), seg.segment_groups)
                seg.behind_segment.movedir = seg.movedir
                break
            else:
                # looping until we get the last segment of the snake
                seg = seg.behind_segment

    def update(self):
        pass

    def move(self):
        self.tilepos = (
            self.tilepos[0] + MOVE_VECTORS[self.movedir][0],
            self.tilepos[1] + MOVE_VECTORS[self.movedir][1]
        )
        self.rect.move_ip(MOVE_VECTORS_PIXELS[self.movedir])
        if self.behind_segment != None:
            self.behind_segment.move()
            self.behind_segment.movedir = self.movedir


class snake_head(snake_segment):
    def __init__(self, tilepos, movedir, segment_groups):
        snake_segment.__init__(self, tilepos, segment_groups, color=SNAKE_HEAD_COLOR, radius=SNAKE_HEAD_RADIUS)
        self.movedir = movedir
        self.movecount = 0

    def update(self):
        self.movecount += MOVE_RATE
        if self.movecount >= MOVE_THRESHOLD:
            self.move()
            self.movecount = 0

    def get_positions(self):
        seg = self
        positions = []
        while True:
            position = seg.tilepos
            positions.append((position[0], position[1]))
            if seg.behind_segment == None:
                break
            else:
                # looping until we get the last segment of the snake
                seg = seg.behind_segment
        return positions


class food(pygame.sprite.Sprite):
    def __init__(self, takenupgroup):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.image = pygame.Surface(TILE_SIZE).convert()
        self.image.fill(COLORKEY_COLOR)
        self.image.set_colorkey(COLORKEY_COLOR)
        pygame.draw.circle(self.image, FOOD_COLOR, TILE_RECT.center, FOOD_RADIUS)

        self.rect = self.image.get_rect()
        while True:
            self.position = (
                random.randint(0, SCREENTILES[0]),
                random.randint(0, SCREENTILES[1])
            )

            self.rect.topleft = (
                self.position[0] * TILE_SIZE[0],
                self.position[1] * TILE_SIZE[1]
            )
            continue_loop = False
            for sprt in takenupgroup:
                if self.rect.colliderect(sprt):
                    continue_loop = True  # collision, food cant go here
            if continue_loop:
                continue
            else:
                break # no collision, food can go here


class block(pygame.sprite.Sprite):
    def __init__(self, takenupgroup):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.image = pygame.Surface(TILE_SIZE).convert()
        self.image.fill(BLOCK_COLOR)

        self.rect = self.image.get_rect()
        while True:
            self.position = (
                random.randint(0, SCREENTILES[0]),
                random.randint(0, SCREENTILES[1])
            )

            self.rect.topleft = (
                self.position[0] * TILE_SIZE[0],
                self.position[1] * TILE_SIZE[1]
            )
            for sprt in takenupgroup:
                if self.rect.colliderect(sprt):
                    continue  # collision, food cant go here
            break  # no collision, food can go here


class Game():
    def __init__(self):
        pygame.init()
        self.addedText = ''
        self.steps_left = 200
        self.reward = 0
        self.lastFitnes = 0

    def setAddedText(self, text):
        self.addedText = text

    def reset(self):
        # show screen
        self.screen = pygame.display.set_mode(SCREENSIZE)
        pygame.display.set_caption(CAPTION)
        self.bg = pygame.Surface(SCREENSIZE).convert()
        self.bg.fill(BACKGROUND_COLOR)
        self.screen.blit(self.bg, (0, 0))
        
        self.snakegroup = pygame.sprite.Group()
        self.snakeheadgroup = pygame.sprite.Group()
        self.foodgroup = pygame.sprite.Group()
        self.blockgroup = pygame.sprite.Group()
        self.takenupgroup = pygame.sprite.Group()
        self.all = pygame.sprite.RenderUpdates()

        column = SCREENSIZE[0] / TILE_SIZE[0]
        row = SCREENSIZE[1] / TILE_SIZE[1]
        self.BlockPositions = []
        self.grid = np.zeros((int(row), int(column)))
        self.snake = snake_head(START_TILE, 'right', [self.snakegroup, self.all, self.takenupgroup])
        self.snakeheadgroup.add(self.snake)
        for index in range(START_SEGMENTS):
            self.snake.add_segment()

        self.currentfood = 'no food'

        self.block_frame = 0

        self.currentscore = 0
        self.addedText = ''

        # turn screen to white
        pygame.display.flip()

        # mainloop
        self.quit = False
        self.clock = pygame.time.Clock()
        self.lose = False

        self.steps_left = 200
        self.reward = 0

    def step(self, direction):
        currentmovedir = self.snake.movedir
        if direction == 2:
            tomove = currentmovedir
        else:
            if currentmovedir == 'up':
                if direction:
                    tomove = 'right'
                else:
                    tomove = 'left'
            elif currentmovedir == 'right':
                if direction:
                    tomove = 'down'
                else:
                    tomove = 'up'
            elif currentmovedir == 'down':
                if direction:
                    tomove = 'left'
                else:
                    tomove = 'right'
            elif currentmovedir == 'left':
                if direction:
                    tomove = 'up'
                else:
                    tomove = 'down'

        self.snake.movedir = tomove

        # clearing
        self.all.clear(self.screen, self.bg)

        # updates snake position
        self.all.update()

        self.steps_left = self.steps_left - 1

        # getting on reward per frame
        self.reward = self.reward + 1
        if self.currentfood == 'no food':
            self.currentfood = food(self.takenupgroup)
            self.foodgroup.add(self.currentfood)
            self.takenupgroup.add(self.currentfood)
            self.all.add(self.currentfood)

        column = SCREENSIZE[0] / TILE_SIZE[0]
        row = SCREENSIZE[1] / TILE_SIZE[1]
        self.grid = np.zeros((int(row + 2), int(column + 2)))
        self.grid[[0, -1], :] = 4
        self.grid[:, [0, -1]] = 4

        BodyPositions = self.snake.get_positions()

        for i in range(0, len(BodyPositions)):
            # 3 is body part
            position = BodyPositions[i]
            if i == 0:
                self.grid[position[1] + 1, position[0] + 1] = 2
            else:
                self.grid[position[1] + 1, position[0] + 1] = 3

        # 2 is food
        self.grid[self.currentfood.position[1] + 1, self.currentfood.position[0] + 1] = 1



        for i in range(0, len(BodyPositions)):
            # 3 is body part
            position = BodyPositions[i]
            if i == 0:
                self.grid[position[1] + 1, position[0] + 1] = 2
            else:
                self.grid[position[1] + 1, position[0] + 1] = 3

        # print(self.grid)
        pos = self.snake.rect.topleft
        if pos[0] < 0:
            quit.lose = True
            self.lose = True
        if pos[0] >= SCREENSIZE[0]:
            quit.lose = True
            self.lose = True
        if pos[1] < 0:
            quit.lose = True
            self.lose = True
        if pos[1] >= SCREENSIZE[1]:
            quit.lose = True
            self.lose = True

        # collisions
        # head -> tail
        col = pygame.sprite.groupcollide(self.snakeheadgroup, self.snakegroup, False, False)
        for head in col:
            for tail in col[head]:
                if not tail is self.snake:
                    self.quit = True
                    self.lose = True
        # head -> food
        col = pygame.sprite.groupcollide(self.snakeheadgroup, self.foodgroup, False, True)
        for head in col:
            for tail in col[head]:
                self.currentfood = 'no food'
                self.snake.add_segment()
                self.currentscore += 1
                self.reward = self.reward + 1
                self.steps_left = 200
                global MOVE_RATE, DIFFICULTY_INCREASE_RATE
                MOVE_RATE += DIFFICULTY_INCREASE_RATE
                self.block_frame += 1
                if self.block_frame >= BLOCK_SPAWN_RATE:
                    self.block_frame = 0
                    b = block(self.takenupgroup)
                    self.BlockPositions.append((b.position[0], b.position[1]))
                    self.blockgroup.add(b)
                    self.takenupgroup.add(b)
                    self.all.add(b)
        # head -> blocks
        col = pygame.sprite.groupcollide(self.snakeheadgroup, self.blockgroup, False, False)
        for head in col:
            for collidedblock in col[head]:
                quit.lose = True
                self.lose = True

        if self.steps_left < 1:
            quit.lose = True
            self.lose = True

            # game over
        if self.lose == True:
            # f = pygame.font.Font(None, 100)
            # failmessage = f.render('FAIL', True, (0, 0, 0))
            # failrect = failmessage.get_rect()
            # failrect.center = SCREENRECT.center
            # self.screen.blit(failmessage, failrect)
            # pygame.display.flip()
            # pygame.time.wait(20)
            pass
        
        
        # 4 is wall or block
        for i in range(0, len(self.BlockPositions)):
            # 3 is body part
            position = self.BlockPositions[i]
            self.grid[position[1] + 1, position[0] + 1] = 4
            
        fitnes = self.reward + (self.currentscore * 10)
        if self.lose == True:
            self.lastFitnes = fitnes
        return self.getObservation(), fitnes, self.lose, self.currentscore

    def getObservation(self):
        # x = BodyPositions[0][0]
        # y = BodyPositions[0][1]
        x = self.snake.tilepos[0]
        y = self.snake.tilepos[1]

        def loop(x_increment, y_increment, head_x, head_y):

            # adjusting tuple coordinate to array base 0 coordinate
            head_x = head_x + 1
            head_y = head_y + 1
            distance = 0
            base_distance = math.sqrt((x_increment ** 2) + (y_increment ** 2))
            food = -1
            body = -1
            wall = -1

            # moving out of the head of the snake
            x = head_x + x_increment
            y = head_y + y_increment

            max_x = len(self.grid[0])
            max_y = len(self.grid)
            while (x > -1) and (y > -1) and (x < max_x) and (y < max_y):
                if self.grid[y, x] == 3:
                    if body == -1:
                        body = distance
                if self.grid[y, x] == 1:
                    if food == -1:
                        food = distance

                distance += base_distance
                # moving further

                if self.grid[y, x] == 4:
                    if wall == -1:
                        wall = distance

                x += x_increment
                y += y_increment
            # wall = distance
            # maximum_distance = 28.284
            maximum_distance = math.sqrt((SCREENTILES[0] ** 2) + (SCREENTILES[1] ** 2))

            if body == -1:
                body = maximum_distance

            if food == -1:
                food = maximum_distance

            return [wall, food, body]

        if self.snake.movedir == 'left':
            observation = np.array([
                # left
                loop(-1, 0, x, y),

                # up left
                loop(-1, -1, x, y),

                # up
                loop(0, -1, x, y),

                # up right
                loop(1, -1, x, y),

                # right
                loop(1, 0, x, y),

                # down right
                loop(1, 1, x, y),

                # down
                loop(0, 1, x, y),

                # down left
                loop(-1, 1, x, y),

            ])
        elif self.snake.movedir == 'right':
            observation = np.array([
                # right
                loop(1, 0, x, y),

                # down right
                loop(1, 1, x, y),

                # down
                loop(0, 1, x, y),

                # down left
                loop(-1, 1, x, y),

                # left
                loop(-1, 0, x, y),

                # up left
                loop(-1, -1, x, y),

                # up
                loop(0, -1, x, y),

                # up right
                loop(1, -1, x, y),

            ])
        elif self.snake.movedir == 'up':
            observation = np.array([
                # up
                loop(0, -1, x, y),

                # up right
                loop(1, -1, x, y),

                # right
                loop(1, 0, x, y),

                # down right
                loop(1, 1, x, y),

                # down
                loop(0, 1, x, y),

                # down left
                loop(-1, 1, x, y),

                # left
                loop(-1, 0, x, y),

                # up left
                loop(-1, -1, x, y),

            ])
        elif self.snake.movedir == 'down':
            observation = np.array([

                # down
                loop(0, 1, x, y),

                # down left
                loop(-1, 1, x, y),

                # left
                loop(-1, 0, x, y),

                # up left
                loop(-1, -1, x, y),

                # up
                loop(0, -1, x, y),

                # up right
                loop(1, -1, x, y),

                # right
                loop(1, 0, x, y),

                # down right
                loop(1, 1, x, y),
            ])

        observation.shape = (24,)
        scale = math.sqrt(SCREENTILES[0] ** 2 + SCREENTILES[1] ** 2)
        observation_scaled = 1 - 2 * observation / scale
        return observation_scaled
        # return observation
        
    def render(self):
        # score
        d = self.screen.blit(self.bg, SCORE_POS, pygame.Rect(SCORE_POS, (50, 100)))
        f = pygame.font.Font(None, 12)
        scoreimage = f.render(SCORE_PREFIX + str(self.currentscore), True, SCORE_COLOR)
        d2 = self.screen.blit(scoreimage, SCORE_POS)

        # steps
        sd = self.screen.blit(self.bg, STEPS_POS, pygame.Rect(STEPS_POS, (50, 100)))
        sf = pygame.font.Font(None, 12)
        stepsimage = sf.render(STEPS_PREFIX + str(self.steps_left), True, SCORE_COLOR)
        sd2 = self.screen.blit(stepsimage, STEPS_POS)

        # fitness
        fd = self.screen.blit(self.bg, FITNESS_POS, pygame.Rect(FITNESS_POS, (50, 100)))
        ff = pygame.font.Font(None, 12)
        fitnessimage = ff.render(FITNESS_PREFIX + str( self.reward + ( self.currentscore * 2 ) ), True, SCORE_COLOR)
        fd2 = self.screen.blit(fitnessimage, FITNESS_POS)

        # last fitness
        lfd = self.screen.blit(self.bg, LAST_FITNESS_POS, pygame.Rect(LAST_FITNESS_POS, (50, 100)))
        lff = pygame.font.Font(None, 12)
        lastfitnessimage = lff.render(LAST_FITNESS_PREFIX + str( self.lastFitnes ), True, SCORE_COLOR)
        lfd2 = self.screen.blit(lastfitnessimage, LAST_FITNESS_POS)

        # generation
        if self.addedText:
            dd = self.screen.blit(self.bg, ADDEDTEXT_POS, pygame.Rect(ADDEDTEXT_POS, (100, 100)))
            ff = pygame.font.Font(None, 12)
            scoreimage = ff.render( self.addedText, True, SCORE_COLOR)
            dd2 = self.screen.blit(scoreimage, ADDEDTEXT_POS)
            
        # drawing
        dirty = self.all.draw(self.screen)
        dirty.append(d)
        dirty.append(d2)
        dirty.append(sd)
        dirty.append(sd2)
        dirty.append(fd)
        dirty.append(fd2)
        dirty.append(lfd)
        dirty.append(lfd2)
        if self.addedText:
            dirty.append(dd)
            dirty.append(dd2)

        # updating screen
        pygame.display.update(dirty)

        # waiting
        self.clock.tick(FPS)
