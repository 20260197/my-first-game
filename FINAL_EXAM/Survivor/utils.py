import pygame

def get_korean_font(size):
    fonts = ['malgungothic', 'applegothic', 'nanumgothic', 'dotum', 'gulim']
    for f in fonts:
        font_path = pygame.font.match_font(f)
        if font_path:
            return pygame.font.Font(font_path, size)
    return pygame.font.SysFont(None, size)