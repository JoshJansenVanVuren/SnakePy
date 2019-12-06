# Author: Joshua Jansen Van Vuren
# Date: 30 Nov
# Desc: Basic Snake Game

import random
import curses
import math

#################
# THE CONSTANTS #
#################
SPEED = -12 # recommended values between (-10 and 10)
MODE = 1 #values is 0 for manual and 1 for auto

###############################
# curses handles the terminal #
###############################
screen = curses.initscr()
curses.curs_set(0)
sh, sw = screen.getmaxyx()
w = curses.newwin(sh,sw,0,0)
w.keypad(1) # allow keypad inputs
w.timeout(10)#130 + 10*SPEED) #refresh every 130ms

#############################
# initialisation of objects #
#############################
#snake initial position
snakeXPos = sw/2
snakeYPos = sh/2

#create snake object
snake = [
    [snakeYPos,snakeXPos],
    [snakeYPos,snakeXPos-1],
    [snakeYPos,snakeXPos-2],
]

#create apple object
apple = [int(sh/3),int(sw/3)]
w.addch(apple[0],apple[1], curses.ACS_DIAMOND)

#initial direction
key = curses.KEY_RIGHT

#score
score = 0

pos = [[10,10],[10,10]]

def closer(nd,head,apple):
    nd_apple = math.sqrt((apple[0]-nd[0])**2+(apple[1]-nd[1])**2)
    head_apple = math.sqrt((head[0]-apple[0])**2+(head[1]-apple[1])**2)

    return nd_apple <= head_apple

def isNextStepATrap(head,snake):
    # is this a square trap
    squareTrap = 0
    nextToCount = 0
    for item in snake[1:]:
        if nextTo(item,head):
            nextToCount += 1
    w.addstr(11,0, "nextToCount: " + str(nextToCount))
    if (nextToCount == 2):
        squareTrap = 1

# returns area of least density 1=up,2=down,3=left,4=right
def avoidDensity(head,snake):
    ## ensure the access is available
    density = 0
    densityCounter = [[0,0],[0,0]] #t,d,l,r
    for i in range(-5,5):
        for j in range(-5,5):
            if [i+head[0],j+head[1]] in snake[1:]:
                # top
                if i < 0:
                    densityCounter[0][0] += 1
                # down
                if i > 0:
                    densityCounter[0][1] += 1
                # left
                if j < 0:
                    densityCounter[1][0] += 1
                # right
                if j > 0:
                    densityCounter[1][1] += 1
    max = 0
    for i in densityCounter:
        if i[0] > max:
            max = i[0]
        if i[1] > max:
            max = i[1]
    w.addstr(18,1, "max" + str(max))
    direc = ['t','d','l','r']
    dirIndex = 0
    for i in range(0,2):
        for j in range(0,2):
            if densityCounter[i][j] == max:
                if (i == 0 and j == 1):
                    dirIndex = 0
                if (i == 0 and j == 1):
                    dirIndex = 1
                if (i == 1 and j == 0):
                    dirIndex = 2
                if (i == 1 and j == 1):
                    dirIndex = 3
                w.addstr(20,1, "dirIndex " +str(direc[dirIndex]))

    w.addstr(15,1, str(densityCounter[0][0]))
    w.addstr(17,1, str(densityCounter[0][1]))
    w.addstr(16,0, str(densityCounter[1][0]))
    w.addstr(16,2, str(densityCounter[1][1]))

    return direc[dirIndex]

def nextTo(pos1,pos2):
    dist_x =  ((pos2[0] - pos1[0]) == 1)
    dist_y =  ((pos2[1] - pos1[1]) == 1)
    w.addstr(9,0, "dist_x: " + str(dist_x))
    w.addstr(10,0, "dist_y: " + str(dist_y))
    both = (dist_x and dist_y)
    w.addstr(12,0, "both: " + str(both))
    return (dist_x or dist_y) and ((dist_x and dist_y))


########################################
############ THE GAME LOOP #############
########################################
looper = 0
while True:
    # update movement
    new_head = [snake[0][0], snake[0][1]]

    if MODE == 0:
        # player movements
        next_key = w.getch()

        # prevent illegal movements
        if next_key == curses.KEY_DOWN and key == curses.KEY_UP:
            next_key = -1
        if next_key == curses.KEY_UP and key == curses.KEY_DOWN:
            next_key = -1
        if next_key == curses.KEY_LEFT and key == curses.KEY_RIGHT:
            next_key = -1
        if next_key == curses.KEY_RIGHT and key == curses.KEY_LEFT:
            next_key = -1

        key = key if next_key == -1 else next_key

        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1
    elif MODE == 1:
        # player movements
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        #new dir
        nd = None
        loopCounter = 0
        while nd is None:
            # head in direction of apple
            if (random.randint(0,1) == 1):
                nd = [
                    new_head[0],
                    random.randint(new_head[1]-1,new_head[1]+1)
                ]
            else:
                nd = [
                    random.randint(new_head[0]-1,new_head[0]+1),
                    new_head[1]
                ]

            # write position to screen
            w.addstr(3,0, "X NEW: " + str(nd[0]))
            w.addstr(4,0, "Y NEW: " + str(nd[1]))
            w.addstr(8,0, "ND: " + str(nd))
            w.addstr(13,0, "Density: " + str(avoidDensity(new_head,snake)))
            # if no possible then relax constraints
            if loopCounter > 1000:
                if nd in snake or snake[0][0] in [0,sh-1] or snake [0][1] in [0,sw-1] or isNextStepATrap(new_head,snake):
                    nd = None
            else:
                #if nd is closer to apple
                if nd in snake or snake[0][0] in [0,sh-1] or snake [0][1] in [0,sw-1] or not closer(nd,new_head,apple) or isNextStepATrap(new_head,snake):
                    nd = None
                if avoidDensity(new_head,snake) == 't' and new_head[0] > snake[0][0]:
                    nd = None
                    w.addstr(20,0, "avoided top")
                if avoidDensity(new_head,snake) == 'd' and new_head[0] < snake[0][0]:
                    nd = None
                    w.addstr(21,2, "avoided bottom")
                if avoidDensity(new_head,snake) == 'l' and new_head[1] > snake[0][1]:
                    nd = None
                    w.addstr(22,0, "avoided left")
                if avoidDensity(new_head,snake) == 'r' and new_head[1] < snake[0][1]:
                    nd = None
                    w.addstr(23,2, "avoided right")
            loopCounter += 1
            w.addstr(5,0, "LOOP: " + str(loopCounter))
        new_head = nd

    # how to loose
    if snake[0][0] in [0,sh-1] or snake [0][1] in [0,sw] or snake[0] in snake[1:]:
        curses.endwin()
        print('Score: ' + str(score))
        quit()

    # add head to snake
    snake.insert(0, new_head)

    if snake[0] == apple:
        # if you get the apple
        apple = None
        while apple is None:
            nf = [
                random.randint(1,sh-2),
                random.randint(1,sw-2)
            ]
            apple = nf if nf not in snake else None
        w.addch(apple[0], apple[1], curses.ACS_DIAMOND)

        #increase score
        score += 1
    else:
        # if you dont
        tail = snake.pop()
        w.addch(tail[0],tail[1],' ')

    # write score to screen
    w.addstr(0,0, "Score: " + str(score))

    # write position to screen
    w.addstr(1,0, "X: " + str(snake[0][1]))
    w.addstr(2,0, "Y: " + str(snake[0][0]))

    # write min and max position to screen
    if (snake[0][1] < pos[0][0]):
        pos[0][0] = snake[0][1]
    if (snake[0][1] > pos[0][1]):
        pos[0][1] = snake[0][1]
    if (snake[0][0] < pos[1][0]):
        pos[1][0] = snake[0][0]
    if (snake[0][0] > pos[1][1]):
        pos[1][1] = snake[0][0]

    w.addstr(1,0, "X MIN: " + str(pos[0][0]))
    w.addstr(2,0, "X MAX: " + str(pos[0][1]))

    # write snake to screen
    w.addch(snake[0][0],snake[0][1], curses.ACS_PI)
    w.addch(snake[1][0],snake[1][1], curses.ACS_BULLET)

    looper += 1

    w.addstr(6,0, "Apple X: " + str(apple[0]))
    w.addstr(7,0, "Apply Y: " + str(apple[1]))
