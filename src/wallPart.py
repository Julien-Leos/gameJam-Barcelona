import pygame
from object import Object
import utils

class WallPart(Object):
    COLLIDE_OFFSET = 40

    def __init__(self, name, rect, core):
        self.name = name
        self.core = core
        self.isSet = False

        self.initSprite(rect)

    def initSprite(self, rect):
        self.imagePart = pygame.Surface((rect.w, rect.h))
        self.imagePart.fill((255, 255, 255))
        self.rectPart = self.imagePart.get_rect()
        self.rectPart.move_ip(rect.x, rect.y)
        
        self.imagePiece = pygame.image.load("assets/pieces/" + self.name + ".png").convert_alpha()
        utils.changeSpriteColor(self.imagePiece, (0, 0, 0))
        self.rectPiece = self.imagePiece.get_rect()
        partXOffset = (rect.w - self.rectPiece.w) / 2
        partYOffset = (rect.h - self.rectPiece.h) / 2
        self.rectPiece.move_ip(*(rect.x + partXOffset, rect.y + partYOffset))

    def checkPutPiece(self, pieceName):
        if pieceName == self.name:
            utils.changeSpriteColor(self.imagePiece, (255, 255, 255))
            self.isSet = True
            return True
        return False

    def update(self, dt):
        self.core.window.blit(self.imagePart, self.rectPart)
        self.core.window.blit(self.imagePiece, self.rectPiece)