# 2026-03-31 (5주차 실습 정리)
## 오늘 한 것
- 탬플릿 게임 4종 플레이
- 탬플릿 게임을 플레이 해보고 중간과제 기획서를 작성하기

## AI 활용 기록
# Qustion
 이 dodger 게임 코드에 대해서 파이썬을 처음 접하는 사람이 이해하기 쉽게 설명해줄래? 

    import pygame
    import random
    import sys

    pygame.init()


    def get_korean_font(size):
        candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
        for name in candidates:
            font = pygame.font.SysFont(name, size)
            if font.get_ascent() > 0:
                return font
        return pygame.font.SysFont(None, size)


    WIDTH, HEIGHT = 800, 600
    FPS = 60

    WHITE  = (255, 255, 255)
    BLACK  = (0,   0,   0)
    BLUE   = (50,  120, 220)
    RED    = (220, 50,  50)
    YELLOW = (240, 200, 0)
    GRAY   = (40,  40,  40)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dodger")
    clock = pygame.time.Clock()
    font = get_korean_font(36)
    font_big = get_korean_font(72)

    # --- 레벨 설정 ---
    LEVELS = [
        {"min_speed": 3, "max_speed": 5,  "spawn": 40, "label": "Lv.1"},
        {"min_speed": 5, "max_speed": 8,  "spawn": 25, "label": "Lv.2"},
        {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
    ]

    # --- 사운드 자리 ---
    # dodge_sound = pygame.mixer.Sound("dodge.wav")
    # hit_sound   = pygame.mixer.Sound("hit.wav")

    PLAYER_W, PLAYER_H = 50, 30
    ENEMY_W,  ENEMY_H  = 30, 30

    def spawn_enemy(level_cfg):
        x = random.randint(0, WIDTH - ENEMY_W)
        speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
        return pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H), speed

    def draw_hud(score, level_cfg, lives):
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))
        screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))

    def game_over_screen(score):
        screen.fill(GRAY)
        screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
        screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
        pygame.display.flip()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r: return True
                    if e.key == pygame.K_q: pygame.quit(); sys.exit()

    def main():
        player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)
        enemies = []
        score = 0
        lives = 3
        spawn_timer = 0
        level_idx = 0
        level_cfg = LEVELS[level_idx]
        invincible = 0

        while True:
            clock.tick(FPS)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]  and player.left  > 0:     player.x -= 5
            if keys[pygame.K_RIGHT] and player.right < WIDTH:  player.x += 5
            if keys[pygame.K_UP]    and player.top   > 0:     player.y -= 5
            if keys[pygame.K_DOWN]  and player.bottom < HEIGHT: player.y += 5

            spawn_timer += 1
            if spawn_timer >= level_cfg["spawn"]:
                spawn_timer = 0
                rect, speed = spawn_enemy(level_cfg)
                enemies.append([rect, speed])

            survived = []
            for pair in enemies:
                pair[0].y += pair[1]
                if pair[0].top < HEIGHT:
                    survived.append(pair)
                else:
                    score += 1
            enemies = survived

            if invincible > 0:
                invincible -= 1
            else:
                for pair in enemies:
                    if player.colliderect(pair[0]):
                        # hit_sound.play()
                        lives -= 1
                        invincible = 90
                        enemies.clear()
                        if lives <= 0:
                            if game_over_screen(score):
                                main()
                            return
                        break

            level_idx = min(score // 20, len(LEVELS) - 1)
            level_cfg = LEVELS[level_idx]

            screen.fill(GRAY)

            blink = (invincible // 10) % 2 == 0
            if blink:
                pygame.draw.rect(screen, BLUE, player)

            for pair in enemies:
                pygame.draw.rect(screen, RED, pair[0])

            draw_hud(score, level_cfg, lives)
            pygame.display.flip()

    main()

# Answer
## 1. 게임의 무대 준비 (설정 및 초기화)
가장 윗부분은 게임을 실행하기 위한 기본적인 세팅을 하는 곳입니다.

- pygame.init(): "자, 이제 게임 도구함을 열게!"라고 파이썬에게 알리는 명령어입니다.
- 변수 (WIDTH, HEIGHT, FPS): 게임 화면의 가로/세로 크기(800x600)와 1초에 화면을 몇 번이나 새로고침할지(60번) 정합니다.
- 색상 정의: 컴퓨터는 빨강, 초록, 파랑(RGB)의 조합으로 색을 만듭니다. (255, 0, 0)은 순수한 빨간색이죠.
- LEVELS: 점수가 올라감에 따라 적이 더 빨리 내려오거나 더 자주 나타나도록 설정값이 들어있는 리스트입니다.

## 2. 게임의 기본 법칙 (좌표계)
컴퓨터 게임에서 위치를 이해하는 것이 가장 중요합니다.

- pygame.Rect: "안보이는 상자"라고 생각하세요. 모든 캐릭터와 총알은 이 상자 안에 들어있습니다. 이 상자의 x, y 좌표를 바꿔서 캐릭터를 움직입니다.
- 좌표: 화면 왼쪽 위가 (0, 0)입니다. 오른쪽으로 갈수록 x가 커지고, 아래로 갈수록 y가 커집니다. 그래서 총알이 위로 올라가려면 y값을 빼줘야 합니다.

## 3. 그림 그리기 도구 (함수)
코드 중간중간에 def로 시작하는 부분들은 특정 기능을 수행하는 "미니 로봇"들입니다.

- draw_player / draw_enemy: 삼각형 모양으로 비행기를 그려주는 로봇입니다.
- spawn_enemy: 화면 위쪽(y = -ENEMY_H)의 랜덤한 위치에 적을 생성합니다.
- draw_hud: 현재 점수와 남은 목숨(♥)을 화면에 글자로 찍어줍니다.

## 4. 게임의 엔진: 메인 루프 (Main Loop)
while True: 부분은 게임이 끝날 때까지 1초에 60번씩 무한 반복되는 게임의 심장입니다.

매 프레임(반복)마다 엔진은 다음 과정을 거칩니다:

> 1. 입력 감지 (Input): 플레이어가 화살표 키를 눌렀는지, 스페이스바를 눌렀는지 확인합니다.
> 2. 위치 업데이트 (Update):
>> - 화살표 키에 맞춰 플레이어 위치 이동.
>> - 총알은 위로(y -= 10), 적은 아래로(y += speed) 이동.
> 3. 충돌 판정 (Collision):
>> - colliderect: "두 상자가 겹쳤니?"라고 물어보는 마법의 명령어입니다.
>> - 총알과 적이 겹치면 점수를 올리고 둘 다 삭제합니다.
>> - 플레이어와 적이 겹치면 목숨을 깎습니다.
> 4. 화면 그리기 (Draw): 배경을 칠하고, 별을 그리고, 비행기를 그린 뒤 pygame.display.flip()으로 유저에게 보여줍니다.

## 5. 특별한 장치들
- 무적 시간 (invincible): 적과 부딪혔을 때 바로 연속으로 죽지 않도록 잠시 깜빡이며 무적 상태가 되는 기능입니다.
- 별 그리기 (stars): 배경이 심심하지 않게 작은 흰색 원들을 그려 우주 공간 느낌을 냈습니다.
- 재시작 (game_over_screen): 목숨이 다하면 점수를 보여주고, R키를 눌러 다시 시작할지 물어봅니다.

## 💡 처음 공부할 때 팁
이 코드에서 숫자들을 조금씩 바꿔보세요! * player.x -= 6을 - 20으로 바꾸면 비행기가 엄청 빨라집니다.

- score // 50을 score // 10으로 바꾸면 레벨업이 훨씬 빨라집니다.

직접 숫자를 바꿔보며 화면이 어떻게 변하는지 보는 것이 파이썬과 가장 빨리 친해지는 방법입니다! 더 궁금한 부분이 있으면 물어봐 주세요. :)