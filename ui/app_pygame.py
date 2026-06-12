import os
import pygame
from collections import deque
from game.dungeon import rotation_case, sont_connectees
from game.engine import tour_aventurier
from data.levels import level1, dragons_level1, aventurier_start

CELL_SIZE = 128
FPS = 60

pygame.init()
pygame.display.set_caption("🧱 Wall Is You")

# ----------- Chargement images ----------
def load_image(name, scale=None):
    """
    IMPORTANT FIX:
    - On NE fait PAS convert_alpha() ici, parce que le display
      n'est pas encore initialisé par set_mode au moment où ce code
      est exécuté.
    - On retourne juste la Surface brute.
    """
    path = os.path.join("data", "assets", name)
    try:
        img = pygame.image.load(path)  # pas de convert_alpha ici
        if scale:
            img = pygame.transform.smoothscale(img, scale)
        return img
    except Exception as e:
        print(f"[WARN] Could not load {path}: {e}")
        surf = pygame.Surface(scale or (CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        surf.fill((120, 120, 120))
        pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 3)
        return surf

# on charge tout (surfaces brutes)
FLOOR_IMG_RAW  = load_image("floor.png")            # texture sol
KNIGHT_IMG_RAW = load_image("knight.png")           # on scalle après
DRAGON1_RAW    = load_image("dragon1.png")
DRAGON2_RAW    = load_image("dragon2.png")
DRAGON3_RAW    = load_image("dragon3.png")

LEVELUP_SOUND = pygame.mixer.Sound("data/assets/levelup.wav") if os.path.exists("data/assets/levelup.wav") else None
ROTATE_SOUND  = None  # pas de rotate.wav dispo chez toi actuellement

def bfs_path(donjon, start, goal):
    queue = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if (x, y) == goal:
            return path
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(donjon) and 0 <= ny < len(donjon[0]):
                if sont_connectees(donjon, (x, y), (nx, ny)) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
    return None


class WallIsYouPygame:
    def __init__(self):
        self.hardcore = False
        self.reset_game()
        self.clock = pygame.time.Clock()

        # maintenant que self.screen existe, on peut faire convert_alpha
        self.prepare_images()

    def prepare_images(self):
        """
        Maintenant que le display mode est initialisé,
        on convertit les surfaces pour les rendre belles/translucides,
        on applique les bons scales définitifs.

        On stocke les versions finales dans self.FLOOR_IMG, etc.
        """
        # sol
        if FLOOR_IMG_RAW:
            self.FLOOR_IMG = pygame.transform.smoothscale(
                FLOOR_IMG_RAW.convert_alpha(),  # convert_alpha OK maintenant
                (CELL_SIZE, CELL_SIZE)
            )
        else:
            self.FLOOR_IMG = None

        # knight
        if KNIGHT_IMG_RAW:
            self.KNIGHT_IMG = pygame.transform.smoothscale(
                KNIGHT_IMG_RAW.convert_alpha(),
                (60, 60)
            )
        else:
            self.KNIGHT_IMG = None

        # dragons
        self.DRAGON_IMGS = {
            1: pygame.transform.smoothscale(DRAGON1_RAW.convert_alpha(), (70, 70)) if DRAGON1_RAW else None,
            2: pygame.transform.smoothscale(DRAGON2_RAW.convert_alpha(), (70, 70)) if DRAGON2_RAW else None,
            3: pygame.transform.smoothscale(DRAGON3_RAW.convert_alpha(), (70, 70)) if DRAGON3_RAW else None,
        }

    def reset_game(self):
        # état jeu
        self.donjon = [row[:] for row in level1]
        self.aventurier = aventurier_start
        self.dragons = dragons_level1[:]
        self.intention = []

        # grille
        self.rows = len(self.donjon)
        self.cols = len(self.donjon[0])
        self.width = self.cols * CELL_SIZE
        self.height = self.rows * CELL_SIZE

        # IMPORTANT: on crée l'écran ICI, avant prepare_images()
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.running = True
        self.state = "menu"

    # ----------- IA intention -----------
    def update_intention(self):
        start = self.aventurier[0]
        best_path = None
        best_level = -1
        for dpos, level in self.dragons:
            path = bfs_path(self.donjon, start, dpos)
            if path and level > best_level:
                best_level = level
                best_path = path
        self.intention = best_path or []

    # ----------- DONJON -----------
    def draw_dungeon(self):
        """
        Salles carrées + branches (excroissances) faites en pierre.
        Maintenant on utilise self.FLOOR_IMG (texture sol réelle),
        donc ça devrait enfin ressembler au rendu voulu sans les bordures magenta.
        """
        for i, ligne in enumerate(self.donjon):
            for j, salle in enumerate(ligne):
                x = j * CELL_SIZE
                y = i * CELL_SIZE
                haut, droite, bas, gauche = salle

                center_size = CELL_SIZE // 2
                cx = x + (CELL_SIZE - center_size) // 2
                cy = y + (CELL_SIZE - center_size) // 2
                corridor_width = CELL_SIZE // 5

                # --- bloc central ---
                if self.FLOOR_IMG:
                    center_tex = pygame.transform.smoothscale(
                        self.FLOOR_IMG, (center_size, center_size)
                    )
                else:
                    center_tex = pygame.Surface((center_size, center_size))
                    center_tex.fill((100, 100, 100))

                self.screen.blit(center_tex, (cx, cy))

                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    (cx, cy, center_size, center_size),
                    2,
                    border_radius=6
                )

                def draw_corridor(rect):
                    rx, ry, rw, rh = rect
                    if rw <= 0 or rh <= 0:
                        return
                    if self.FLOOR_IMG:
                        tex = pygame.transform.smoothscale(
                            self.FLOOR_IMG, (rw, rh)
                        )
                    else:
                        tex = pygame.Surface((rw, rh))
                        tex.fill((100, 100, 100))
                    self.screen.blit(tex, (rx, ry))
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 0),
                        (rx, ry, rw, rh),
                        2,
                        border_radius=4
                    )

                if haut:
                    draw_corridor((
                        cx + center_size//2 - corridor_width//2,
                        y,
                        corridor_width,
                        (cy - y) + center_size//2
                    ))
                if droite:
                    draw_corridor((
                        cx + center_size//2,
                        cy + center_size//2 - corridor_width//2,
                        (x + CELL_SIZE) - (cx + center_size//2),
                        corridor_width
                    ))
                if bas:
                    draw_corridor((
                        cx + center_size//2 - corridor_width//2,
                        cy + center_size//2,
                        corridor_width,
                        (y + CELL_SIZE) - (cy + center_size//2)
                    ))
                if gauche:
                    draw_corridor((
                        x,
                        cy + center_size//2 - corridor_width//2,
                        (cx + center_size//2) - x,
                        corridor_width
                    ))

    # ----------- Chemin rouge -----------
    def draw_path(self):
        if len(self.intention) > 1:
            pts = [
                (j * CELL_SIZE + CELL_SIZE // 2,
                 i * CELL_SIZE + CELL_SIZE // 2)
                for (i, j) in self.intention
            ]
            pygame.draw.lines(self.screen, (255, 0, 0), False, pts, 4)

    # ----------- Persos (dragons + héros) -----------
    def draw_characters(self):
        font = pygame.font.SysFont("arial", 20, bold=True)

        # dragons
        for pos, level in self.dragons:
            i, j = pos
            cx = j * CELL_SIZE + CELL_SIZE // 2
            cy = i * CELL_SIZE + CELL_SIZE // 2

            img = self.DRAGON_IMGS.get(level)
            if img:
                self.screen.blit(img, img.get_rect(center=(cx, cy)))

            lvl_txt = font.render(str(level), True, (255, 255, 255))
            self.screen.blit(lvl_txt, lvl_txt.get_rect(center=(cx, cy - CELL_SIZE // 3)))

        # aventurier
        i, j = self.aventurier[0]
        cx = j * CELL_SIZE + CELL_SIZE // 2
        cy = i * CELL_SIZE + CELL_SIZE // 2

        if self.KNIGHT_IMG:
            self.screen.blit(self.KNIGHT_IMG, self.KNIGHT_IMG.get_rect(center=(cx, cy)))

        hero_lvl = font.render(str(self.aventurier[1]), True, (255, 255, 0))
        self.screen.blit(hero_lvl, hero_lvl.get_rect(center=(cx, cy - CELL_SIZE // 3)))

    # ----------- Torche hardcore -----------
    def draw_lighting(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))

        hero_i, hero_j = self.aventurier[0]
        hero_x = hero_j * CELL_SIZE + CELL_SIZE // 2
        hero_y = hero_i * CELL_SIZE + CELL_SIZE // 2

        import random
        flicker = random.randint(-10, 10)
        light_radius = CELL_SIZE * 2.2 + flicker

        for r in range(int(light_radius), 0, -8):
            alpha = int(255 * (r / light_radius))
            pygame.draw.circle(overlay, (0, 0, 0, alpha), (hero_x, hero_y), r)

        self.screen.blit(overlay, (0, 0))

    # ----------- Frame render -----------
    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_dungeon()
        self.draw_path()
        self.draw_characters()
        if self.hardcore:
            self.draw_lighting()
        pygame.display.flip()

    # ----------- Fondu noir -----------
    def fade_transition(self, fade_in=True, duration=600):
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))

        clock = pygame.time.Clock()
        steps = 30
        step_alpha = max(1, int(255 / steps))
        delay_ms = max(1, duration // steps)

        if fade_in:
            for alpha in range(255, -1, -step_alpha):
                overlay.set_alpha(alpha)
                self.screen.fill((0,0,0))
                self.draw_dungeon()
                self.draw_path()
                self.draw_characters()
                if self.hardcore:
                    self.draw_lighting()
                self.screen.blit(overlay, (0, 0))
                pygame.display.flip()
                clock.tick(1000 // delay_ms)
        else:
            for alpha in range(0, 256, step_alpha):
                overlay.set_alpha(alpha)
                self.screen.blit(overlay, (0, 0))
                pygame.display.flip()
                clock.tick(1000 // delay_ms)

    # ----------- Input joueur -----------
    def handle_click(self, pos):
        j = pos[0] // CELL_SIZE
        i = pos[1] // CELL_SIZE
        if 0 <= i < self.rows and 0 <= j < self.cols:
            rotation_case(self.donjon, i, j)
            if ROTATE_SOUND:
                ROTATE_SOUND.play()

    def play_turn(self):
        prev_level = self.aventurier[1]
        self.aventurier, self.dragons, result = tour_aventurier(
            self.donjon,
            self.aventurier,
            self.dragons,
            self.intention or []
        )

        if self.aventurier[1] > prev_level and LEVELUP_SOUND:
            LEVELUP_SOUND.play()
            self.flash_effect((255, 255, 0))

        if result == "VICTOIRE":
            self.state = "victory"
        elif result == "GAME_OVER":
            self.state = "game_over"

    def flash_effect(self, color):
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(color)
        for alpha in range(150, 0, -10):
            overlay.set_alpha(alpha)
            self.render()
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    # ----------- Menu principal -----------
    def show_menu(self):
        menu_bg = load_image("menu_bg.png", scale=None)
        bg_w, bg_h = menu_bg.get_size()

        self.screen = pygame.display.set_mode((bg_w, bg_h))
        self.width, self.height = bg_w, bg_h
        pygame.display.set_caption("🧱 Wall Is You — Menu")

        btn_normal_rect   = pygame.Rect(bg_w//2 - 250, bg_h//2 - 40, 500, 60)
        btn_hardcore_rect = pygame.Rect(bg_w//2 - 250, bg_h//2 + 60, 500, 60)

        font_big = pygame.font.SysFont("arial", 28, bold=True)
        font_sub = pygame.font.SysFont("arial", 18)

        DEBUG_RECTANGLES = False

        while self.state == "menu":
            self.screen.blit(menu_bg, (0, 0))

            if DEBUG_RECTANGLES:
                pygame.draw.rect(self.screen, (0,255,0), btn_normal_rect, 2)
                pygame.draw.rect(self.screen, (255,0,0), btn_hardcore_rect, 2)

            # bouton Normal
            txt_normal_main = font_big.render("▶ Jouer (Normal)", True, (255, 255, 255))
            txt_normal_sub  = font_sub.render("Visibilité totale", True, (200, 255, 200))
            self.screen.blit(txt_normal_main, txt_normal_main.get_rect(center=(btn_normal_rect.centerx, btn_normal_rect.centery - 10)))
            self.screen.blit(txt_normal_sub,  txt_normal_sub.get_rect(center=(btn_normal_rect.centerx, btn_normal_rect.centery + 15)))

            # bouton Hardcore
            txt_hard_main = font_big.render("🔥 Hardcore", True, (255, 180, 180))
            txt_hard_sub  = font_sub.render("Vision torche + pénombre", True, (255, 180, 180))
            self.screen.blit(txt_hard_main, txt_hard_main.get_rect(center=(btn_hardcore_rect.centerx, btn_hardcore_rect.centery - 10)))
            self.screen.blit(txt_hard_sub,  txt_hard_sub.get_rect(center=(btn_hardcore_rect.centerx, btn_hardcore_rect.centery + 15)))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.state = "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_normal_rect.collidepoint(event.pos):
                        self.hardcore = False
                        self.fade_transition(fade_in=False)
                        self._enter_game()
                        return
                    elif btn_hardcore_rect.collidepoint(event.pos):
                        self.hardcore = True
                        self.fade_transition(fade_in=False)
                        self._enter_game()
                        return

    def _enter_game(self):
        # on revient à la taille du donjon
        self.width  = self.cols * CELL_SIZE
        self.height = self.rows * CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🧱 Wall Is You — Playing")
        # (re)convertit les images pour le display actuel si besoin
        self.prepare_images()
        self.fade_transition(fade_in=True)
        self.state = "playing"

    # ----------- Écran de fin -----------
    def show_end_screen(self, msg, color):
        font = pygame.font.SysFont("arial", 48, bold=True)
        text = font.render(msg, True, color)

        button_font = pygame.font.SysFont("arial", 28)
        button_text = button_font.render("↻ Rejouer", True, (0, 0, 0))
        button_rect = pygame.Rect(self.width//2 - 90, self.height//2 + 100, 180, 50)

        while self.state in ("victory", "game_over"):
            self.screen.fill((0, 0, 0))
            self.screen.blit(text, text.get_rect(center=(self.width//2, self.height//2 - 50)))
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, border_radius=8)
            self.screen.blit(button_text, button_text.get_rect(center=button_rect.center))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "quit"; self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.prepare_images()
                        return

    # ----------- Boucle principale -----------
    def run(self):
        while self.running:
            if self.state == "menu":
                self.show_menu()

            elif self.state == "playing":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.handle_click(event.pos)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.play_turn()

                self.update_intention()
                self.render()
                self.clock.tick(FPS)

            elif self.state in ("victory", "game_over"):
                msg   = "🏆 Victoire ! Tous les dragons ont été vaincus 🎉" if self.state == "victory" else "💀 GAME OVER 💀"
                color = (0, 255, 0) if self.state == "victory" else (255, 0, 0)
                self.show_end_screen(msg, color)

        pygame.quit()


if __name__ == "__main__":
    WallIsYouPygame().run()