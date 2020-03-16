import pygame

def changeSpriteColor(image, color):
    w, h = image.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = image.get_at((x, y))[3]
            image.set_at((x, y), pygame.Color(r, g, b, a))

def checkCollision(rect, otherRect):
    return rect.colliderect(otherRect)