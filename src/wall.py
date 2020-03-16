import pygame
from random import randint

from piece import Piece
from object import Object
from wallPart import WallPart


class Wall(Object):
    PART_LENGTH = 75

    def __init__(self, side, piecesName, core):
        self.core = core
        self.side = side

        self.wallParts = []
        self.initWallPart(piecesName)

    def initWallPart(self, piecesName):
        partHeight = self.core.WINDOW_HEIGHT / len(piecesName)
        for index, piece in enumerate(piecesName):
            partPos = (0 if self.side == "LEFT" else self.core.WINDOW_LENGTH - self.PART_LENGTH,
                       partHeight * index)
            partSize = (self.PART_LENGTH, partHeight)
            pieceRect = pygame.Rect(partPos, partSize)
            self.wallParts.append(WallPart(piece, pieceRect, self.core))

    def checkIfComplete(self):
        for part in self.wallParts:
            if part.isSet == False:
                return False
        return True

    def update(self, dt):
        for part in self.wallParts:
            part.update(dt)

