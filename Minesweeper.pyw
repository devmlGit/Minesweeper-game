import pygame
import random
import sys
import os

"""
--------------- Minesweeper game -----------------
Author: Mounir LBATH
Version: 1.0
Creation Date: 05/2021
-----------------------------------------------------------
"""

sys.setrecursionlimit(10000)

# miscellaneous
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toInt(self):
        return Vector(int(self.x),int(self.y))

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)

    def __mul__(self, other):
        return Vector(self.x*other, self.y*other)

    def __truediv__(self, other):
        return Vector(self.x/other, self.y/other)

def setCursor():
    cursor_text = (
    'X                       ',
    'XX                      ',
    'X.X                     ',
    'X..X                    ',
    'X...X                   ',
    'X....X                  ',
    'X.....X                 ',
    'X......X                ',
    'X.......X               ',
    'X........X              ',
    'X.........X             ',
    'X..........X            ',
    'X......XXXXX            ',
    'X...X..X                ',
    'X..X X..X               ',
    'X.X  X..X               ',
    'XX    X..X              ',
    '      X..X              ',
    '       XX               ',
    '                        ',
    '                        ',
    '                        ',
    '                        ',
    '                        ')
    cs, mask = pygame.cursors.compile(cursor_text)
    cursor = ((24, 24), (0, 0), cs, mask)
    pygame.mouse.set_cursor(*cursor)

# Gameobjects

class GameObject:
    def __init__(self, screen, posX,posY, width, height=-1, color=(0,0,0), shape = "rect", text=""):
        self.screen = screen 
        self.pos = Vector(posX, posY)
        self.shape = shape # can be "rect" or "circle"
        if height < 0:
            self.dim = Vector(width, width) # width =  2*radius if circle 
        else:
            self.dim = Vector(width, height)
        self.isColliding = False
        self.color = color
        self.clickedPos = Vector(0,0)
        self.text = text
        self.Draw()
    
    def Update(self):
        pass

    def Draw(self):
        if self.shape == "rect":
            self.screen.fill(self.color, ((self.pos.x,self.pos.y),(self.dim.x,self.dim.y)))
        elif self.shape == "circle":
            pygame.draw.circle( self.screen, self.color, (self.pos.x,self.pos.y),self.dim.x//2)
        if self.text != "":
            font = pygame.font.Font('freesansbold.ttf', self.dim.x*30//60)
            textSurf = font.render(self.text, True, (255,255,255))
            textRect = textSurf.get_rect()
            textRect.center = (self.pos.x + self.dim.x//2, self.pos.y + self.dim.y//2)
            self.screen.blit(textSurf, textRect)

    def IsHover(self):
        mousePos = pygame.mouse.get_pos()
        if mousePos[0] >= self.pos.x and\
            mousePos[0] <= self.pos.x + self.dim.x and\
                mousePos[1] >= self.pos.y and\
                    mousePos[1] <= self.pos.y + self.dim.y:
            return True
        
        return False

class GridElement(GameObject):
    def __init__(self, game,x,y, width, height, padding):
        self.screen = game.screen 
        self.game = game
        self.pos = Vector(x*width+padding, y*height+padding )
        self.gridPos = Vector(x,y)
        self.isMine = False # False = no mine ; True = mine
        self.dispState = 0 # 0=hidden, 1=flag, 2=out
        self.text = ""
        self.nbNeighbors = 0 #nb of neighbor mines
        self.shape = "rect"
        self.dim = Vector(width-2*padding, height-2*padding)
        self.isColliding = False
        self.color = (0,0,0)
        self.clickedPos = Vector(0,0)
        self.Draw()

    def Update(self):
        if self.dispState == 0: #hidden
            self.color = (188,188,188)#(47,40,35)
        elif self.dispState == 1: # flag
            self.color = (74,172,167)
        else: # out
            if not(self.isMine): # nothing
                self.color = (88,157,66)
            else: # mine
                self.color = (218,89,76)
        self.Draw()
    
    def Reveal(self):
        if self.isMine: # mine
            self.dispState = 2
            self.game.gameState = 3
        else: #Display
            if self.nbNeighbors != 0:
                self.text = str(self.nbNeighbors)
            self.dispState = 2
            game.nbFound += 1
            if game.nbFound == game.n*game.n - game.nbMine:
                self.game.gameState = 2
            

    def OnClick(self, mouseClick):
        if mouseClick == 3 and self.dispState != 2:
            self.dispState = (self.dispState+1)%2 #Flag
        elif mouseClick == 1: # out
            if self.nbNeighbors == 0:
                game.ZeroZone(self.gridPos.x, self.gridPos.y)
            else:
                self.Reveal()

############## MAIN #####################

class Game:
    def __init__(self, screenW, screenH, padding, n, nbMine, args):
        self.args = args
        
        # centers the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # create screen
        self.screenW = screenW
        self.screenH = screenH
        self.screen = pygame.display.set_mode((self.screenW,self.screenH))
        self.screen.fill((255,255,255))
        setCursor()
        pygame.init()
        pygame.display.set_caption('Minesweeper')

        # create Scene

        self.n = n
        self.nbMine = nbMine
        # states : 0 = no mine, 1= mine ; 0=hidden, 1=flag, 2=out
        self.padding = padding
        self.w = self.screenW//self.n
        self.h = self.screenH//self.n
        self.grid = [[GridElement(self, j, i, self.w,self.h, self.padding) for i in range(self.n)] for j in range(self.n)]
        

        self.fillGrid()

        self.nbFound = 0

        self.running = True
        self.gameState = 1 # 0 = before ; 1 = in ; 2 = win ; 3 = lost

        # calculate neighbors
        for i in range(self.n):
            for j in range(self.n):
                self.grid[i][j].nbNeighbors = self.nbNeighbors(i, j)
    
    def fillGrid(self):
        nbPlaced = 0
        while nbPlaced < self.nbMine:
            x,y = random.randint(0,self.n-1),random.randint(0,self.n-1)
            if not(self.grid[x][y].isMine):
                self.grid[x][y].isMine = True
                nbPlaced+=1  

    def nbNeighbors(self, i, j):

        counter = 0
        if j <= self.n-2:
            counter += self.grid[i][j+1].isMine
            if i <= self.n-2:
                counter += self.grid[i+1][j+1].isMine
            if i >= 1:
                counter += self.grid[i-1][j+1].isMine
        if j >= 1:
            counter += self.grid[i][j-1].isMine
            if i <= self.n-2:
                counter += self.grid[i+1][j-1].isMine
            if i >= 1:
                counter += self.grid[i-1][j-1].isMine
        if i <= self.n-2:
            counter += self.grid[i+1][j].isMine
        if i >= 1:
            counter += self.grid[i-1][j].isMine
        
        self.grid[i][j].nbNeighbors = counter
        return counter

    def RevealMine(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j].isMine == True:
                    self.grid[i][j].dispState = 2

    # reveal zone filled with zeros (recursive method)
    def ZeroZone(self, x, y):
        
        if x < self.n and y < self.n and x >= 0 and y >= 0 and self.grid[x][y].dispState == 0:  
            self.grid[x][y].Reveal()
            if self.grid[x][y].nbNeighbors == 0:
                self.ZeroZone(x+1,y)
                self.ZeroZone(x+1,y-1)
                self.ZeroZone(x+1,y)
                self.ZeroZone(x,y+1)
                self.ZeroZone(x,y-1)
                self.ZeroZone(x-1,y+1)
                self.ZeroZone(x-1,y-1)
                self.ZeroZone(x-1,y)

    def main(self):
        # run game
        while self.running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.gameState == 1:
                    if event.type == pygame.MOUSEBUTTONUP:
                        for i in range(self.n):
                            for j in range(self.n):
                                if self.grid[i][j].IsHover():
                                    self.grid[i][j].OnClick(event.button)
                elif self.gameState >= 2: # end 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            # restart
                            self.__init__(*self.args, self.args)

            self.screen.fill((255,255,255))            
            # updates
            for i in range(self.n):
                for j in range(self.n):
                    self.grid[i][j].Update()

            if self.gameState == 2 or self.gameState == 3: #if game over
                # transparent cache
                s = pygame.Surface((self.screenW,self.screenH))  # the size of your rect
                s.set_alpha(180)    # alpha level (255 is opaque)
                s.fill((0,0,0))     # this fills the entire surface
                self.screen.blit(s, (0,0))
                
                if self.gameState==2: # if won
                    text = "Congratulations, you win !"
                else:   # if gamestate==3 <=> if lost
                    text = "Game over, you lost !"
                    self.RevealMine()

                # Write text
                font = pygame.font.Font('freesansbold.ttf', 35)
                textSurf = font.render(text, True, (255,255,255))
                textRect = textSurf.get_rect()
                textRect.center = (self.screenW//2, self.screenH//2-30)
                self.screen.blit(textSurf, textRect)
                
                font = pygame.font.Font('freesansbold.ttf', 20)
                textSurf = font.render("Press enter to restart", True, (255,255,255))
                textRect = textSurf.get_rect()
                textRect.center = (self.screenW//2, self.screenH//2+ 30)
                self.screen.blit(textSurf, textRect)
            
            #update screen
            pygame.display.update()
        pygame.quit()

# Change these parameters to change the game difficulty/layout :##########
#screen width, screen height, padding between cells, grid size (n in n*n grid), total number of mines
args = (600,600,1, 10, 10)
######################################################################

game = Game(*args, args)
game.main()
