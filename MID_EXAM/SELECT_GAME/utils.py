import pygame
import sys
import random
from settings import *

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

def spawn_enemy(level_cfg):
    min_s = level_cfg.get("min_speed", 3) 
    max_s = level_cfg.get("max_speed", 7)
    
    speed = random.randint(min_s, max_s)
    
    # 해상도가 커졌으므로 적 생성 위치(WIDTH)는 settings.py의 값을 그대로 참조합니다.

    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    rect = pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)
    return [rect, 0, speed, False, 0, 0, 30, 150]

def draw_hud(screen, font, score, level_cfg, lives):
    # 왼쪽 상단 여백 소폭 조정
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 20))
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (20, 60))
    
    # Lives 표시를 오른쪽 끝에서 일정 거리 띄움
    lives_text = font.render(f"Lives: {'♥ ' * lives}", True, RED)
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))

def game_over_screen(screen, font, font_big, score):
    screen.fill(GRAY)
    
    # 텍스트 서피스 생성
    title_surf = font_big.render("GAME OVER", True, RED)
    score_surf = font.render(f"Final Score: {score}", True, WHITE)
    retry_surf = font.render("R: Restart   Q: Quit", True, WHITE)
    
    # 화면 중앙 좌표 계산
    # WIDTH, HEIGHT의 절반에서 텍스트 너비의 절반을 빼서 정확히 중앙 배치
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, HEIGHT // 2))
    screen.blit(retry_surf, (WIDTH // 2 - retry_surf.get_width() // 2, HEIGHT // 2 + 70))
    
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()