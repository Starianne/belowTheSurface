import pygame

class SpriteSheet:
    def __init__(self, image, frames):
        self.image = image
        self.frames = frames
        w, h = image.get_size()
        self.frame_w = w // frames
        self.frame_h = h
        self.frames_list = []
        for i in range(frames):
            rect = pygame.Rect(i*self.frame_w, 0, self.frame_w, self.frame_h)
            frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
            frame.blit(image, (0,0), rect)
            self.frames_list.append(frame)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, spritesheet: SpriteSheet, fps=10):
        super().__init__()
        self.sheet = spritesheet
        self.fps = fps
        self.index = 0
        self.image = self.sheet.frames_list[0]
        self.rect = self.image.get_rect()
        self.timer = 0
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= 1000 / self.fps:
            self.timer = 0
            self.index = (self.index + 1) % len(self.sheet.frames_list)
            self.image = self.sheet.frames_list[self.index]