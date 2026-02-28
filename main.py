import asyncio

import pygame
import random
import sys
import math

pygame.init()

# ===== EKRAN =====
SIRINA_EKRANA = 1920
VISINA_EKRANA = 1080
screen = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
pygame.display.set_caption("Ronilac igra")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 30)

# ===== SVET =====
SVET_SIRINA = SIRINA_EKRANA * 2
SVET_VISINA = VISINA_EKRANA * 2

# ===== POZADINA =====
try:
    bg_image = pygame.image.load("./pozadina3.png").convert()
    bg_image = pygame.transform.smoothscale(bg_image, (SVET_SIRINA, SVET_VISINA))
except:
    bg_image = pygame.Surface((SVET_SIRINA, SVET_VISINA))
    bg_image.fill((0, 100, 200))

# ===== SLIKE =====
try:
    igrac_img = pygame.image.load("./diver.png").convert_alpha()
    igrac_img = pygame.transform.smoothscale(igrac_img, (80,80))
except:
    igrac_img = pygame.Surface((80,80), pygame.SRCALPHA)
    igrac_img.fill((0,255,0))

igrac_base = igrac_img.copy()

try:
    kristal_img = pygame.image.load("./uzvicni koin.png").convert_alpha()
    kristal_img = pygame.transform.smoothscale(kristal_img, (40,40))
except:
    kristal_img = pygame.Surface((40,40), pygame.SRCALPHA)
    kristal_img.fill((255,255,0))

try:
    meduza_img_original = pygame.image.load("./meduya2.0.png").convert_alpha()
    meduza_img_original = pygame.transform.smoothscale(meduza_img_original, (60,60))
except:
    meduza_img_original = pygame.Surface((60,60), pygame.SRCALPHA)
    meduza_img_original.fill((255,0,0))

# ===== OBJEKTI =====
igrac = pygame.Rect(SVET_SIRINA//2, SVET_VISINA//2, 80, 80)
brzina_igraca = 8

def napravi_kristale(broj=10):
    lst = []
    for _ in range(broj):
        rect = pygame.Rect(random.randint(0, SVET_SIRINA-40),
                           random.randint(0, SVET_VISINA-40), 40, 40)
        lst.append(rect)
    return lst

def napravi_meduze(broj=5):
    lst = []
    for _ in range(broj):
        rect = pygame.Rect(random.randint(0, SVET_SIRINA-50),
                           random.randint(0, SVET_VISINA-50), 50, 50)
        brzina_x = random.choice([-3, -2, 2, 3])
        brzina_y = random.choice([-3, -2, 2, 3])
        lst.append({"rect": rect, "brzina_x": brzina_x, "brzina_y": brzina_y})
    return lst


# ===== GLAVNA PETLJA =====
async def main():
    kristali = napravi_kristale(10)
    meduze = napravi_meduze()

    score = 0
    kraj_igre = False

    igrac_vx = 0.0
    igrac_vy = 0.0
    gleda_levo = False

    start_time = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and kraj_igre:
                    kraj_igre = False
                    score = 0
                    igrac.center = (SVET_SIRINA//2, SVET_VISINA//2)
                    kristali = napravi_kristale(10)
                    meduze = napravi_meduze()
                    igrac_vx = 0.0
                    igrac_vy = 0.0
                    start_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()

        if not kraj_igre:

            dx = 0
            dy = 0

            if keys[pygame.K_LEFT]:
                dx -= 1
                gleda_levo = True
            if keys[pygame.K_RIGHT]:
                dx += 1
                gleda_levo = False
            if keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_DOWN]:
                dy += 1

            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                dx = dx / length * brzina_igraca
                dy = dy / length * brzina_igraca

            # smooth underwater feel
            igrac_vx += (dx - igrac_vx) * 0.35
            igrac_vy += (dy - igrac_vy) * 0.35

            igrac_vx *= 0.90
            igrac_vy *= 0.90

            igrac.x += int(igrac_vx)
            igrac.y += int(igrac_vy)

            igrac.x = max(0, min(igrac.x, SVET_SIRINA - igrac.width))
            igrac.y = max(0, min(igrac.y, SVET_VISINA - igrac.height))

            # MEDUZE
            for m in meduze:
                m["rect"].x += m["brzina_x"]
                m["rect"].y += m["brzina_y"]

                if m["rect"].left <= 0 or m["rect"].right >= SVET_SIRINA:
                    m["brzina_x"] *= -1
                if m["rect"].top <= 0 or m["rect"].bottom >= SVET_VISINA:
                    m["brzina_y"] *= -1

                if igrac.colliderect(m["rect"]):
                    kraj_igre = True


            for k in kristali:
                if igrac.colliderect(k):
                    score += 1
                    k.x = random.randint(0, SVET_SIRINA-40)
                    k.y = random.randint(0, SVET_VISINA-40)

        # ===== KAMERA =====
        kamera_x = igrac.centerx - SIRINA_EKRANA//2
        kamera_y = igrac.centery - VISINA_EKRANA//2
        kamera_x = max(0, min(kamera_x, SVET_SIRINA-SIRINA_EKRANA))
        kamera_y = max(0, min(kamera_y, SVET_VISINA-VISINA_EKRANA))

        # ===== CRTANJE =====
        screen.blit(bg_image, (-kamera_x, -kamera_y))
        for k in kristali:
            screen.blit(kristal_img, (k.x - kamera_x, k.y - kamera_y))

        for m in meduze:
            ugao = math.degrees(math.atan2(-m["brzina_y"], m["brzina_x"])) - 90
            rotirana_meduza = pygame.transform.rotate(meduza_img_original, ugao)
            rect_rot = rotirana_meduza.get_rect(center=m["rect"].center)
            screen.blit(rotirana_meduza, (rect_rot.x - kamera_x, rect_rot.y - kamera_y))

        # ===== CRTANJE IGRAČA (ISPRAVNO CENTRIRAN FLIP) =====
        if gleda_levo:
            igrac_img_draw = pygame.transform.flip(igrac_base, True, False)
        else:
            igrac_img_draw = igrac_base

        rect_draw = igrac_img_draw.get_rect(center=igrac.center)
        screen.blit(igrac_img_draw, (rect_draw.x - kamera_x, rect_draw.y - kamera_y))

        # ===== HUD =====
        elapsed_ms = pygame.time.get_ticks() - start_time
        elapsed_s = elapsed_ms // 1000
        mm = elapsed_s // 60
        ss = elapsed_s % 60

        time_text = font.render(f"{mm:02d}:{ss:02d}", True, (255,255,255))
        coin_text = small_font.render(f"Novcici: {score}", True, (255,255,255))

        padding = 200
        screen.blit(time_text, (SIRINA_EKRANA - padding - time_text.get_width(), padding))
        screen.blit(coin_text, (SIRINA_EKRANA - padding - coin_text.get_width(),
                                padding + time_text.get_height() + 6))

        if kraj_igre:
            overlay = pygame.Surface((SIRINA_EKRANA, VISINA_EKRANA))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))

            text = font.render("GAME OVER!", True, (255,0,0))
            restart = small_font.render("SPACE = restart | ESC = quit", True, (255,255,0))

            screen.blit(text, (SIRINA_EKRANA//2 - text.get_width()//2, VISINA_EKRANA//2 - 40))
            screen.blit(restart, (SIRINA_EKRANA//2 - restart.get_width()//2, VISINA_EKRANA//2 + 40))

        pygame.display.flip()

        await asyncio.sleep(0)

    #pygame.quit()
    #sys.exit()

asyncio.run(main())