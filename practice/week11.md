# 2026-05-12 (11주차 실습 정리)

## 오늘 한 것
- pyInstaller 빌드
- resource_path() 함수 추가
- -add-data 옵션으로 에셋 포함
- .exe 실행 확인

## resource_path() 를 써야하는 이유

- 배포의 이식성: 이 코드를 친구 컴퓨터에 보냈을 때, 친구 컴퓨터의 경로가 어떻게 되어 있든 상관없이 항상 정확한 위치를 찾아냅니다.

- 경로 에러 방지: FileNotFoundError를 방지하는 가장 표준적이고 안전한 방법입니다. 전 세계 모든 파이썬 개발자들이 PyInstaller를 쓸 때 사용하는 사실상의 공식 관례(Standard Convention)입니다.

- 코드의 일관성: 경로 계산 로직을 파일마다 다르게 짜지 않고, resource_path()라는 함수 하나로 모든 파일 호출을 통일하여 유지보수가 쉽습니다.

결론적으로, 이 함수를 쓰지 않으면 개발자는 본인의 컴퓨터에서만 잘 돌아가는 코드를 짜게 됩니다. 타인의 컴퓨터나 다른 환경에서도 게임이 정상적으로 실행되게 하려면 resource_path는 선택이 아닌 필수입니다.

이 로직을 그대로 사용하면, 교수님 컴퓨터에서 제출할 때 경로 에러로 인한 감점을 원천 봉쇄할 수 있습니다!

## 빌드 명령어
- pyinstaller --onefile --noconsole --add-data "Assets;Assets" dodger.py

## AI 활용 내역 
# Question
- pyinstaller dodger.py 를 했는데, dist 폴더 생성이 되었고, 그 안에 exe 생성이 되서 실행을 했는데 실행조차 안돼

# Answer
- PyInstaller로 빌드한 EXE가 실행되지 않는 건 개발자라면 누구나 한 번은 겪는 '자산 경로(Asset Path)' 문제입니다. 현재 dodger.py에서 사용 중인 이미지, 폰트, 혹은 Base64로 처리하지 않은 외부 파일들이 EXE 파일 입장에서는 "어디 있는지 모르는" 상태이기 때문이죠. 
- 가장 먼저 할 일은 '왜 안 되는지' 에러 메시지를 확인하는 것입니다.

# 1. 에러 메시지 확인하기 (가장 중요)
그냥 EXE를 더블 클릭하면 창이 바로 닫혀서 에러를 볼 수 없습니다.

1. dist 폴더 내에서 Shift + 우클릭 -> **'여기에 PowerShell(또는 터미널) 열기'**를 선택하세요.
2. 터미널에 ./dodger.exe를 입력하고 엔터를 칩니다.
3. 분명 FileNotFoundError나 특정 모듈 관련 에러가 뜰 겁니다. 그 메시지를 보면 답이 나옵니다.

# 2. 가장 흔한 원인과 해결책
① 외부 파일(Assets) 누락

PyInstaller는 파이썬 코드는 묶어주지만, 이미지 폴더나 폰트 파일은 자동으로 넣어주지 않습니다.

- 해결: dist 폴더 안에 있는 dodger.exe 옆에 게임에서 사용하는 assets 폴더나 이미지 파일들을 수동으로 복사해서 넣어보세요. 보통 이 단계에서 해결됩니다.

② 상대 경로 문제 (sys._MEIPASS)

--onefile 옵션을 써서 하나의 EXE로 만들면, 실행 시 임시 폴더에 압축을 풉니다. 이때 코드 내의 상대 경로가 꼬입니다. 이를 해결하려면 파일 경로를 불러오는 함수를 추가해야 합니다.

utils.py나 dodger.py 상단에 추가:

    import sys
    import os

    def resource_path(relative_path):
        """ 리소스 파일의 절대 경로를 반환합니다. (PyInstaller 대응) """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # 사용 예시:
    # font = pygame.font.Font(resource_path("assets/my_font.ttf"), 30)

③ Pygame Mixer 에러

간혹 사운드 관련 모듈이 포함되지 않아 터지는 경우가 있습니다. 빌드 명령어를 줄 때 아래와 같이 명시해 보세요.

# 3. 추천하는 빌드 명령어
콘솔 창이 뜨지 않게 하고(--noconsole), 필요한 데이터 폴더를 포함시키는(--add-data) 명령어입니다.

    # 윈도우 기준 (폴더 구분자 ; 사용)
    pyinstaller --onefile --noconsole --add-data "assets;assets" dodger.py

(참고: assets;assets는 "현재 경로의 assets 폴더를 EXE 내부의 assets 폴더로 넣어라"는 뜻입니다.)

# 💡 팁
처음에는 --noconsole 옵션을 빼고 빌드하세요. 그래야 에러가 났을 때 검은 창(콘솔)에 에러 내용이 남아서 디버깅하기 훨씬 편합니다.

혹시 터미널에서 실행했을 때 뜨는 에러 메시지가 있다면 알려주세요. 바로 해결해 드릴 수 있습니다! 전공자답게 에러 로그부터 뜯어봅시다. 🚀