import pygame
import os
import sys

_images = {}
_sounds = {}
_fonts = {}
_sound_cooldowns = {}

def resource_path(relative_path):
    """ 실행 파일 내의 리소스 경로를 반환합니다. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_image(path, alpha=True):
    """ 이미지를 캐싱하여 불러옵니다. """
    if path in _images:
        return _images[path]
    
    real_path = resource_path(path)
    try:
        img = pygame.image.load(real_path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _images[path] = img
        return img
    except pygame.error as e:
        print(f"이미지를 찾을 수 없습니다: {real_path}")
        return None

def get_sound(path):
    global _sounds
    if path not in _sounds:
        full_path = resource_path(path) # 수정됨: get_resource_path -> resource_path
        try:
            _sounds[path] = pygame.mixer.Sound(full_path)
        except pygame.error as e:
            print(f"사운드를 찾을 수 없습니다: {full_path}")
            _sounds[path] = None
    return _sounds[path]

def get_font(path, size):
    global _fonts
    key = f"{path}_{size}"
    if key not in _fonts:
        full_path = resource_path(path) # 수정됨: get_resource_path -> resource_path
        try:
            _fonts[key] = pygame.font.Font(full_path, size)
        except pygame.error as e:
            print(f"폰트를 찾을 수 없습니다: {full_path}. 기본 폰트로 대체합니다.")
            _fonts[key] = pygame.font.SysFont(None, size)
    return _fonts[key]

def play_bgm(path, volume=0.5):
    full_path = resource_path(path) # 수정됨: get_resource_path -> resource_path
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"BGM을 찾을 수 없거나 재생할 수 없습니다: {full_path}")

def play_sound(path, volume=0.5, cooldown_ms=50):
    global _sound_cooldowns
    current_time = pygame.time.get_ticks()
    if path in _sound_cooldowns:
        if current_time - _sound_cooldowns[path] < cooldown_ms:
            return
            
    snd = get_sound(path)
    if snd is not None:
        channel = pygame.mixer.find_channel()
        if channel:
            snd.set_volume(volume)
            channel.play(snd)
            _sound_cooldowns[path] = current_time

def load_sprite_sheet(path, frame_width, frame_height, columns, rows):
    """
    스프라이트 시트를 불러와서 프레임별로 자른 2차원 리스트를 반환합니다.
    """
    # 수정됨: 이제 get_image 함수가 제대로 alpha 인자를 처리함
    sheet = get_image(path, alpha=True)
    if sheet is None: return [] # 이미지 로드 실패 시 빈 리스트 반환
    
    frames = []
    for row in range(rows):
        row_frames = []
        for col in range(columns):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            row_frames.append(frame)
        frames.append(row_frames)
    return frames