# rolling-around-a-cube.py
# Maulik Doshi + Section F + maulikd

# 15-112 Term Project Fall 2014
# Rolling Around a Cube

from __future__ import with_statement
from visual import *
import pygame   # Used purely for the music functionality
import math, random, os

pygame.mixer.init()
intromusic = pygame.mixer.music.load("music/bgmusic.ogg")
# Tacky Background Music
# http://www.freesfx.co.uk/sfx/background%20music

# Plays the music that is loaded
def playMusic():
    pygame.mixer.music.play(-1)

# Stops the music that is loaded
def stopMusic():
    pygame.mixer.music.stop()

# Pauses the music that is playing
def pauseMusic():
    pygame.mixer.music.pause()

# Unpauses the music that was paused
def unpauseMusic():
    pygame.mixer.music.unpause()

# Returns the text instructions for the game
def getInstructions():
    instructions = '''Welcome to Rolling Around a Cube!

- Press the backspace key to go back to the previous menu
- During gameplay, press 'r' to restart with a new arrangement
- Press 'p' to pause, 'u' to unpause
- Click points to create paths
- Press the down key to run
- Guide the ball so it travels around the cube
- Less tries and time is better score
- Lower the score the better

Thank You for Playing!'''
    return instructions

# Reads a file (Taken from Course Notes)
def readFile(filename, mode="rt"):
    # rt = "read text"
    with open(filename, mode) as fin:
        return fin.read()

# Writes to a file (Taken from Course Notes)
def writeFile(filename, contents, mode="wt"):
    # wt = "write text"
    with open(filename, mode) as fout:
        fout.write(contents)

# Almost Equals adapted from Course Notes
def almostEqual(d1, d2):
    epsilon = 10
    return (abs(d2 - d1) < epsilon)

# Class for the actual gameplay of the project
class Gameplay(object):

    # Constructor for the Gameplay class
    def __init__(self, scene, level=1, side=600):
        if(level == 1):
            self.bgcolor = (102/255.0,0/255.0,102/255.0)
        elif(level == 2):
            self.bgcolor = (0/255.0,51/255.0,102/255.0)
        elif(level == 3):
            self.bgcolor = (102/255.0,102/255.0,0/255.0)
        elif(level == 4):
            self.bgcolor = (102/255.0,51/255.0,0/255.0)
        elif(level == 5):
            self.bgcolor = (102/255.0,0/255.0,0/255.0)
        self.scene = scene
        self.scene.background = self.bgcolor
        self.level = level
        self.numOfObstacles = self.level * 4
        self.scene.userzoom = False
        self.scene.userspin = False
        self.side = side
        self.initAnimation()

    # Initialize other variables needed in the class
    def initAnimation(self):
        self.gameRange = 500
        self.solving = False
        self.solved = False
        self.paused = False
        self.time = 0
        self.tries = 0
        self.rotateRange = 600
        self.scene.range = self.gameRange
        self.frames = [frame(), frame(), frame(), frame()]
        self.currentFrame = 0
        self.collide = False
        self.curvePts = [[],[],[],[]]
        self.start = []
        self.end = []
        self.curves = [[],[],[],[]]
        self.firstPoint = [[],[],[],[]]
        self.endPoint = [[],[],[],[]]
        self.clickedPts = [[],[],[],[]]
        self.quit = False
        self.oob = True
        (self.x, self.y, self.z, self.r) = (-267, 267, 320, 15)
        self.addPoints = [[],[],[],[]]
        self.obstacles = []
        self.numOfFrames = 4
        self.ballFrame = 0
        self.ballMove = False
        for x in xrange(4): self.initializePoints(x)
        self.timer = label(pos=(0,0,320), height=20, text=str(self.tries) + "-" + "0.00", align='center', depth=0.01, color=color.white, frame=self.currentFrame)
        self.tempCol = label(pos=(0,0,320), height=20, text="COLLISION", align='center', depth=0.01, color=color.red, background=color.black, frame=self.currentFrame)
        self.tempCol.visible = False
        self.tempOOB = label(pos=(0,0,320), height=20, text="OUT OF BOUNDS", align='center', depth=0.01, color=color.red, background=color.black, frame=self.currentFrame)
        self.tempOOB.visible = False
        self.drawObjects()

    # Draw the beginning and ending squares
    def drawBeginEnds(self):
        self.start.append(Rectangle(0, 0, 50, 50, color.red, 0, self.frames))
        self.start.append(Rectangle(0, 550, 50, 600, color.red, 1, self.frames))
        self.start.append(Rectangle(0, 0, 50, 50, color.red, 2, self.frames))
        self.start.append(Rectangle(0, 550, 50, 600, color.red, 3, self.frames))
        self.end.append(Rectangle(550, 550, 600, 600, color.green, 0, self.frames))
        self.end.append(Rectangle(550, 0, 600, 50, color.green, 1, self.frames))
        self.end.append(Rectangle(550, 550, 600, 600, color.green, 2, self.frames))
        self.end.append(Rectangle(550, 0, 600, 50, color.green, 3, self.frames))

    # Generates a random rgb color for the obstacles
    def randomColor(self):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        return (r/255.0, g/255.0, b/255.0)

    # Draws the rectangle obstacles on screen with random color and position
    def drawObstacles(self):
        num = 0
        f = 0
        self.obsColors = []
        while(num < self.numOfObstacles):
            x0 = random.randint(50,540)
            y0 = random.randint(50,540)
            s = random.randint(1,8)
            di = random.choice(["up", "right"])
            while(True):
                x1 = random.randint(60,550)
                if(abs(x0-x1) < 10): continue
                if(x0 < x1): break
            while(True):
                y1 = random.randint(60,550)
                if(abs(y0-y1) < 10): continue
                if(y0 < y1): break
            self.obsColors.append(self.randomColor())
            self.obstacles.append(Rectangle(x0, y0, x1, y1, self.obsColors[num], f, self.frames, di, s))
            f = ((f + 1) % 4)   # 4 frames (0, 1, 2, 3)
            num += 1
        self.unhighlight()

    # Draws the beginning and ending black points to start and end paths
    def drawFirstEndPoints(self):
        self.firstPoint[0] = points(frame=self.frames[0], pos=(self.x, self.y, self.z), size=50, color=color.black)
        self.firstPoint[1] = points(frame=self.frames[1], pos=(self.z, -self.y, -self.x), size=50, color=color.black)
        self.firstPoint[2] = points(frame=self.frames[2], pos=(-self.x, self.y, -self.z), size=50, color=color.black)
        self.firstPoint[3] = points(frame=self.frames[3], pos=(-self.z, -self.y, self.x), size=50, color=color.black)

        self.endPoint[0] = points(frame=self.frames[0], pos=(-self.x, -self.y, self.z), size=50, color=color.black)
        self.endPoint[1] = points(frame=self.frames[1], pos=(self.z, self.y, self.x), size=50, color=color.black)
        self.endPoint[2] = points(frame=self.frames[2], pos=(self.x, -self.y, -self.z), size=50, color=color.black)
        self.endPoint[3] = points(frame=self.frames[3], pos=(-self.z, self.y, -self.x), size=50, color=color.black)

    # Draws the curves to move between faces of the cube
    def drawCurvePts(self):
        self.addPoints[0] = [(-self.x, -self.y, self.z), (-self.x+50, -self.y, self.z), (self.z, -self.y, -self.x)]
        self.addPoints[1] = [(self.z, self.y, self.x), (self.z, self.y, self.x-50), (-self.x, self.y, -self.z)]
        self.addPoints[2] = [(self.x, -self.y, -self.z), (self.x-50, -self.y, -self.z), (-self.z, -self.y, self.x)]
        self.addPoints[3] = [(-self.z, self.y, -self.x), (-self.z, self.y, -self.x+50), (self.x, self.y, self.z)]
        for x in xrange(4):
            curve(pos=self.addPoints[x], frame=self.frames[x], color=color.blue)

    # Darkens all objects that are not in the current frame
    def unhighlight(self):
        for x in xrange(len(self.obstacles)):
            if(self.obstacles[x].getFrame() != self.currentFrame):
                self.obstacles[x].changeColor((0,0,0))
            else:
                self.obstacles[x].changeColor(self.obsColors[x])
        for y in xrange(4):
            if(self.start[y].getFrame() != self.currentFrame):
                self.start[y].changeColor((0,0,0))
            else:
                self.start[y].changeColor((1,0,0))
            if(self.end[y].getFrame() != self.currentFrame):
                self.end[y].changeColor((0,0,0))
            else:
                self.end[y].changeColor((0,1,0))

    # Deletes all objects on screen
    def deleteAllObjects(self):
        # To delete, visibility must be False and then use del command
        for x in xrange(4):
            self.frames[0].visible = False
            del self.frames[0]
        self.box.visible = False
        del self.box
        self.timer.visible = False
        del self.timer

    # Initializes the first point at the starting location
    def initializePoints(self, frame):
        if(frame == 0):
            self.curvePts[0] = [(self.x, self.y, self.z)]
        elif(frame == 1):
            self.curvePts[1] = [(self.z, -self.y, -self.x)]
        elif(frame == 2):
            self.curvePts[2] = [(-self.x, self.y, -self.z)]
        elif(frame == 3):
            self.curvePts[3] = [(-self.z, -self.y, self.x)]

    # Draws all the objects needed for Gameplay on screen in position
    def drawObjects(self):
        self.box = box(pos=(0,0,0), axis=(1,0,0), length=self.side, height=self.side, width=self.side, color=color.white, opacity=0.1)
        self.drawBeginEnds()
        self.drawObstacles()
        self.drawFirstEndPoints()
        self.drawCurvePts()
        self.ball = sphere(pos=(self.x,self.y,self.z), radius=self.r, color=color.yellow, frame=self.frames[self.ballFrame])

    # Handles the rotation between different faces of the cube
    def rotation(self, direction):
        for x in xrange(self.gameRange, self.rotateRange+1, 10):
            sleep(0.001)
            self.scene.range = x
        (start, end) = (1, 21)
        if (direction == "right"):
            self.currentFrame = ((self.currentFrame+1)%4)
            coeff = -1
        else:
            self.currentFrame = ((self.currentFrame-1)%4)
            coeff = 1
        self.unhighlight()
        for x in xrange(start, end):
            sleep(0.001)
            self.box.rotate(angle=coeff*(1*math.pi/((end-start)*2)), axis=(0,1,0), origin=(0,0,0))
            for y in xrange(self.numOfFrames):
                self.frames[y].rotate(angle=coeff*(1*math.pi/((end-start)*2)), axis=(0,1,0), origin=(0,0,0))
        for x in xrange(self.rotateRange, self.gameRange-1, -10):
            sleep(0.001)
            self.scene.range = x

    # Rotates up specifically for end of game
    def rotateUp(self):
        (start, end) = (1,21)
        for x in xrange(start, end):
            sleep(0.001)
            self.box.rotate(angle=(1*math.pi/((end-start)*2)), axis=(1,0,0), origin=(0,0,0))
            for y in xrange(self.numOfFrames):
                self.frames[y].rotate(angle=(1*math.pi/((end-start)*2)), axis=(1,0,0), origin=(0,0,0))
        for x in xrange(self.gameRange, 100, -5):
            sleep(0.01)
            self.scene.range = x

    # Detects when player (ball) has gone outside the box
    def outOfBounds(self):
        gap = 25
        if(self.oob == True):
            if(self.currentFrame == 0 or self.currentFrame == 2):
                if(self.ball.pos.x < self.x-gap or self.ball.pos.x > -self.x+gap
                   or self.ball.pos.y < -self.y-gap or self.ball.pos.y > self.y+gap):
                    return True
                else: return False
            elif(self.currentFrame == 1 or self.currentFrame == 3):
                if(self.ball.pos.z < self.x-gap or self.ball.pos.z > -self.x+gap
                   or self.ball.pos.y < -self.y-gap or self.ball.pos.y > self.y+gap):
                    return True
                else: return False
        else: return False

    # Short animation for when collision is detected
    def collisionDisplay(self):
        self.timer.visible = False
        for x in xrange(3):
            self.tempCol.visible = False
            sleep(0.3)
            self.tempCol.visible = True
            sleep(0.3)
        sleep(0.5)
        self.tempCol.visible = False
        self.timer.visible = True

    # Short animation for when out-of-bounds is detected
    def oobDisplay(self):
        self.timer.visible = False
        for x in xrange(3):
            self.tempOOB.visible = False
            sleep(0.3)
            self.tempOOB.visible = True
            sleep(0.3)
        sleep(0.5)
        self.tempOOB.visible = False
        self.timer.visible = True

    # Moves along the path that the user draws and keeps moving between frames
    def moveAlongPath(self):
        if(self.curvePts[self.currentFrame] == []):
            self.ballMove = False
            self.rotation("right")  # Rotate after finishing face
            self.ballFrame += 1
            if(len(self.curvePts[self.currentFrame]) > 1):
                self.ballMove = True
                self.downPressed()
        else:
            if(len(self.curvePts[self.currentFrame]) == 1):
                self.curvePts[self.currentFrame].pop()
            else:
                if(len(self.curvePts[self.currentFrame]) > 3):
                    collision = self.obsCollide()
                    oob = self.outOfBounds()
                    if(collision == True or oob == True):
                        self.collide = True
                        if(collision):
                            self.collisionDisplay()
                        if(oob):
                            self.oobDisplay()
                        self.ballMove = False
                        self.postCollisionTasks()
                        return
                x0, x1 = self.curvePts[self.currentFrame][0][0], self.curvePts[self.currentFrame][1][0]
                y0, y1 = self.curvePts[self.currentFrame][0][1], self.curvePts[self.currentFrame][1][1]
                z0, z1 = self.curvePts[self.currentFrame][0][2], self.curvePts[self.currentFrame][1][2]
                if(almostEqual(self.ball.pos.x,x1) and almostEqual(self.ball.pos.y,y1) and almostEqual(self.ball.pos.z,z1)):
                    self.ball.pos = (x1,y1,z1)  # Almost equal used for small errors
                    self.curvePts[self.currentFrame].pop(0)
                else:   # Calculates slope and travles the distance
                    d = ((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)**0.5
                    d /= 8.0
                    xStep = (x1 - x0)/d
                    yStep = (y1 - y0)/d
                    zStep = (z1 - z0)/d
                    self.ball.pos += (xStep,yStep,zStep)

    # Reset the ball on current frame after a collision or out-of-bounds
    def postCollisionTasks(self):
        self.initializePoints(self.currentFrame)
        for curve in self.curves[self.currentFrame]:
            curve.visible = False
            del curve
        for point in self.clickedPts[self.currentFrame]:
            point.visible = False
            del point
        self.ball.pos = self.curvePts[self.currentFrame][0]

    # Check that the ball is in the end square to win that face
    def checkWin(self):
        gap = 25
        point = self.ball.pos
        if(self.currentFrame == 0):
            if(point[0] > self.end[self.currentFrame].getPos().x - gap and point[1] < self.end[self.currentFrame].getPos().y + gap):
                return True
            return False
        elif(self.currentFrame == 1):
            if(point[1] > self.end[self.currentFrame].getPos().y - gap and point[2] < self.end[self.currentFrame].getPos().z + gap):
                return True
            return False
        elif(self.currentFrame == 2):
            if(point[0] < self.end[self.currentFrame].getPos().x + gap and point[1] < self.end[self.currentFrame].getPos().y + gap):
                return True
            return False
        elif(self.currentFrame == 3):
            if(point[1] > self.end[self.currentFrame].getPos().y - gap and point[2] > self.end[self.currentFrame].getPos().z - gap):
                return True
            return False

    # Returns True if ball collides with obstacle, False otherwise
    def obsCollide(self):
        (x,y,z) = (self.ball.pos.x, self.ball.pos.y, self.ball.pos.z)
        for obs in self.obstacles:
            if(obs.collision(x,y,z) == True and obs.getFrame() == self.currentFrame):
                return True
        return False

    # Moves obstacles every iteration of the game by a specific amount direction
    def moveObstacle(self):
        for obs in self.obstacles:
            obs.move()

    # Last point needs to be within the end square, ideally on that black point
    def lastPoint(self):
        gap = 25
        point = self.curvePts[self.currentFrame][-1]
        if(self.currentFrame == 0):
            if(point[0] > self.end[self.currentFrame].getPos().x - gap and point[1] < self.end[self.currentFrame].getPos().y + gap):
                return True
            return False
        elif(self.currentFrame == 1):
            if(point[1] > self.end[self.currentFrame].getPos().y - gap and point[2] < self.end[self.currentFrame].getPos().z + gap):
                return True
            return False
        elif(self.currentFrame == 2):
            if(point[0] < self.end[self.currentFrame].getPos().x + gap and point[1] < self.end[self.currentFrame].getPos().y + gap):
                return True
            return False
        elif(self.currentFrame == 3):
            if(point[1] > self.end[self.currentFrame].getPos().y - gap and point[2] > self.end[self.currentFrame].getPos().z - gap):
                return True
            return False

    # Add the points needed to move between faces once ball rolls
    def downPressed(self):
        if(self.ballFrame != 4 and self.ballFrame == self.currentFrame and self.lastPoint() == True):
            self.ballMove = True
            for elem in self.addPoints[self.currentFrame]:
                self.curvePts[self.currentFrame].append(elem)

    # Steps needed for the solve function
    def solveSteps(self, x, y, step):
        self.ball.pos.x = x
        self.ball.pos.y = y
        if(self.outOfBounds() == False and self.obsCollide() == False): result = True
        else: result = False
        if(step == 0): self.ball.pos.x -= 8
        elif(step == 1): self.ball.pos.y += 8
        elif(step == 2): self.ball.pos.x += 8
        elif(step == 3): self.ball.pos.y -= 8
        return result

    # Automatically solves the first face of the cube, no points anymore
    def solve(self):
        while(self.checkWin() == False):
            rate(50)
            self.moveObstacle()
            if(self.solveSteps(self.ball.pos.x + 8, self.ball.pos.y, 0) == True):
                self.ball.pos.x += 8
                self.curvePts[self.currentFrame].append((self.ball.pos.x, self.ball.pos.y, self.ball.pos.z))
                self.curves[0].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            elif(self.solveSteps(self.ball.pos.x - 8, self.ball.pos.y, 2) == True):
                self.ball.pos.x -= 8
                self.curvePts[self.currentFrame].append((self.ball.pos.x, self.ball.pos.y, self.ball.pos.z))
                self.curves[0].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            if(self.solveSteps(self.ball.pos.x, self.ball.pos.y - 8, 1) == True):
                self.ball.pos.y -= 8
                self.curvePts[self.currentFrame].append((self.ball.pos.x, self.ball.pos.y, self.ball.pos.z))
                self.curves[0].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            elif(self.solveSteps(self.ball.pos.x, self.ball.pos.y + 8, 3) == True):
                self.ball.pos.y += 8
                self.curvePts[self.currentFrame].append((self.ball.pos.x, self.ball.pos.y, self.ball.pos.z))
                self.curves[0].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
        self.curvePts[self.currentFrame] = [self.curvePts[self.currentFrame][-1]]
        for elem in self.addPoints[self.currentFrame]:
            self.curvePts[self.currentFrame].append(elem)
        self.ballMove = True
        self.solving = False

    # Hides all objects on screen
    def hideAll(self):
        for x in xrange(4):
            self.frames[x].visible = False
        self.box.visible = False
        self.timer.visible = False

    # Shows all objects back on the screen
    def showAll(self):
        for x in xrange(4):
            self.frames[x].visible = True
        self.box.visible = True
        self.timer.visible = True

    # Handles key presses during the game
    def onKeyPressed(self):
        k = self.scene.kb.getkey()
        if (self.paused == False):
            if (k == "r"):
                self.deleteAllObjects()
                self.initAnimation()
            elif (k == "p"):
                pauseMusic()
                self.paused = True
                self.hideAll()
                instructions = getInstructions()
                self.pauseTitle = label(pos=(0,400,0), text='Help Screen', height=35, color=color.white, background=color.black, opacity=1)
                self.pauseBox = box(pos=(0,330,0), length=395.5, height=59, width=0)
                self.pauseText = label(pos=(0,326.2,0), text='(Paused)', height=15, color=color.white, background=color.black)
                self.pauseHelp = label(pos=(0,0,0), text=instructions, height=16, color=color.black, background=color.white, opacity=1, align="center")
            elif (k == "s"):
                if(self.currentFrame == 0):
                    self.solved = True
                    self.timer.text = "None"
                    self.solving = True
            elif (k == "backspace"):
                self.quit = True
            elif (k == "right"):
                self.rotation("right")
            elif (k == "left"):
                self.rotation("left")
            elif (k == "down"):
                    if(self.ballFrame == self.currentFrame and self.lastPoint() == True):
                        if(self.solved == False):
                            self.tries += 1
                            self.timer.text = str(self.tries) + "-" + str(self.score)
                        else: self.timer.text = "None"
                    self.downPressed()
        else:
            if (k == "u"):
                self.pauseTitle.visible = False
                self.pauseBox.visible = False
                self.pauseText.visible = False
                self.pauseHelp.visible = False
                del self.pauseTitle
                del self.pauseBox
                del self.pauseText
                del self.pauseHelp
                self.paused = False
                unpauseMusic()
                self.showAll()

    # Handles all mouse presses and mouse clicks in the game
    def onMousePressed(self):
        m = self.scene.mouse.getclick()
        newMouse = self.scene.mouse.project(normal=(0,0,1),d=self.z)
        if(self.currentFrame == 0):
            self.curvePts[self.currentFrame].append((newMouse.x, newMouse.y, newMouse.z))
            self.curves[0].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            self.clickedPts[0].append(points(frame=self.frames[self.currentFrame], pos=(newMouse.x, newMouse.y, newMouse.z), size=50, color=color.cyan))
        elif(self.currentFrame == 1):
            self.curvePts[self.currentFrame].append((newMouse.z, newMouse.y, -newMouse.x))
            self.curves[1].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            self.clickedPts[1].append(points(frame=self.frames[self.currentFrame], pos=(newMouse.z, newMouse.y, -newMouse.x), size=50, color=color.cyan))
        elif(self.currentFrame == 2):
            self.curvePts[self.currentFrame].append((-newMouse.x, newMouse.y, -newMouse.z))
            self.curves[2].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            self.clickedPts[2].append(points(frame=self.frames[self.currentFrame], pos=(-newMouse.x, newMouse.y, -newMouse.z), size=50, color=color.cyan))
        elif(self.currentFrame == 3):
            self.curvePts[self.currentFrame].append((-newMouse.z, newMouse.y, newMouse.x))
            self.curves[3].append(curve(pos=self.curvePts[self.currentFrame], frame=self.frames[self.currentFrame], color=color.white))
            self.clickedPts[3].append(points(frame=self.frames[self.currentFrame], pos=(-newMouse.z, newMouse.y, newMouse.x), size=50, color=color.cyan))

    # Updates scores at the end of the game by using file IO
    def updateScores(self):
        if(self.level == 1):
            path = "scores/stage1bs.txt"
        elif(self.level == 2):
            path = "scores/stage2bs.txt"
        elif(self.level == 3):
            path = "scores/stage3bs.txt"
        elif(self.level == 4):
            path = "scores/stage4bs.txt"
        elif(self.level == 5):
            path = "scores/stage5bs.txt"
        if (not os.path.exists(path)):
            writeFile(path, str(self.score))
        else:
            s = readFile(path)
            if(self.score < float(s)):
                if (os.path.exists(path)):
                    os.remove(path)
                writeFile(path, str(self.score))

    # Runs the game of this class
    def run(self):
        while(True):
            rate(50)
            if(self.quit == False):
                if(self.scene.kb.keys == True): self.onKeyPressed()
                if(self.paused == False):
                    self.moveObstacle()
                    if(self.solving == True): self.solve()
                    if(self.ballMove == True): self.moveAlongPath()
                    if(self.ballFrame != 4):
                        if(self.solved == False):
                            self.time += 0.025
                            self.score = round(self.time, 1)
                            self.timer.text = str(self.tries) + "-" + str(self.score)
                        else:
                            self.timer.text = "None"
                    else:
                        if(self.solved == False):
                            self.score *= self.tries
                            sleep(1)
                            self.timer.text = "Score: " + str(self.score)
                            self.updateScores()
                        else:
                            sleep(1)
                            self.timer.text = "Score: None"
                        self.rotateUp()
                        self.go = label(pos=(0,0,0), height=30, text="GAME OVER", align='center', depth=0.01, color=color.white, frame=self.currentFrame, font="monospace")
                        sleep(1)
                        self.go.visible = False
                        del self.go
                        self.quit = True
                    if(self.scene.mouse.events == 1): self.onMousePressed()
                    else: self.scene.mouse.events = 0   # Used to fix bugs dealing with too many mouse presses
            else:
                self.deleteAllObjects()
                levels = PlayLevels(self.scene)
                levels.run()

# Class creating Rectangles as obstacles for the game
class Rectangle(object):

    # Constructor that does math to allow users to easily create on faces
    def __init__(self, x1, y1, x2, y2, color, frameNumber, framesList, direction="up", speed=0):
        if(direction == "up"):
            self.moveUp = True
        elif(direction == "right"):
            self.moveUp = False
        if(direction == "rotate"):
            self.rotate = True
        else:
            self.rotate = False
        self.current = frameNumber
        self.frames = framesList
        self.speed = speed
        self.width = 0
        self.moveOneWay = True
        self.positions(x1,y1,x2,y2)
        self.rect = box(pos=(self.x, self.y, self.z), axis=self.axis, length=self.length, height=self.height,
                        width=self.width, color=color, frame=self.frames[self.current])

    # Calculates the positions of the obstacles in relation to the face
    def positions(self, x1, y1, x2, y2):
        self.length = x2-x1
        self.height = y2-y1
        self.x = (((x1-300) + self.length/2.0))
        self.y = (((300-y1) - self.height/2.0))
        self.z = 301
        if (self.current == 0):
            (self.x, self.y, self.z) = (self.x, self.y, self.z)
            self.axis = (1,0,0)
        elif (self.current == 1):
            (self.x, self.y, self.z) = (self.z, self.y, -self.x)
            self.axis = (0,0,1)
        elif (self.current == 2):
            (self.x, self.y, self.z) = (-self.x, self.y, -self.z)
            self.axis = (1,0,0)
        elif (self.current == 3):
            (self.x, self.y, self.z) = (-self.z, self.y, self.x)
            self.axis = (0,0,1)

    # Moves the obstacles in the specified direction
    def move(self):
        if(self.moveOneWay == True):
            if(self.moveUp == True):
                self.rect.pos += (0,self.speed,0)
                if (self.rect.pos.y+self.height/2.0 > 300):
                    self.moveOneWay = False
            else:
                if(self.current == 0):
                    self.rect.pos += (self.speed,0,0)
                    if (self.rect.pos.x+self.length/2.0 > 300):
                        self.moveOneWay = False
                elif(self.current == 1):
                    self.rect.pos -= (0,0,self.speed)
                    if (self.rect.pos.z-self.length/2.0 < -300):
                        self.moveOneWay = False
                elif(self.current == 2):
                    self.rect.pos -= (self.speed,0,0)
                    if (self.rect.pos.x-self.length/2.0 < -300):
                        self.moveOneWay = False
                elif(self.current == 3):
                    self.rect.pos += (0,0,self.speed)
                    if (self.rect.pos.z+self.length/2.0 > 300):
                        self.moveOneWay = False
        else:
            if(self.moveUp == True):
                self.rect.pos -= (0,self.speed,0)
                if (self.rect.pos.y-self.height/2.0 < -300):
                    self.moveOneWay = True
            else:
                if(self.current == 0):
                    self.rect.pos -= (self.speed,0,0)
                    if (self.rect.pos.x-self.length/2.0 < -300):
                        self.moveOneWay = True
                elif(self.current == 1):
                    self.rect.pos += (0,0,self.speed)
                    if (self.rect.pos.z+self.length/2.0 > 300):
                        self.moveOneWay = True
                elif(self.current == 2):
                    self.rect.pos += (self.speed,0,0)
                    if (self.rect.pos.x+self.length/2.0 > 300):
                        self.moveOneWay = True
                elif(self.current == 3):
                    self.rect.pos -= (0,0,self.speed)
                    if (self.rect.pos.z-self.length/2.0 < -300):
                        self.moveOneWay = True

    # Collision algorithm used to detect between ball and rectangles
    def collision(self, x, y, z):
        frame = self.current
        if(frame == 0 or frame == 2):
            if((x > (self.rect.pos.x - self.rect.length/2.0)) and (x < (self.rect.pos.x + self.rect.length/2.0)) and
                (y > (self.rect.pos.y - self.rect.height/2.0)) and (y < (self.rect.pos.y + self.rect.height/2.0))):
                return True
            else: return False
        elif(frame == 1 or frame == 3):
            if((z > (self.rect.pos.z - self.rect.length/2.0)) and (z < (self.rect.pos.z + self.rect.length/2.0)) and
                (y > (self.rect.pos.y - self.rect.height/2.0)) and (y < (self.rect.pos.y + self.rect.height/2.0))):
                return True
            else: return False

    # Getter function for the position of the obstacle
    def getPos(self):
        return self.rect.pos

    # Getter function for the frame of the obstacles
    def getFrame(self):
        return self.current

    # Setter function to change color of obstacle
    def changeColor(self, c):
        self.rect.color = c

# Class for the initial Menu display
class Menu(object):

    # Constructor for the class
    def __init__(self, scene):
        self.scene = scene
        self.scene.background = color.black
        self.scene.range = 12
        self.scene.userspin = False
        self.scene.userzoom = False
        self.frame = frame()
        self.drawAll()

    # Draws all the objects needed on the screen
    def drawAll(self):
        x = 20.59
        self.title = label(pos=(0,9,0),text='Rolling Around a Cube', height=44, color=color.white, frame=self.frame, background=color.blue, opacity=1)
        self.subbox = box(pos=(0,7.13,0), length=x, height=1.5, width=0, frame=self.frame)
        self.subtitle = label(pos=(0,7,0),text='By: Maulik Doshi', height=15, color=color.white, frame=self.frame)
        self.play = box(pos=(0,3.5,0), length=x, height=3.3, color=color.green, width=0, frame=self.frame)
        self.playTitle = label(pos=(0,3.5,0), text='PLAY', height=20, frame=self.frame, box=False, font="monospace")
        self.ins = box(pos=(0,-0.6,0), length=x, height=3.3, color=color.yellow, width=0, frame=self.frame)
        self.insTitle = label(pos=(0,-0.6,0), text='INSTRUCTIONS', height=20, frame=self.frame, box=False, font="monospace")
        self.set = box(pos=(0,-4.7,0), length=x, height=3.3, color=color.red, width=0, frame=self.frame)
        self.setTitle = label(pos=(0,-4.7,0), text='SETTINGS', height=20, frame=self.frame, box=False, font="monospace")
        self.best = box(pos=(0,-8.8,0), length=x, height=3.3, color=color.orange, width=0, frame=self.frame)
        self.bestTitle = label(pos=(0,-8.8,0), text='BEST SCORES', height=20, frame=self.frame, box=False, font="monospace")

    # Handles the event when the play button is pressed
    def onPlayPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.play.pos.x, self.play.pos.y)
        (l, h) = (self.play.length, self.play.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the event when the instructions button is pressed
    def onInsPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.ins.pos.x, self.ins.pos.y)
        (l, h) = (self.ins.length, self.ins.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the event when the settings button is pressed
    def onSetPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.set.pos.x, self.set.pos.y)
        (l, h) = (self.set.length, self.set.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the event when the best scores button is pressed
    def onBestPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.best.pos.x, self.best.pos.y)
        (l, h) = (self.best.length, self.best.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Highlights the play button when mouse over
    def highlightPlay(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.play.pos.x, self.play.pos.y)
        (l, h) = (self.play.length, self.play.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.play.color = color.white
        else: self.play.color = color.green

    # Highlights the instructions button when mouse over
    def highlightIns(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.ins.pos.x, self.ins.pos.y)
        (l, h) = (self.ins.length, self.ins.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.ins.color = color.white
        else: self.ins.color = color.yellow

    # Highlights the settings button when mouse over
    def highlightSet(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.set.pos.x, self.set.pos.y)
        (l, h) = (self.set.length, self.set.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.set.color = color.white
        else: self.set.color = color.red

    # Highlights the best scores button when mouse over
    def highlightBest(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.best.pos.x, self.best.pos.y)
        (l, h) = (self.best.length, self.best.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.best.color = color.white
        else: self.best.color = color.orange

    # Highlights all of the buttons when needed
    def highlightAll(self):
        self.highlightPlay()
        self.highlightIns()
        self.highlightSet()
        self.highlightBest()

    # Runs the menu display
    def run(self):
        while True:
            rate(50)
            self.highlightAll()
            if(self.scene.mouse.events == 1):
                m = self.scene.mouse.getclick()
                if(self.onPlayPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    levels = PlayLevels(self.scene)
                    levels.run()
                elif(self.onInsPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    ins = Instructions(self.scene)
                    ins.run()
                elif(self.onSetPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    sett = Settings(self.scene)
                    sett.run()
                elif(self.onBestPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    best = BestScores(self.scene)
                    best.run()
            else: self.scene.mouse.events = 0

# Class for the best scores display
class BestScores(object):

    # Constructor for the class
    def __init__(self, scene):
        self.scene = scene
        self.scene.background = color.orange
        self.scene.range = 12
        self.scene.userspin = False
        self.scene.userzoom = False
        self.frame = frame()
        self.drawAll()

    # Handles the event to go back to the menu using backspace
    def onBackPressed(self, event):
        if(event == "backspace"):
            return True
        return False

    # Find scores from files to display, None if there aren't any yet
    def findScores(self):
        self.scores = 5*["None"]
        path = "scores/stage1bs.txt"
        if (not os.path.exists(path)):
            self.scores[0] = "None"
        else:
            self.scores[0] = readFile(path)
        path = "scores/stage2bs.txt"
        if (not os.path.exists(path)):
            self.scores[1] = "None"
        else:
            self.scores[1] = readFile(path)
        path = "scores/stage3bs.txt"
        if (not os.path.exists(path)):
            self.scores[2] = "None"
        else:
            self.scores[2] = readFile(path)
        path = "scores/stage4bs.txt"
        if (not os.path.exists(path)):
            self.scores[3] = "None"
        else:
            self.scores[3] = readFile(path)
        path = "scores/stage5bs.txt"
        if (not os.path.exists(path)):
            self.scores[4] = "None"
        else:
            self.scores[4] = readFile(path)

    # Draws all the objects needed on the screen
    def drawAll(self):
        self.findScores()
        self.title = label(pos=(0,9,0),text='Best Scores', height=35, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.s1 = label(pos=(0,5.8,0),text='Stage 1', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.bs1 = label(pos=(0,4.4,0),text=str(self.scores[0]), height=15, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.s2 = label(pos=(0,2.3,0),text='Stage 2', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.bs2 = label(pos=(0,0.9,0),text=str(self.scores[1]), height=15, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.s3 = label(pos=(0,-1.2,0),text='Stage 3', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.bs3 = label(pos=(0,-2.6,0),text=str(self.scores[2]), height=15, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.s4 = label(pos=(0,-4.7,0),text='Stage 4', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.bs4 = label(pos=(0,-6.1,0),text=str(self.scores[3]), height=15, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.s5 = label(pos=(0,-8.2,0),text='Stage 5', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.bs5 = label(pos=(0,-9.6,0),text=str(self.scores[4]), height=15, color=color.white, frame=self.frame, background=color.black, opacity=1)

    # Runs the best scores menu
    def run(self):
        while(True):
            rate(50)
            if(self.scene.kb.keys == 1):
                k = self.scene.kb.getkey()
                if(self.onBackPressed(k) == True):
                    self.frame.visible = False
                    del self.frame
                    menu = Menu(self.scene)
                    menu.run()

# Class for the levels screen
class PlayLevels(object):

    # Constructor for the class
    def __init__(self, scene):
        self.scene = scene
        self.scene.background = color.green
        self.scene.range = 12
        self.scene.userspin = False
        self.scene.userzoom = False
        self.frame = frame()
        self.drawAll()

    # Draws all the objects needed on the screen
    def drawAll(self):
        x = 20.59
        self.title = label(pos=(0,8.8,0), text='Stages', height=35, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.lv1box = box(pos=(0,5.1,0), length=x, height=2.7, width=0, frame=self.frame, color=color.black)
        self.lv1 = label(pos=(0,5.1,0), text='Stage 1: Easy', height=15, color=color.white, frame=self.frame, background=(102/255.0,0/255.0,102/255.0), opacity=1)
        self.lv2box = box(pos=(0,1.7,0), length=x, height=2.7, width=0, frame=self.frame, color=color.black)
        self.lv2 = label(pos=(0,1.7,0), text='Stage 2: Medium', height=15, color=color.white, frame=self.frame, background=(0/255.0,51/255.0,102/255.0), opacity=1)
        self.lv3box = box(pos=(0,-1.7,0), length=x, height=2.7, width=0, frame=self.frame, color=color.black)
        self.lv3 = label(pos=(0,-1.7,0), text='Stage 3: Hard', height=15, color=color.white, frame=self.frame, background=(102/255.0,102/255.0,0/255.0), opacity=1)
        self.lv4box = box(pos=(0,-5.1,0), length=x, height=2.7, width=0, frame=self.frame, color=color.black)
        self.lv4 = label(pos=(0,-5.1,0), text='Stage 4: Extreme', height=15, color=color.white, frame=self.frame, background=(102/255.0,51/255.0,0/255.0), opacity=1)
        self.lv5box = box(pos=(0,-8.5,0), length=x, height=2.7, width=0, frame=self.frame, color=color.black)
        self.lv5 = label(pos=(0,-8.5,0), text='Stage 5: Intense', height=15, color=color.white, frame=self.frame, background=(102/255.0,0/255.0,0/255.0), opacity=1)

    # Handles the backspace key to go back to a previous menu
    def onBackPressed(self):
        k = self.scene.kb.getkey()
        if(k == "backspace"):
            return True
        return False

    # Highlights the first stage button
    def highlightS1(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv1box.pos.x, self.lv1box.pos.y)
        (l, h) = (self.lv1box.length, self.lv1box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.lv1box.color = color.white
        else: self.lv1box.color = color.black

    # Highlights the second stage button
    def highlightS2(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv2box.pos.x, self.lv2box.pos.y)
        (l, h) = (self.lv2box.length, self.lv2box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.lv2box.color = color.white
        else: self.lv2box.color = color.black

    # Highlights the third stage button
    def highlightS3(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv3box.pos.x, self.lv3box.pos.y)
        (l, h) = (self.lv3box.length, self.lv3box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.lv3box.color = color.white
        else: self.lv3box.color = color.black

    # Highlights the fourth stage button
    def highlightS4(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv4box.pos.x, self.lv4box.pos.y)
        (l, h) = (self.lv4box.length, self.lv4box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.lv4box.color = color.white
        else: self.lv4box.color = color.black

    # Highlights the fifth stage button
    def highlightS5(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv5box.pos.x, self.lv5box.pos.y)
        (l, h) = (self.lv5box.length, self.lv5box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.lv5box.color = color.white
        else: self.lv5box.color = color.black

    # Handles the button press of the first stage
    def onS1Pressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv1box.pos.x, self.lv1box.pos.y)
        (l, h) = (self.lv1box.length, self.lv1box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the button press of the second stage
    def onS2Pressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv2box.pos.x, self.lv2box.pos.y)
        (l, h) = (self.lv2box.length, self.lv2box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the button press of the third stage
    def onS3Pressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv3box.pos.x, self.lv3box.pos.y)
        (l, h) = (self.lv3box.length, self.lv3box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the button press of the fourth stage
    def onS4Pressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv4box.pos.x, self.lv4box.pos.y)
        (l, h) = (self.lv4box.length, self.lv4box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the button press of the fifth stage
    def onS5Pressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.lv5box.pos.x, self.lv5box.pos.y)
        (l, h) = (self.lv5box.length, self.lv5box.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Highlights all based on mouse position
    def highlightAll(self):
        self.highlightS1()
        self.highlightS2()
        self.highlightS3()
        self.highlightS4()
        self.highlightS5()

    # Runs the display for the levels screen
    def run(self):
        while(True):
            rate(50)
            self.highlightAll()
            if(self.scene.kb.keys == True):
                if(self.onBackPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    menu = Menu(self.scene)
                    menu.run()
            if(self.scene.mouse.events == 1):
                m = self.scene.mouse.getclick()
                if(self.onS1Pressed() == True):
                    self.frame.visible = False
                    del self.frame
                    game = Gameplay(self.scene, 1)
                    game.run()
                elif(self.onS2Pressed() == True):
                    self.frame.visible = False
                    del self.frame
                    game = Gameplay(self.scene, 2)
                    game.run()
                elif(self.onS3Pressed() == True):
                    self.frame.visible = False
                    del self.frame
                    game = Gameplay(self.scene, 3)
                    game.run()
                elif(self.onS4Pressed() == True):
                    self.frame.visible = False
                    del self.frame
                    game = Gameplay(self.scene, 4)
                    game.run()
                elif(self.onS5Pressed() == True):
                    self.frame.visible = False
                    del self.frame
                    game = Gameplay(self.scene, 5)
                    game.run()
            else: self.scene.mouse.events = 0

# Class for the instructions screen
class Instructions(object):

    # Constructor for the class
    def __init__(self, scene):
        self.scene = scene
        self.scene.background = color.yellow
        self.scene.range = 12
        self.scene.userspin = False
        self.scene.userzoom = False
        self.frame = frame()
        self.drawAll()

    # Draws the objects needed for the instructions
    def drawAll(self):
        words = getInstructions()
        self.title = label(pos=(0,9,0), text='Instructions', height=35, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.ins = label(pos=(0,0,0), text=words, height=16, color=color.black, frame=self.frame, background=color.white, opacity=1, align="center")

    # Handles the backspace key to go back to the previous menu
    def onBackPressed(self):
        k = self.scene.kb.getkey()
        if(k == "backspace"):
            return True
        return False

    # Runs the different stages display
    def run(self):
        while(True):
            rate(50)
            if(self.scene.kb.keys == True):
                if(self.onBackPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    menu = Menu(self.scene)
                    menu.run()

# The class for settings menu
class Settings(object):

    # Constructor for the class
    def __init__(self, scene):
        self.scene = scene
        self.scene.background = color.red
        self.scene.range = 12
        self.scene.userspin = False
        self.scene.userzoom = False
        self.frame = frame()
        self.drawAll()

    # Draws the objects needed for the class
    def drawAll(self):
        self.title = label(pos=(0,9,0),text='Settings', height=35, color=color.white, frame=self.frame, background=color.black, opacity=1)
        self.heading = label(pos=(0,6.1,0),text='Music', height=20, color=color.white, frame=self.frame, background=color.black, opacity=0.3)
        self.onBox = box(pos=(0,1.1,0), length=10, height=6.7, width=0, frame=self.frame, color=color.black)
        self.onLabel = label(pos=(0,1.1,0), text="ON", frame=self.frame, height=17, background=color.black, font="monospace")
        self.offBox = box(pos=(0,-6.55,0), length=10, height=6.7, width=0, frame=self.frame, color=color.black)
        self.offLabel = label(pos=(0,-6.55,0), text="OFF", frame=self.frame, height=17, background=color.black, font="monospace")

    # Handles the backspace key to go back to a the previous menu
    def onBackPressed(self):
        k = self.scene.kb.getkey()
        if(k == "backspace"):
            return True
        return False

    # Highlights the music on button
    def highlightOn(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.onBox.pos.x, self.onBox.pos.y)
        (l, h) = (self.onBox.length, self.onBox.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.onBox.color = color.white
        else: self.onBox.color = color.black

    # Highlights the music off button
    def highlightOff(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.offBox.pos.x, self.offBox.pos.y)
        (l, h) = (self.offBox.length, self.offBox.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            self.offBox.color = color.white
        else: self.offBox.color = color.black

    # Handles the on-button mouse press
    def onPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.onBox.pos.x, self.onBox.pos.y)
        (l, h) = (self.onBox.length, self.onBox.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Handles the off-button mouse press
    def offPressed(self):
        (x, y) = (self.scene.mouse.pos.x, self.scene.mouse.pos.y)
        (xBox, yBox) = (self.offBox.pos.x, self.offBox.pos.y)
        (l, h) = (self.offBox.length, self.offBox.height)
        if(x > (xBox - l/2.0) and x < (xBox + l/2.0) and y > (yBox - h/2.0) and y < (yBox + h/2.0)):
            return True
        return False

    # Runs the settings display
    def run(self):
        while(True):
            rate(50)
            self.highlightOn()
            self.highlightOff()
            if(self.scene.kb.keys == True):
                if(self.onBackPressed() == True):
                    self.frame.visible = False
                    del self.frame
                    menu = Menu(self.scene)
                    menu.run()
            if(self.scene.mouse.events == 1):
                m = self.scene.mouse.getclick()
                if(self.onPressed() == True):
                    playMusic()
                elif(self.offPressed() == True):
                    stopMusic()
            else: self.scene.mouse.events = 0

# Runs the game starting with the display and menu --> class-driven from there
def runGame():
    scene = display(title="Rolling Around a Cube", width=600, height=620, autoscale=False)
    playMusic()
    menu = Menu(scene)
    menu.run()

runGame()
