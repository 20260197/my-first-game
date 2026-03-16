import pygame
import random
import math

# --- 설정 상수 ---
WIDTH, HEIGHT = 1600, 900
FPS = 60
GRAVITY = 0.12
BOUNCE = -0.65
FRICTION = 0.992

class Particle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        
        # 1. 속도와 방향 (더 폭발적인 느낌을 위해 속도 범위 상향)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 10)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed

        # 2. 수명 및 크기
        self.max_life = random.randint(60, 120)
        self.life = self.max_life
        self.size = random.randint(4, 9)

        # 3. 색상 설정 (HSV 활용)
        # 시작 색상을 무지개색(0~360도) 중 하나로 선택
        self.hue = random.uniform(0, 360) 
        self.color = pygame.Color(0, 0, 0)
        # 색상이 변하는 속도
        self.hue_shift = random.uniform(1, 3) 

    def update(self):
        # 물리 연산
        self.vel.y += GRAVITY
        self.vel *= FRICTION
        self.pos += self.vel

        # 바닥 튕기기
        if self.pos.y + self.size > HEIGHT:
            self.pos.y = HEIGHT - self.size
            self.vel.y *= BOUNCE
            self.vel.x *= 0.9

        # 색상 변화 (시간이 흐를수록 무지개색으로 변함)
        self.hue = (self.hue + self.hue_shift) % 360
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            # 수명에 따른 투명도 및 명도 조절
            alpha_ratio = self.life / self.max_life
            
            # HSV를 RGB로 변환 (채도 100%, 명도 100%로 고정하여 아주 화사함)
            # 수명이 다할수록 명도(Value)를 낮춤
            self.color.hsva = (self.hue, 100, 100 * alpha_ratio, 100)
            
            # 크기도 서서히 줄어듦
            current_size = max(1, int(self.size * alpha_ratio))
            
            # 파티클 그리기
            pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), current_size)
            
            # 선택 사항: 더 화려하게 만들고 싶다면 주변에 작은 '빛무리' 효과를 추가 (살짝 더 연하게)
            # glow_color = pygame.Color(0,0,0)
            # glow_color.hsva = (self.hue, 80, 100 * alpha_ratio, 50)
            # pygame.draw.circle(surf, glow_color, (int(self.pos.x), int(self.pos.y)), current_size + 2, 1)

    @property
    def is_alive(self):
        return self.life > 0

def main():
    pygame.init()
    # 전체화면 혹은 큰 화면 권장
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Colorful Rainbow Fireworks")
    clock = pygame.time.Clock()

    particles = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 마우스 클릭/드래그 시 파티클 생성 (더 많이 생성하여 화려함 강조)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            for _ in range(10): 
                particles.append(Particle(mx, my))

        # 배경색: 완전 검은색보다 약간 깊은 남색이 색을 더 돋보이게 합니다.
        screen.fill((5, 5, 15)) 

        # 파티클 업데이트 및 그리기
        for p in particles:
            p.update()
            p.draw(screen)

        # 죽은 파티클 제거
        particles = [p for p in particles if p.is_alive]

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()