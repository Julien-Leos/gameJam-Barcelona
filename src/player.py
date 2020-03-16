import pygame
import operator
import utils

from object import Object
from piece import Piece
from wall import Wall

class Player(Object):
    SPEED = 300
    SPEED_HOLDING_PERCENT = 0.85
    DASH_DURATION = 0.3
    DASH_SPEED_BONUS = 500
    DASH_COOLDOWN = 2

    STUNT_DURATION = 1.5
    STUNT_FADE_INTENSITY = 150

    ANIM_URL_PREFIX = "assets/player/character-"
    ANIM_URL_SUFFIX = ".png"
    ANIM_SPEED = 0.05

    def __init__(self, name, pos, keys, color, core):
        self.name = name
        self.originalDashFire = pygame.image.load("assets/particles/blue-fire.png").convert_alpha()
        self.dashFire = self.originalDashFire
        self.keys = keys

        self.color = color
        self.core = core

        self.velocity = [0, 0]
        self.hold = None
        self.stunt = 0
        self.dash = 0
        self.anim = 0
        self.animElapsed = 0

        self.initSprite(pos)

    def initSprite(self, pos):
        self.image = pygame.image.load(
            self.ANIM_URL_PREFIX + str(self.anim) + self.ANIM_URL_SUFFIX).convert_alpha()
        utils.changeSpriteColor(self.image, self.color)
        self.rect = self.image.get_rect()
        self.rect.move_ip(*pos)

    def checkPlayerAction(self):
        players = self.core.getObjectsByType(Player)
        for player in players:
            if player != self:
                if utils.checkCollision(self.rect, player.rect):
                    if player.hold:
                        player.hold = None
                    if player.stunt == 0:
                        player.stunt = self.STUNT_DURATION
                    return True
        return False

    def checkBlockAction(self):
        blocks = self.core.getObjectsByType(Piece)
        for block in blocks:
            if utils.checkCollision(self.rect, block.rect):
                self.hold = block
                return True
        return False

    def checkWallCollision(self, rectToCheck):
        walls = self.core.getObjectsByType(Wall)
        for wall in walls:
            for part in wall.wallParts:
                if utils.checkCollision(rectToCheck, part.rectPart):
                    return part
        return None

    def checkWallPartAction(self):
        partCollided = self.checkWallCollision(self.rect)
        if partCollided != None and self.hold:
            return partCollided.checkPutPiece(self.hold.name)
        return None

    def checkAction(self):
        wallPartCollided = self.checkWallPartAction()
        if self.hold and wallPartCollided != None:
            if wallPartCollided == True:
                self.core.objects.remove(self.hold)
                self.hold = None
            return

        if self.hold:
            self.hold = None
            return

        willDash = True
        if self.checkBlockAction():
            willDash = False
        if self.checkPlayerAction():
            willDash = False
        if willDash and not self.hold:
            self.dash = self.DASH_SPEED_BONUS
            

    def setStuntColor(self):
        fade = self.stunt * (self.STUNT_FADE_INTENSITY / self.STUNT_DURATION)
        newColor = (
            0 if self.color[0] == 0 else int(fade),
            0 if self.color[1] == 0 else int(fade),
            0 if self.color[2] == 0 else int(fade))
        utils.changeSpriteColor(self.image, tuple(
            map(operator.sub, self.color, newColor)))

    def checkIfMove(self, move):
        if ((not self.checkWallCollision(self.rect)) or (self.checkWallCollision(self.rect) and not self.checkWallCollision(self.rect.move(*move))) or (self.rect.x == self.rect.x + move[0])) \
            and (self.rect.move(*move).top >= 0 and self.rect.move(*move).bottom <= self.core.WINDOW_HEIGHT):
            return True
        return False

    def updateAnim(self, dt):
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.animElapsed -= dt
            if self.animElapsed <= 0:
                self.anim = (self.anim + 1) % 2
                self.animElapsed = self.ANIM_SPEED
        else:
            self.anim = 0
            self.animElapsed = self.ANIM_SPEED

        url = self.ANIM_URL_PREFIX + ("hold-" if self.hold else "") + str(self.anim) + self.ANIM_URL_SUFFIX
        self.image = pygame.image.load(url).convert_alpha()

    def update(self, dt):
        self.updateAnim(dt)

        if self.stunt == 0:
            speed = self.SPEED * self.SPEED_HOLDING_PERCENT if self.hold else self.SPEED
            speed += self.dash if self.dash > 0 else 0
            move = [v * speed * dt for v in self.velocity]

            if self.checkIfMove(move):
                self.rect.move_ip(*move)
            if self.dash > 0:
                self.dash -= self.DASH_SPEED_BONUS * (dt / self.DASH_DURATION)
            if self.dash < 0:
                self.dash = 0
            utils.changeSpriteColor(self.image, self.color)
        else:
            self.stunt -= self.stunt if dt > self.stunt else dt
            self.setStuntColor()

        if self.hold:
            self.hold.rect.x = self.rect.copy().x
            self.hold.rect.y = self.rect.copy().y
            self.hold.rect.x += 28
            self.hold.rect.y -= 25

        self.checkDash()
        self.core.window.blit(self.image, self.rect)

    def checkDash(self):
        if self.dash != 0 and (self.velocity[0] > 0):
            self.dashFire = pygame.transform.rotate(self.originalDashFire, 0)
            self.core.window.blit(self.dashFire, [self.rect.x - 130, self.rect.y - 5])
        if self.dash != 0 and (self.velocity[0] < 0):
            self.dashFire = pygame.transform.rotate(self.originalDashFire, 180)
            self.core.window.blit(self.dashFire, [self.rect.x + 22, self.rect.y - 16])
        if self.dash != 0 and (self.velocity[1] < 0):
            self.dashFire = pygame.transform.rotate(self.originalDashFire, 90)
            self.core.window.blit(self.dashFire, [self.rect.x + 10, self.rect.y + 10])
        if self.dash != 0 and (self.velocity[1] > 0):
            self.dashFire = pygame.transform.rotate(self.originalDashFire, 270)
            self.core.window.blit(self.dashFire, [self.rect.x, self.rect.y - 130])

    def eventManager(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.keys["left"]:
                self.velocity[0] += -1
            if event.key == self.keys["right"]:
                self.velocity[0] += 1
            if event.key == self.keys["up"]:
                self.velocity[1] += -1
            if event.key == self.keys["down"]:
                self.velocity[1] += 1
            if event.key == self.keys["action"] and self.stunt == 0:
                self.checkAction()
        if event.type == pygame.KEYUP:
            if event.key == self.keys["left"]:
                self.velocity[0] -= -1
            if event.key == self.keys["right"]:
                self.velocity[0] -= 1
            if event.key == self.keys["up"]:
                self.velocity[1] -= -1
            if event.key == self.keys["down"]:
                self.velocity[1] -= 1
