import pygame
import sys
import json
import os
import arabic_reshaper
from bidi.algorithm import get_display

pygame.init()

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 100, 200)
LIGHT_GRAY = (200, 200, 200)

# --- سیستم دو زبانه ---
LANG = "en"
LANG_FILE = "pong_lang.json"

if os.path.exists(LANG_FILE):
    try:
        with open(LANG_FILE, "r") as f:
            LANG = json.load(f).get("lang", "en")
    except:
        LANG = "en"

def save_lang():
    with open(LANG_FILE, "w") as f:
        json.dump({"lang": LANG}, f)

# --- تابع فونت ---
def get_font(size, bold=False):
    if LANG == "fa":
        for font_name in ["Tahoma", "Arial", "B Nazanin", "IRANSans"]:
            try:
                return pygame.font.SysFont(font_name, size, bold=bold)
            except:
                continue
        return pygame.font.SysFont("Tahoma", size, bold=bold)
    else:
        return pygame.font.SysFont("Arial", size, bold=bold)

# --- تابع اصلاح متن فارسی ---
def fa_text(text):
    """متن فارسی رو برای نمایش در Pygame آماده می‌کنه (اتصال حروف + راست‌به‌چپ)"""
    if LANG == "fa":
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except:
            return text
    return text

# --- متن‌های ترجمه ---
TEXTS = {
    "en": {
        "title": "PONG GAME",
        "start_new": "start new game",
        "high_scores": "High Scores",
        "select_mode": "Select Mode",
        "1p": "1 Player (CPU)",
        "2p": "2 Players",
        "screen_size": "Screen Size",
        "small": "Small",
        "medium": "Medium",
        "big": "Big (Fullscreen)",
        "cpu_diff": "CPU Difficulty",
        "easy": "Easy",
        "normal": "Normal",
        "hard": "Hard",
        "ball_speed": "Ball Speed",
        "slow": "Slow",
        "fast": "Fast",
        "target_mode": "Target Mode",
        "with_target": "With Target",
        "without_target": "Without Target",
        "target_score": "Target Score",
        "start": "START",
        "pause": "PAUSED",
        "p1": "Player 1",
        "p2_cpu": "Player 2 / CPU",
        "restart": "Restart",
        "home": "Home",
        "game_over": "GAME OVER",
        "wins": "Wins!",
        "final_score": "Final Score",
        "no_scores": "No scores yet!",
        "back": "Back",
        "lang_btn": "فا",
        "guide_title": "How to Play",
        "guide_text": [
            "Player 1 (Left): W / S keys",
            "Player 2 (Right): Arrow Up / Down keys",
            "CPU plays automatically in 1P mode",
            "Pause button is at top-left of the game",
            "First to reach Target Score wins!",
            "",
            "Click anywhere or press any key to start"
        ],
    },
    "fa": {
        "title": "بازی پونگ",
        "start_new": "شروع بازی جدید",
        "high_scores": "جدول امتیازات",
        "select_mode": "انتخاب حالت",
        "1p": "یک نفره (کامپیوتر)",
        "2p": "دو نفره",
        "screen_size": "اندازه صفحه",
        "small": "کوچک",
        "medium": "متوسط",
        "big": "بزرگ (تمام‌صفحه)",
        "cpu_diff": "سختی کامپیوتر",
        "easy": "آسان",
        "normal": "معمولی",
        "hard": "سخت",
        "ball_speed": "سرعت توپ",
        "slow": "کند",
        "fast": "سریع",
        "target_mode": "حالت هدف",
        "with_target": "با هدف",
        "without_target": "بدون هدف",
        "target_score": "امتیاز هدف",
        "start": "شروع",
        "pause": "توقف",
        "p1": "بازیکن ۱",
        "p2_cpu": "بازیکن ۲ / کامپیوتر",
        "restart": "شروع مجدد",
        "home": "خانه",
        "game_over": "پایان بازی",
        "wins": "برنده شد!",
        "final_score": "امتیاز نهایی",
        "no_scores": "هنوز امتیازی ثبت نشده!",
        "back": "بازگشت",
        "lang_btn": "EN",
        "guide_title": "راهنمای بازی",
        "guide_text": [
            "بازیکن ۱ (چپ): کلیدهای W و S",
            "بازیکن ۲ (راست): کلیدهای بالا و پایین",
            "در حالت تک‌نفره، کامپیوتر خودکار بازی می‌کند",
            "دکمه توقف در گوشه بالا-چپ صفحه است",
            "هر کس زودتر به امتیاز هدف برسد، برنده است!",
            "",
            "برای شروع، هر جایی کلیک کن یا کلیدی بزن"
        ],
    }
}

def t(key):
    return TEXTS[LANG].get(key, key)

# --- راهنمای بار اول ---
GUIDE_FILE = "pong_guide_seen.json"
show_guide = True
if os.path.exists(GUIDE_FILE):
    try:
        with open(GUIDE_FILE, "r") as f:
            show_guide = not json.load(f).get("seen", False)
    except:
        show_guide = True

def mark_guide_seen():
    global show_guide
    show_guide = False
    with open(GUIDE_FILE, "w") as f:
        json.dump({"seen": True}, f)

# --- متغیرهای سراسری ---
game_mode = "2P"
screen_size = "medium"
cpu_difficulty = 1.0
ball_speed_setting = "normal"
target_mode = False
target_score = 10
current_state = "MAIN_MENU"
score1 = 0
score2 = 0

scores_file = "pong_scores.json"
high_scores = []
if os.path.exists(scores_file):
    try:
        with open(scores_file, "r", encoding="utf-8") as f:
            loaded_scores = json.load(f)
        # Accept only entries in the new format: {"score1": number, "score2": number}.
        # Older files containing only a single number are ignored safely.
        if isinstance(loaded_scores, list):
            high_scores = [
                item for item in loaded_scores
                if isinstance(item, dict)
                and isinstance(item.get("score1"), int)
                and isinstance(item.get("score2"), int)
            ]
    except (OSError, json.JSONDecodeError, TypeError):
        high_scores = []

def save_high_score():
    """Save a result only for single-player games with target mode disabled."""
    global high_scores

    if game_mode != "1P" or target_mode:
        return
    if score1 == 0 and score2 == 0:
        return

    high_scores.append({"score1": score1, "score2": score2})
    high_scores = sorted(
        high_scores,
        key=lambda item: (item["score1"], -item["score2"]),
        reverse=True
    )[:5]

    try:
        with open(scores_file, "w", encoding="utf-8") as f:
            json.dump(high_scores, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

# --- کلاس دکمه ---
class Button:
    def __init__(self, x, y, width, height, text_key, color, action=None, is_lang=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_key = text_key
        self.color = color
        self.action = action
        self.is_hovered = False
        self.is_lang = is_lang

    def draw(self, surface):
        current_color = self.color
        if self.is_hovered:
            current_color = (min(self.color[0] + 50, 255), 
                             min(self.color[1] + 50, 255), 
                             min(self.color[2] + 50, 255))
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        text = t(self.text_key) if not self.is_lang else t("lang_btn")
        text_surf = get_font(25, True).render(fa_text(text), True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            if self.action:
                self.action()

# --- کلاس راکت و توپ ---
class Paddle:
    def __init__(self, x, y, width, height, speed, is_cpu=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.is_cpu = is_cpu
        self.original_y = y

    def move_up(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def reset(self):
        self.rect.y = self.original_y

class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.base_speed = abs(speed_x)

    def move(self, dt):
        self.rect.x += self.speed_x * dt
        self.rect.y += self.speed_y * dt

    def reset(self):
        self.rect.center = (self.start_x, self.start_y)
        self.speed_x = self.base_speed if self.speed_x > 0 else -self.base_speed
        self.speed_y = self.base_speed if self.speed_y > 0 else -self.base_speed

# --- توابع تغییر وضعیت ---
def set_state(state):
    global current_state
    current_state = state

def toggle_lang():
    global LANG
    LANG = "fa" if LANG == "en" else "en"
    save_lang()

def start_game():
    global score1, score2
    score1 = 0
    score2 = 0
    setup_game_objects()
    set_state("GAMEPLAY")

def go_to_main_menu():
    set_state("MAIN_MENU")

def go_to_player_select():
    set_state("PLAYER_SELECT")

def go_to_size_select():
    set_state("SIZE_SELECT")

def go_to_difficulty_select():
    set_state("DIFFICULTY_SELECT")

def go_to_speed_select():
    set_state("SPEED_SELECT")

def go_to_target_select():
    set_state("TARGET_SELECT")

def go_to_score_select():
    set_state("SCORE_SELECT")

def go_to_leaderboard():
    set_state("LEADERBOARD")

def toggle_pause():
    if current_state == "GAMEPLAY":
        set_state("PAUSE")
    elif current_state == "PAUSE":
        set_state("GAMEPLAY")

def restart_game():
    global score1, score2
    score1 = 0
    score2 = 0
    setup_game_objects()
    set_state("GAMEPLAY")

def increment_score():
    global target_score
    target_score = min(50, target_score + 1)

def decrement_score():
    global target_score
    target_score = max(1, target_score - 1)

# --- تنظیم اشیاء بازی + فول‌اسکرین ---
WIDTH, HEIGHT = 800, 600
paddle1 = None
paddle2 = None
ball = None
pause_btn = None
screen = None

def setup_game_objects():
    global WIDTH, HEIGHT, paddle1, paddle2, ball, pause_btn, screen
    
    if screen_size == "small":
        WIDTH, HEIGHT = 600, 400
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    elif screen_size == "medium":
        WIDTH, HEIGHT = 800, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    else:  # big / fullscreen
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
    
    b_speed = 350
    if ball_speed_setting == "slow": b_speed = 200
    elif ball_speed_setting == "normal": b_speed = 350
    elif ball_speed_setting == "fast": b_speed = 500
    
    p_speed = 400
    
    paddle_width, paddle_height = 15, 100
    paddle1 = Paddle(30, HEIGHT//2 - paddle_height//2, paddle_width, paddle_height, p_speed)
    paddle2 = Paddle(WIDTH - 30 - paddle_width, HEIGHT//2 - paddle_height//2, paddle_width, paddle_height, p_speed, is_cpu=(game_mode=="1P"))
    
    ball = Ball(WIDTH//2, HEIGHT//2, 10, b_speed, b_speed)
    pause_btn = Button(10, 10, 40, 40, "pause", LIGHT_GRAY, toggle_pause)

# --- حلقه اصلی ---
running = True
clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

btn_start_new = Button(250, 300, 300, 60, "start_new", GREEN, go_to_player_select)
btn_high_scores = Button(250, 380, 300, 60, "high_scores", YELLOW, go_to_leaderboard)
btn_lang = Button(700, 10, 80, 40, "lang_btn", LIGHT_GRAY, toggle_lang, is_lang=True)

btn_1p = Button(150, 250, 200, 80, "1p", BLUE, lambda: [setattr(sys.modules[__name__], 'game_mode', '1P'), go_to_size_select()])
btn_2p = Button(450, 250, 200, 80, "2p", GREEN, lambda: [setattr(sys.modules[__name__], 'game_mode', '2P'), go_to_size_select()])

btn_small = Button(250, 180, 300, 60, "small", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'screen_size', 'small'), go_to_difficulty_select() if game_mode=="1P" else go_to_speed_select()])
btn_medium = Button(250, 260, 300, 60, "medium", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'screen_size', 'medium'), go_to_difficulty_select() if game_mode=="1P" else go_to_speed_select()])
btn_big = Button(250, 340, 300, 60, "big", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'screen_size', 'big'), go_to_difficulty_select() if game_mode=="1P" else go_to_speed_select()])

btn_easy = Button(250, 180, 300, 60, "easy", GREEN, lambda: [setattr(sys.modules[__name__], 'cpu_difficulty', 0.5), go_to_speed_select()])
btn_normal = Button(250, 260, 300, 60, "normal", YELLOW, lambda: [setattr(sys.modules[__name__], 'cpu_difficulty', 1.0), go_to_speed_select()])
btn_hard = Button(250, 340, 300, 60, "hard", RED, lambda: [setattr(sys.modules[__name__], 'cpu_difficulty', 1.5), go_to_speed_select()])

btn_slow = Button(250, 180, 300, 60, "slow", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'ball_speed_setting', 'slow'), go_to_target_select()])
btn_normal_speed = Button(250, 260, 300, 60, "normal", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'ball_speed_setting', 'normal'), go_to_target_select()])
btn_fast = Button(250, 340, 300, 60, "fast", LIGHT_GRAY, lambda: [setattr(sys.modules[__name__], 'ball_speed_setting', 'fast'), go_to_target_select()])

btn_with_target = Button(250, 200, 300, 60, "with_target", GREEN, lambda: [setattr(sys.modules[__name__], 'target_mode', True), go_to_score_select()])
btn_without_target = Button(250, 300, 300, 60, "without_target", YELLOW, lambda: [setattr(sys.modules[__name__], 'target_mode', False), start_game()])

btn_inc = Button(450, 200, 50, 50, "pause", LIGHT_GRAY, increment_score)
btn_inc.text_key = "+"
btn_dec = Button(300, 200, 50, 50, "pause", LIGHT_GRAY, decrement_score)
btn_dec.text_key = "-"
btn_start_game = Button(300, 350, 200, 60, "start", GREEN, start_game)

btn_restart_pause = Button(300, 350, 200, 60, "restart", YELLOW, restart_game)
btn_home_pause = Button(300, 430, 200, 60, "home", RED, go_to_main_menu)

btn_restart_over = Button(250, 350, 300, 60, "restart", GREEN, restart_game)
btn_home_over = Button(250, 430, 300, 60, "home", RED, go_to_main_menu)

btn_back_leaderboard = Button(250, 500, 300, 60, "back", LIGHT_GRAY, go_to_main_menu)

# --- توابع رسم ---
def draw_main_menu(surface):
    surface.fill(BLACK)
    title = get_font(60, True).render(fa_text(t("title")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_start_new.draw(surface)
    btn_high_scores.draw(surface)
    btn_lang.draw(surface)

def draw_player_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("select_mode")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_1p.draw(surface)
    btn_2p.draw(surface)
    btn_lang.draw(surface)

def draw_size_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("screen_size")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_small.draw(surface)
    btn_medium.draw(surface)
    btn_big.draw(surface)
    btn_lang.draw(surface)

def draw_difficulty_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("cpu_diff")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_easy.draw(surface)
    btn_normal.draw(surface)
    btn_hard.draw(surface)
    btn_lang.draw(surface)

def draw_speed_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("ball_speed")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_slow.draw(surface)
    btn_normal_speed.draw(surface)
    btn_fast.draw(surface)
    btn_lang.draw(surface)

def draw_target_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("target_mode")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    btn_with_target.draw(surface)
    btn_without_target.draw(surface)
    btn_lang.draw(surface)

def draw_score_select(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("target_score")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    score_text = get_font(50, True).render(str(target_score), True, WHITE)
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))
    btn_inc.draw(surface)
    btn_dec.draw(surface)
    btn_start_game.draw(surface)
    btn_lang.draw(surface)

def draw_gameplay(surface):
    surface.fill(BLACK)
    pygame.draw.line(surface, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    pygame.draw.rect(surface, WHITE, paddle1.rect)
    pygame.draw.rect(surface, WHITE, paddle2.rect)
    pygame.draw.ellipse(surface, WHITE, ball.rect)
    score_text = get_font(40, True).render(f"{score1}   -   {score2}", True, WHITE)
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
    pause_btn.draw(surface)

def draw_pause(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    title = get_font(50, True).render(fa_text(t("pause")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    score_text = get_font(30).render(fa_text(f"{t('p1')}: {score1}  |  {t('p2_cpu')}: {score2}"), True, WHITE)
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))
    btn_restart_pause.draw(surface)
    btn_home_pause.draw(surface)

def draw_game_over(surface):
    surface.fill(BLACK)
    title = get_font(60, True).render(fa_text(t("game_over")), True, RED)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    winner = t("p1") if score1 > score2 else (t("1p") if game_mode == "1P" else t("2p"))
    win_text = get_font(40).render(fa_text(f"{winner} {t('wins')}"), True, WHITE)
    surface.blit(win_text, (WIDTH//2 - win_text.get_width()//2, 200))
    score_text = get_font(30).render(fa_text(f"{t('final_score')}: {score1} - {score2}"), True, LIGHT_GRAY)
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 260))
    btn_restart_over.draw(surface)
    btn_home_over.draw(surface)

def draw_leaderboard(surface):
    surface.fill(BLACK)
    title = get_font(40, True).render(fa_text(t("high_scores")), True, WHITE)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 50))

    if not high_scores:
        text = get_font(30).render(fa_text(t("no_scores")), True, GRAY)
        surface.blit(text, (WIDTH//2 - text.get_width()//2, 200))
    else:
        sorted_scores = sorted(
            high_scores,
            key=lambda item: (item["score1"], -item["score2"]),
            reverse=True
        )[:5]
        for i, result in enumerate(sorted_scores):
            result_text = f"{result['score1']} vs {result['score2']}"
            text = get_font(30).render(f"{i+1}. {result_text}", True, WHITE)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i*50))

    btn_back_leaderboard.draw(surface)

def draw_guide(surface):
    surface.fill(BLACK)
    title = get_font(50, True).render(fa_text(t("guide_title")), True, YELLOW)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    y = 160
    for line in t("guide_text"):
        text = get_font(24).render(fa_text(line), True, WHITE)
        surface.blit(text, (WIDTH//2 - text.get_width()//2, y))
        y += 40

# --- حلقه اصلی ---
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if screen_size == "big":
                screen = pygame.display.set_mode((800, 600))
                WIDTH, HEIGHT = 800, 600
                setup_game_objects()
                continue
        
        if show_guide:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                mark_guide_seen()
            continue
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if current_state == "MAIN_MENU":
                    btn_start_new.check_click(pos)
                    btn_high_scores.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "PLAYER_SELECT":
                    btn_1p.check_click(pos)
                    btn_2p.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "SIZE_SELECT":
                    btn_small.check_click(pos)
                    btn_medium.check_click(pos)
                    btn_big.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "DIFFICULTY_SELECT":
                    btn_easy.check_click(pos)
                    btn_normal.check_click(pos)
                    btn_hard.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "SPEED_SELECT":
                    btn_slow.check_click(pos)
                    btn_normal_speed.check_click(pos)
                    btn_fast.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "TARGET_SELECT":
                    btn_with_target.check_click(pos)
                    btn_without_target.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "SCORE_SELECT":
                    btn_inc.check_click(pos)
                    btn_dec.check_click(pos)
                    btn_start_game.check_click(pos)
                    btn_lang.check_click(pos)
                elif current_state == "GAMEPLAY":
                    pause_btn.check_click(pos)
                elif current_state == "PAUSE":
                    btn_restart_pause.check_click(pos)
                    btn_home_pause.check_click(pos)
                elif current_state == "GAME_OVER":
                    btn_restart_over.check_click(pos)
                    btn_home_over.check_click(pos)
                elif current_state == "LEADERBOARD":
                    btn_back_leaderboard.check_click(pos)

    if not show_guide:
        mouse_pos = pygame.mouse.get_pos()
        if current_state == "MAIN_MENU":
            btn_start_new.check_hover(mouse_pos)
            btn_high_scores.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "PLAYER_SELECT":
            btn_1p.check_hover(mouse_pos)
            btn_2p.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "SIZE_SELECT":
            btn_small.check_hover(mouse_pos)
            btn_medium.check_hover(mouse_pos)
            btn_big.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "DIFFICULTY_SELECT":
            btn_easy.check_hover(mouse_pos)
            btn_normal.check_hover(mouse_pos)
            btn_hard.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "SPEED_SELECT":
            btn_slow.check_hover(mouse_pos)
            btn_normal_speed.check_hover(mouse_pos)
            btn_fast.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "TARGET_SELECT":
            btn_with_target.check_hover(mouse_pos)
            btn_without_target.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "SCORE_SELECT":
            btn_inc.check_hover(mouse_pos)
            btn_dec.check_hover(mouse_pos)
            btn_start_game.check_hover(mouse_pos)
            btn_lang.check_hover(mouse_pos)
        elif current_state == "GAMEPLAY":
            pause_btn.check_hover(mouse_pos)
        elif current_state == "PAUSE":
            btn_restart_pause.check_hover(mouse_pos)
            btn_home_pause.check_hover(mouse_pos)
        elif current_state == "GAME_OVER":
            btn_restart_over.check_hover(mouse_pos)
            btn_home_over.check_hover(mouse_pos)
        elif current_state == "LEADERBOARD":
            btn_back_leaderboard.check_hover(mouse_pos)

        if current_state == "GAMEPLAY":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: paddle1.move_up(dt)
            if keys[pygame.K_s]: paddle1.move_down(dt)
            
            if game_mode == "2P":
                if keys[pygame.K_UP]: paddle2.move_up(dt)
                if keys[pygame.K_DOWN]: paddle2.move_down(dt)
            else:
                cpu_speed = 300 * cpu_difficulty
                if paddle2.rect.centery < ball.rect.centery - 10:
                    paddle2.rect.y += cpu_speed * dt
                elif paddle2.rect.centery > ball.rect.centery + 10:
                    paddle2.rect.y -= cpu_speed * dt
                if paddle2.rect.top < 0: paddle2.rect.top = 0
                if paddle2.rect.bottom > HEIGHT: paddle2.rect.bottom = HEIGHT

            ball.move(dt)
            
            if ball.rect.top <= 0 or ball.rect.bottom >= HEIGHT:
                ball.speed_y *= -1
                
            if ball.rect.colliderect(paddle1.rect) and ball.speed_x < 0:
                ball.speed_x *= -1
                ball.speed_x *= 1.05
                ball.speed_y *= 1.05
                relative_y = (ball.rect.centery - paddle1.rect.centery) / (paddle1.rect.height / 2)
                ball.speed_y += relative_y * 100
                
            if ball.rect.colliderect(paddle2.rect) and ball.speed_x > 0:
                ball.speed_x *= -1
                ball.speed_x *= 1.05
                ball.speed_y *= 1.05
                relative_y = (ball.rect.centery - paddle2.rect.centery) / (paddle2.rect.height / 2)
                ball.speed_y += relative_y * 100

            if ball.rect.left <= 0:
                score2 += 1
                if target_mode and score2 >= target_score:
                    set_state("GAME_OVER")
                else:
                    ball.reset()
                    paddle1.reset()
                    paddle2.reset()
                    
            if ball.rect.right >= WIDTH:
                score1 += 1
                if target_mode and score1 >= target_score:
                    set_state("GAME_OVER")
                else:
                    ball.reset()
                    paddle1.reset()
                    paddle2.reset()

    if show_guide:
        draw_guide(screen)
    else:
        if current_state == "MAIN_MENU":
            draw_main_menu(screen)
        elif current_state == "PLAYER_SELECT":
            draw_player_select(screen)
        elif current_state == "SIZE_SELECT":
            draw_size_select(screen)
        elif current_state == "DIFFICULTY_SELECT":
            draw_difficulty_select(screen)
        elif current_state == "SPEED_SELECT":
            draw_speed_select(screen)
        elif current_state == "TARGET_SELECT":
            draw_target_select(screen)
        elif current_state == "SCORE_SELECT":
            draw_score_select(screen)
        elif current_state == "GAMEPLAY":
            draw_gameplay(screen)
        elif current_state == "PAUSE":
            draw_gameplay(screen)
            draw_pause(screen)
        elif current_state == "GAME_OVER":
            draw_game_over(screen)
        elif current_state == "LEADERBOARD":
            draw_leaderboard(screen)

    pygame.display.flip()

# In no-target mode the game has no automatic end, so save the current result
# once when the player closes the app. Only 1P games without target mode qualify.
if game_mode == "1P" and not target_mode:
    save_high_score()

pygame.quit()
sys.exit()
