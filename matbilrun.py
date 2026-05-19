import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

#  EKRAN
WIDTH  = 1024
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MATBIL RUN")
clock  = pygame.time.Clock()
FPS    = 60

#  FONTLAR
try:
    font     = pygame.font.Font("pressstart2p.ttf", 14)
    font_big = pygame.font.Font("pressstart2p.ttf", 28)
except:
    font     = pygame.font.SysFont("couriernew", 18, bold=True)
    font_big = pygame.font.SysFont("couriernew", 34, bold=True)

#  BOYUTLAR
DINO_SIZE   = 80    # Karakter boyutu
ENGEL_W_SC  = 55    # Engel genisligi
ENGEL_H_SC  = 90    # Engel yuksekligi
BOMBA_W_SC  = 95    # Ozel engel genisligi
BOMBA_H_SC  = 100   # Ozel engel yuksekligi
GROUND_H    = 200   # Zemin yuksekligi

#Floating sorunu
GROUND_OFFSET = 36  # karakter ne kadar batıyor

#  ASSETS
def load_img(path, w, h, fallback=(180, 100, 50)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    except:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(fallback)
        return s

# Arka plan
try:
    bg_img = pygame.transform.scale(
        pygame.image.load("bg.png").convert_alpha(), (WIDTH, HEIGHT))
except:
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((100, 160, 220))

# Zemin
try:
    ground_img = pygame.transform.scale(
        pygame.image.load("yer1.png").convert_alpha(), (WIDTH, GROUND_H))
except:
    ground_img = pygame.Surface((WIDTH, GROUND_H))
    ground_img.fill((90, 60, 30))

# Karakter
run0_img = load_img("run0.png", DINO_SIZE, DINO_SIZE, (60, 180, 60))
run1_img = load_img("run1.png", DINO_SIZE, DINO_SIZE, (60, 200, 80))
jump_img = load_img("jump.png", DINO_SIZE, DINO_SIZE, (200, 200, 60))

# Engeller
engel_img = load_img("engel.png", ENGEL_W_SC, ENGEL_H_SC, (80, 140, 60))
bomba_img = load_img("bomb.png", BOMBA_W_SC, BOMBA_H_SC, (200, 60,  60))

#  SES
snd_jump = None
try:
    pygame.mixer.music.load("music.wav")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except:
    pass
try:
    snd_jump = pygame.mixer.Sound("jump.mp3")
    snd_jump.set_volume(0.05)
except:
    pass

#KURALLAR/FIZIK
GROUND_TOP = HEIGHT - GROUND_H          # zemin baslangici y ustunde
FLOOR_Y    = GROUND_TOP + GROUND_OFFSET # karakterin geldigi kisim

GRAVITY    = 0.9
JUMP_POWER = -17
DINO_X     = 120
START_SPEED = 7
SPEED_INC   = 1

WHITE  = (255, 255, 255)
RED    = (255,  80,  80)
YELLOW = (255, 230,  50)
GRAY   = (180, 180, 180)

#  Duzeltmeler
def draw_shadowed(surf, text_surf, x, y, offset=2):
    shadow = text_surf.copy()
    shadow.fill((0, 0, 0, 160), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(shadow, (x + offset, y + offset))
    surf.blit(text_surf, (x, y))


def make_obstacle(): #Onemli matlab oranı
    if random.randint(1, 100) <= 15:
        rect = pygame.Rect(WIDTH, FLOOR_Y - BOMBA_H_SC, BOMBA_W_SC, BOMBA_H_SC)
        return {"rect": rect, "type": "special", "clicks": 0, "passed": False}
    else:
        rect = pygame.Rect(WIDTH, FLOOR_Y - ENGEL_H_SC, ENGEL_W_SC, ENGEL_H_SC)
        return {"rect": rect, "type": "normal", "clicks": 0, "passed": False}

#  OYUN DURUMU
high_score = 0

def reset_game():
    global dino_y, dino_vel, is_jumping
    global obstacles, score, speed, ground_x, bg_x, state, next_obs_dist

    bg_x          = 0
    dino_y        = float(FLOOR_Y - DINO_SIZE)
    dino_vel      = 0.0
    is_jumping    = False
    obstacles     = []
    score         = 0
    speed         = START_SPEED
    ground_x      = 0
    next_obs_dist = random.randint(500, 750)
    state         = "playing"

reset_game()

#Loop

while True:
    clock.tick(FPS)

    # ── OLAYLAR ──────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if state == "playing" and not is_jumping:
                    dino_vel   = JUMP_POWER
                    is_jumping = True
                    if snd_jump:
                        snd_jump.play()
            elif event.key == pygame.K_r:
                if state == "gameover":
                    reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "playing":
                mx, my = event.pos
                for obs in obstacles[:]:
                    if obs["type"] == "special" and obs["rect"].collidepoint(mx, my):
                        obs["clicks"] += 1
                        if obs["clicks"] >= 2:
                            obstacles.remove(obs)
                        break

    # Updateler
    if state == "playing":

        # Zemin kaydirma (cok ugrastim)
        ground_x = (ground_x - speed) % (-WIDTH)
        bg_x     = (bg_x - speed // 3) % (-WIDTH)

        # Fizik
        dino_vel += GRAVITY
        dino_y   += dino_vel
        if dino_y >= FLOOR_Y - DINO_SIZE:
            dino_y     = float(FLOOR_Y - DINO_SIZE)
            dino_vel   = 0.0
            is_jumping = False

        dino_rect = pygame.Rect(DINO_X, int(dino_y), DINO_SIZE, DINO_SIZE)

        # Engel olusturma
        spawn = True
        if obstacles and obstacles[-1]["rect"].x > WIDTH - next_obs_dist:
            spawn = False
        if spawn:
            obstacles.append(make_obstacle())
            next_obs_dist = random.randint(400, 700)

        # Hareket + skor + carpisma olaylari
        for obs in obstacles[:]:
            obs["rect"].x -= speed

            if obs["rect"].right < DINO_X and not obs["passed"]:
                score += 1
                obs["passed"] = True
                if score % 5 == 0:
                    speed = min(speed + SPEED_INC, 20)

            if dino_rect.inflate(-20, -20).colliderect(obs["rect"]):
                state = "gameover"
                if score > high_score:
                    high_score = score

            if obs["rect"].right < 0:
                obstacles.remove(obs)

    # Ekran gorsel ayarlari

    screen.blit(bg_img, (bg_x,         0))
    screen.blit(bg_img, (bg_x + WIDTH, 0))
    screen.blit(ground_img, (ground_x,         GROUND_TOP))
    screen.blit(ground_img, (ground_x + WIDTH, GROUND_TOP))

    if state == "playing":

        # Karakter
        if is_jumping:
            char_img = jump_img
        else:
            frame    = (pygame.time.get_ticks() // 130) % 2
            char_img = run0_img if frame == 0 else run1_img
        screen.blit(char_img, (DINO_X, int(dino_y)))

        # Engeller
        for obs in obstacles:
            if obs["type"] == "special":
                screen.blit(bomba_img, (obs["rect"].x, obs["rect"].y))
                # Tiklama bari (ugrastirici)
                if obs["clicks"] == 1:
                    bx, by = obs["rect"].x, obs["rect"].y - 12
                    bw, bh = BOMBA_W_SC, 7
                    pygame.draw.rect(screen, (60,  0,  0),    (bx,      by, bw,      bh))
                    pygame.draw.rect(screen, (220, 60, 60),   (bx,      by, bw // 2, bh))
                    pygame.draw.rect(screen, WHITE,           (bx - 1, by - 1, bw + 2, bh + 2), 1)
            else:
                screen.blit(engel_img, (obs["rect"].x, obs["rect"].y))

        # Skor Tablosu
        hi_surf  = font.render("HI: %03d"   % high_score, True, GRAY)
        scr_surf = font.render("SKOR: %03d" % score,      True, WHITE)
        draw_shadowed(screen, hi_surf,  WIDTH - hi_surf.get_width()  - 20, 20)
        draw_shadowed(screen, scr_surf, WIDTH - scr_surf.get_width() - 20, 44)
        draw_shadowed(screen, font.render("HIZ: %d" % speed, True, YELLOW), 20, 20)

    elif state == "gameover":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        cx, cy = WIDTH // 2, HEIGHT // 2

        s1 = font_big.render("OYUN BITTI!", True, RED)
        s2 = font.render("SKOR: %d     EN YUKSEK: %d" % (score, high_score), True, WHITE)
        s3 = font.render("Yeniden baslamak icin  R", True, GRAY)

        screen.blit(s1, s1.get_rect(center=(cx, cy - 55)))
        screen.blit(s2, s2.get_rect(center=(cx, cy +  5)))
        screen.blit(s3, s3.get_rect(center=(cx, cy + 55)))

    pygame.display.update()
