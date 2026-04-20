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

def show_title_screen(screen, font, font_big):
    # 💡 [해결] 함수 시작 시 변수를 초기화해야 에러가 나지 않습니다.
    show_help = False
    
    title_text = font_big.render("SPACE DISASTER", True, (255, 255, 255))
    start_text = font.render("Press SPACE to Start", True, (200, 200, 200))
    help_hint = font.render("[H]: How to Play", True, (150, 150, 150))
    
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(50)]

    while True:
        screen.fill((0, 0, 0))
        
        # 배경 별 움직임
        for star in stars:
            star[1] += 1
            if star[1] > HEIGHT: star[1] = 0
            pygame.draw.circle(screen, (100, 100, 100), star, 1)

        # 메인 타이틀 표시
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))
        screen.blit(help_hint, (WIDTH//2 - help_hint.get_width()//2, HEIGHT//3 + 80))
        
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 50))

        # 💡 H를 눌렀을 때 보여줄 도움말 오버레이 (타이틀용)
        if show_help:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 220), (50, 50, WIDTH-100, HEIGHT-100))
            screen.blit(overlay, (0, 0))
            
            help_lines = [
                "HOW TO PLAY",
                "",
                "이동: 1,2 페이즈 : 방향키 또는 AD",
                "이동: 3,4,5 페이즈 : 방향키 또는WASD",
                "쉴드: 유성을 튕겨냄 (자동)",
                "보너스: 레이저 근처에서 버티기!",
                "",
                "[H] 키를 눌러 닫기"
            ]
            for i, line in enumerate(help_lines):
                color = (255, 255, 0) if i == 0 else (255, 255, 255)
                msg = font.render(line, True, color)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 120 + i * 45))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # 💡 [해결] 스페이스를 누르면 return을 통해 게임 루프로 진입
                if event.key == pygame.K_SPACE:
                    return 
                # 💡 [해결] H 키 토글 시 에러 방지
                if event.key == pygame.K_h:
                    show_help = not show_help