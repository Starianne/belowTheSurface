import sprites, config
import pygame

class Player(sprites.AnimatedSprite):
    def __init__(self, sheet, x, y):
        super().__init__(sheet, fps=12)
        self.rect.topleft = (x,y)
        self.vy = 0
        self.on_ground = True
        self.jump_strength = -10
        self.gravity = 0.6
    
    def jump(self):
        if self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False
    
    def update(self, dt):
        super().update(dt)
        self.vy += self.gravity
        self.rect.y += int(self.vy)
        if self.rect.bottom >= config.SCREEN_H:
            self.rect.bottom = config.SCREEN_H
            self.vy = 0
            self.on_ground = True

class ScrollingObject(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(topleft=(x,y))
    
    def update(self, dt):
        self.rect.x -= config.SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()