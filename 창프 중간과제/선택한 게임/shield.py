import pygame
import math
import random # 💡 랜덤한 방향과 회전 속도를 위해 추가

class Shield:
    def __init__(self, radius=75):
        self.radius = int(radius)
        self.color = (50, 150, 255) # 파란색
        self.active = False
        # 방어막의 충돌 영역 사각형 설정
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

    def update(self, player_center):
        # 방어막 중심을 플레이어 중심으로 동기화
        self.rect.center = player_center
        
        # 키 입력 감지
        keys = pygame.key.get_pressed()
        self.active = keys[pygame.K_SPACE]

    def check_collision(self, enemy_data):
        """
        [중요] 데이터 구조 변경
        enemy_data: [Rect, dx, dy, is_deflected, angle, rot_speed]
        """
        if not self.active:
            return False

        enemy_rect = enemy_data[0]
        
        # 1. 두 중심점 사이의 거리 계산
        dx = self.rect.centerx - enemy_rect.centerx
        dy = self.rect.centery - enemy_rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # 2. 충돌 판정 (방어막 반지름 + 적 절반 크기)
        if distance < self.radius + 15:
            # 적이 내려오는 중(dy > 0)이고 아직 튕겨나가지 않은 상태일 때만 실행
            if enemy_data[2] > 0 and not enemy_data[3]:
                
                # 💡 [핵심] 랜덤 방향 및 포물선 물리 초기값 세팅
                # 1. 좌우 속도(dx): -5에서 5 사이의 랜덤값 (곡선의 좌우 너비 결정)
                enemy_data[1] = random.uniform(-5, 5)
                
                # 2. 상하 속도(dy): 위로 강하게 튕겨냄 (포물선의 높이 결정)
                enemy_data[2] = random.uniform(-12, -18)
                
                # 3. 상태 변화: 이제 튕겨나가는 상태임을 표시
                enemy_data[3] = True
                
                # 4. 회전 속도: 초당 5~15도 사이로 랜덤하게 회전
                enemy_data[5] = random.uniform(5, 15) * random.choice([-1, 1])
                
                return True
        return False

    def draw(self, screen):
        if self.active:
            # 테두리 원 그리기
            pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 3)
            
            # 반투명 채우기 효과
            overlay = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*self.color, 60), (self.radius, self.radius), self.radius)
            screen.blit(overlay, (self.rect.x, self.rect.y))