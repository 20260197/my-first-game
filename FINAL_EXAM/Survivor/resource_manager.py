import pygame
import os
import sys

# 메모리 캐싱을 위한 딕셔너리 (한 번 로드한 리소스는 여기서 꺼내 씀)
_images = {}
_sounds = {}
_fonts = {}

def get_resource_path(relative_path):
    """
    일반 실행과 PyInstaller EXE 실행을 모두 지원하는 상대 경로 추출 함수입니다.
    EXE로 압축했을 때 풀리는 임시 폴더 경로(sys._MEIPASS)를 우선적으로 찾습니다.
    """
    try:
        # PyInstaller에 의해 생성된 임시 폴더 경로
        base_path = sys._MEIPASS
    except Exception:
        # 일반 파이썬 실행 시의 현재 작업 디렉토리 경로
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_image(path, alpha=True):
    """
    이미지를 로드합니다. 투명도가 있는 이미지면 alpha=True로 둡니다.
    """
    global _images
    if path not in _images:
        full_path = get_resource_path(path)
        try:
            img = pygame.image.load(full_path)
            if alpha:
                _images[path] = img.convert_alpha()
            else:
                _images[path] = img.convert()
        except pygame.error as e:
            print(f"이미지를 찾을 수 없습니다: {full_path}")
            # 에러 방지용 더미(임시) 표면 반환
            fallback = pygame.Surface((50, 50))
            fallback.fill((255, 0, 255)) # 눈에 띄는 자홍색
            _images[path] = fallback

    return _images[path]

def get_sound(path):
    """
    효과음(SFX)을 로드합니다.
    """
    global _sounds
    if path not in _sounds:
        full_path = get_resource_path(path)
        try:
            _sounds[path] = pygame.mixer.Sound(full_path)
        except pygame.error as e:
            print(f"사운드를 찾을 수 없습니다: {full_path}")
            # 에러가 나면 빈 사운드 객체를 만들 수는 없으므로 None 반환
            _sounds[path] = None
            
    return _sounds[path]

def get_font(path, size):
    """
    외부 폰트 파일(.ttf)을 로드합니다. 크기별로 따로 캐싱합니다.
    """
    global _fonts
    key = f"{path}_{size}"
    
    if key not in _fonts:
        full_path = get_resource_path(path)
        try:
            _fonts[key] = pygame.font.Font(full_path, size)
        except pygame.error as e:
            print(f"폰트를 찾을 수 없습니다: {full_path}. 기본 폰트로 대체합니다.")
            _fonts[key] = pygame.font.SysFont(None, size)
            
    return _fonts[key]

def play_bgm(path, volume=0.5):
    """
    배경음악(BGM)을 재생합니다. BGM은 스트리밍 방식이므로 캐싱하지 않습니다.
    """
    full_path = get_resource_path(path)
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1) # -1: 무한 반복
    except pygame.error as e:
        print(f"BGM을 찾을 수 없거나 재생할 수 없습니다: {full_path}")