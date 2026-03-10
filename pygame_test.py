import pygame
import random
import math

# --- 설정 상수 ---
WIDTH, HEIGHT = 1600, 900
FPS = 60
GRAVITY = 0.15      # 중력을 조금 더 키워 묵직하게 변경
BOUNCE = -0.6       # 바닥에 닿았을 때 튕기는 힘 (에너지 손실 포함)
FRICTION = 0.99     # 공기 저항 (매 프레임 속도 유지 비율)

class Particle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        
        # 360도 방향으로 랜덤하게 발사
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed

        self.max_life = random.randint(60, 100)
        self.life = self.max_life
        self.size = random.randint(4, 8)
        self.base_color = [random.randint(150, 255), random.randint(50, 150), 255]

    def update(self):
        # 1. 물리 연산
        self.vel.y += GRAVITY   # 중력 적용
        self.vel *= FRICTION    # 공기 저항 적용
        self.pos += self.vel    # 이동

        # 2. 바닥 튕기기 처리
        if self.pos.y + self.size > HEIGHT:
            self.pos.y = HEIGHT - self.size
            self.vel.y *= BOUNCE # 속도를 반대로 뒤집고 위로 튕김
            self.vel.x *= 0.8    # 바닥 마찰로 인해 수평 속도 감소

        # 3. 수명 감소
        self.life -= 1

    def draw(self, surf):
        # 수명에 비례해서 투명도 계산 (색상을 어둡게 만들어 투명해지는 효과 연출)
        alpha_ratio = self.life / self.max_life
        current_color = [max(0, int(c * alpha_ratio)) for c in self.base_color]
        
        if self.life > 0:
            pygame.draw.circle(surf, current_color, (int(self.pos.x), int(self.pos.y)), int(self.size * alpha_ratio))

    @property
    def is_alive(self):
        return self.life > 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ultimate Particle System")
    clock = pygame.time.Clock()

    particles = []
    time_val = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # 마우스 클릭/드래그 시 파티클 생성
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            for _ in range(5):
                particles.append(Particle(mx, my))

        # 배경 그리기 (잔상 효과를 위해 살짝 덮기 혹은 함수 호출)
        screen.fill((10, 10, 20)) 

        # 파티클 업데이트 및 그리기
        for p in particles:
            p.update()
            p.draw(screen)

        # 죽은 파티클 제거
        particles = [p for p in particles if p.is_alive]

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()