import pygame
import random
import math

# --- 상수는 대문자로 관리하여 가독성 향상 ---
WIDTH, HEIGHT = 900, 600
FPS = 60
GRAVITY = 0.08
PARTICLE_COUNT = 8  # 한 번 클릭 시 생성되는 파티클 수

class Particle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        
        # 벡터를 사용하여 속도와 방향을 한 번에 설정
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 6)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed

        self.life = random.randint(40, 80)
        self.size = random.randint(3, 7)
        self.color = [random.randint(100, 255) for _ in range(3)]

    def update(self):
        self.pos += self.vel    # 위치 이동
        self.vel.y += GRAVITY   # 중력 가속도
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), self.size)

    @property
    def is_alive(self):
        return self.life > 0

def draw_background(surface, t):
    # 성능을 위해 2픽셀 단위로 그리기 (선택 사항)
    for y in range(0, HEIGHT, 2):
        c = int(40 + 30 * math.sin(y * 0.01 + t))
        color = (10, c, 50 + c // 2)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fancy Particle Playground")
    clock = pygame.time.Clock()

    particles = []
    time_val = 0
    running = True

    while running:
        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. 로직 처리 (마우스 입력 및 파티클 생성)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            particles.extend([Particle(mx, my) for _ in range(PARTICLE_COUNT)])

        # 3. 그리기 및 업데이트
        time_val += 0.03
        draw_background(screen, time_val)

        for p in particles:
            p.update()
            p.draw(screen)

        # 수명이 다한 파티클 제거 (필터링)
        particles = [p for p in particles if p.is_alive]

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()