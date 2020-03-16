import os
import random
import time
import pygame
import sys

from object import Object
from player import Player
from piece import Piece
from wall import Wall


class Core:
    FPS = 60
    WINDOW_LENGTH = 1080
    WINDOW_HEIGHT = 720

    PLAYER1_NAME = "Blue"
    PLAYER1_START_POS = (WINDOW_LENGTH / 2 - 100, WINDOW_HEIGHT / 2)
    PLAYER1_COLOR = (0, 0, 255)
    PLAYER1_KEYS = {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "action": pygame.K_SPACE
    }

    PLAYER2_NAME = "Red"
    PLAYER2_START_POS = (WINDOW_LENGTH / 2 + 100, WINDOW_HEIGHT / 2)
    PLAYER2_COLOR = (255, 0, 0)
    PLAYER2_KEYS = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "action": pygame.K_RETURN
    }

    NUMBER_WALL_HOLE = 6
    NUMBER_PIECES = 40

    PIECE_SPAWN_RANGE_X_PERCENT = 0.1
    PIECE_SPAWN_RANGE_Y_PERCENT = 0.45

    NETWORK_GAME = False

    def __init__(self):
        random.seed(time.time())
        random.seed(123)
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 200)
        self.window = pygame.display.set_mode(
            (self.WINDOW_LENGTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.piecesName = []
        self.objects = []

        self.objects.append(Player(self.PLAYER1_NAME, self.PLAYER1_START_POS,
                                   self.PLAYER1_KEYS, self.PLAYER1_COLOR, self))
        self.objects.append(Player(self.PLAYER2_NAME, self.PLAYER2_START_POS,
                                   self.PLAYER2_KEYS, self.PLAYER2_COLOR, self))
        
        self.piecesName = []
        self.generatePieces()
        
        self.objects.append(Wall("LEFT", self.piecesName, self))
        self.objects.append(Wall("RIGHT", self.piecesName, self))


    def networkManager(self, datagram):
        if (datagram[0] == '1' or datagram[0] == '2'):
            self.getObjectsByType(Player)[1].networkManager(datagram)
        if (datagram[0] == '0'):
            sys.exit()

    def generateRandomPiecePosition(self):
        x = random.randint(self.WINDOW_LENGTH / 2 - (self.WINDOW_LENGTH * self.PIECE_SPAWN_RANGE_X_PERCENT),
                           self.WINDOW_LENGTH / 2 + (self.WINDOW_LENGTH * self.PIECE_SPAWN_RANGE_X_PERCENT))
        y = random.randint(self.WINDOW_HEIGHT / 2 - (self.WINDOW_HEIGHT * self.PIECE_SPAWN_RANGE_Y_PERCENT),
                           self.WINDOW_HEIGHT / 2 + (self.WINDOW_HEIGHT * self.PIECE_SPAWN_RANGE_Y_PERCENT))
        return (x, y)

    def generatePieces(self):
        for filename in os.listdir(os.getcwd() + "/assets/pieces"):
            self.piecesName.append(filename.split('.png')[0])

        for i in range(self.NUMBER_WALL_HOLE):
            name = self.piecesName[i]
            self.objects.append(
                Piece(name, self.generateRandomPiecePosition(), self))
            self.objects.append(
                Piece(name, self.generateRandomPiecePosition(), self))

    def checkWinCondition(self):
        walls = self.getObjectsByType(Wall)
        for wall in walls:
            if wall.checkIfComplete() == True:
                if wall.side == "LEFT":
                    text = "BLUE WIN !!!"
                    color = self.PLAYER1_COLOR
                else:
                    text = "RED WIN !!!"
                    color = self.PLAYER2_COLOR
                textsurface = self.font.render(text, False, color)
                self.window.blit(textsurface, (self.WINDOW_LENGTH / 2 - 400, self.WINDOW_HEIGHT / 2 - 50))

    def eventManager(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for object_ in self.objects:
                object_.eventManager(event)

    def update(self, dt):
        for object_ in self.objects:
            object_.update(dt)
        self.checkWinCondition()

    def getObjectsByType(self, type_):
        response = []

        for object_ in self.objects:
            if type(object_) == type_:
                response.append(object_)
        return response

    def gameloop(self):
        sound = pygame.mixer.Sound("assets/sound/flute.wav")
        sound.play(loops=-1, maxtime=0, fade_ms=0)
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000
            self.window.fill((0, 0, 0))

            self.eventManager()
            self.update(dt)

            pygame.display.flip()