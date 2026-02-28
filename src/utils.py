import pygame

def load_image(path, fallback_size=(32,32,)):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((200, 50, 200, 255))
        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
        return surf

def darken_surface(surf, factor=0.5):
    s = surf.copy()
    arr = pygame.surfarray.pixels3d(s)
    arr[:] = (arr * factor).astype('uint8')
    del arr
    return s

def invert_colours(surf):
    s = surf.copy()
    arr = pygame.surfarray.pixels3d(s)
    arr[:] = 255 - arr
    del arr
    return s