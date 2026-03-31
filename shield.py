import pygame

class Shield:
    def __init__(self, radius=75):
        self.radius = radius
        self.color = (50, 150, 255)
        self.active = False
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)

    def update(self, player_center):
        self.rect.center = player_center
        keys = pygame.key.get_pressed()
        self.active = keys[pygame.K_SPACE]

    def check_collision(self, enemy_rect):
        """방어막과 부딪혔는지 여부만 반환합니다."""
        if not self.active: return False
        
        # 거리 기반 원형 충돌 판정
        dist = pygame.math.Vector2(self.rect.center).distance_to(enemy_rect.center)
        if dist < self.radius + 15:
            return True
        return False

    def draw(self, screen):
        if self.active:
            # ... (이전과 동일한 그리기 코드)
            pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 3)