import pygame
import random
import os
import math
import json
from board import Board
from piece import Piece
from constants import *

HARD_DROP_TRAIL_COLOR = (180, 180, 255)
ACTIVE_PIECE_OUTLINE_COLOR = (255, 255, 255)

TIPS = [
    "¡Recuerda usar el hold (C) para guardar piezas!",
    "Limpia 4 líneas a la vez para un Tetris y más puntos.",
    "Los power-ups pueden cambiar el rumbo de la partida.",
    "¿Sabías que puedes cambiar el tema y el modo accesible en el menú?",
    "¡Intenta superar tu mejor combo de líneas!"
]

class Particle:
    def __init__(self, x, y, color, dx, dy, life, size):
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
        self.life = life
        self.size = size
        self.max_life = life

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        # Gravedad suave
        self.dy += 0.15

    def draw(self, surface):
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        surface.blit(s, (self.x, self.y))

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.music_muted = False
        self.effects_muted = False
        self.current_music = None
        self.stats = None
        self.config = None
        self.stats_screen = False
        self.tip = random.choice(TIPS)
        self.selected_theme = DEFAULT_THEME
        self.theme = THEMES[self.selected_theme]
        self.menu_option = 0
        self.state = "menu"
        self.high_score = 0
        self.sounds = None
        self.hard_drop_trail = []
        self.animated_bg_figures = []
        self.particles = []
        self.menu_transition = 0
        self.pause_transition = 0
        self.piece_pop_timer = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.highscore_flash_timer = 0
        self.accessibility_mode = 0
        self.game_mode = 0  # 0: Clásico, 1: Maratón, 2: Zen
        self.mode_names = ["Clásico", "Maratón", "Zen"]

        # Carga primero stats y config
        self.stats = self.load_stats()
        self.config = self.load_config()

        # Aplica config antes de cualquier otra cosa
        if self.config:
            self.selected_theme = self.config.get('theme', DEFAULT_THEME)
            self.theme = THEMES[self.selected_theme]
            self.music_muted = self.config.get('music_muted', False)
            self.effects_muted = self.config.get('effects_muted', False)
            self.accessibility_mode = self.config.get('accessibility_mode', 0)
            self.apply_accessibility()

        self.high_score = self.load_high_score()
        self.sounds = self.load_sounds()
        if self.sounds.get("music"):
            self.sounds["music"].play(loops=-1)

        self.reset_game()
        self.hard_drop_trail = []
        self.animated_bg_figures = self.generate_bg_figures()
        self.particles = []

    def load_high_score(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                try:
                    return int(f.read())
                except ValueError:
                    return 0
        return 0

    def save_high_score(self):
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(self.high_score))

    def load_sounds(self):
        sounds = {}
        for key, path in SOUNDS.items():
            if os.path.exists(path):
                if key.startswith("music"):
                    sounds[key] = path  # Guardar ruta, no cargar aún
                else:
                    sounds[key] = pygame.mixer.Sound(path)
            else:
                # Si no hay archivo, asignar None (no beep)
                sounds[key] = None
        return sounds

    def set_music(self, music_key):
        if self.current_music == music_key:
            return
        if music_key in self.sounds and self.sounds[music_key]:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.sounds[music_key])
            pygame.mixer.music.set_volume(0.4 if not self.music_muted else 0)
            pygame.mixer.music.play(-1)
            self.current_music = music_key
        # Si no hay archivo, simplemente no hace nada y el juego sigue funcionando.

    def play_sound(self, name):
        if name in self.sounds and not self.effects_muted and self.sounds[name]:
            try:
                self.sounds[name].play()
            except Exception:
                pass
            
    def reset_game(self):
        self.board = Board()
        self.current_piece = Piece()
        self.next_piece = Piece()
        self.held_piece = None
        self.can_swap_hold = True
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 0.8
        self.game_over = False
        # Time tracking
        self.game_start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.base_fall_speed = 0.8
        self.stats['games_played'] += 1
        self.save_stats()
        self.save_config()

    def update_speed(self):
        # Calculate time-based speed increase
        self.elapsed_time = (pygame.time.get_ticks() - self.game_start_time) / 1000  # in seconds
        time_speed_factor = min(0.6, self.elapsed_time / 60.0)  # Max 0.6 speed increase over 60 seconds
        level_speed_factor = min(0.4, (self.level - 1) * 0.05)
        total_speed_increase = time_speed_factor + level_speed_factor
        # Si hay slow_time activo, ralentiza
        if hasattr(self, 'slow_time_timer') and pygame.time.get_ticks() < self.slow_time_timer:
            self.fall_speed = max(0.1, self.base_fall_speed - total_speed_increase + 0.5)
        else:
            self.fall_speed = max(0.1, self.base_fall_speed - total_speed_increase)
        # Cambiar música según velocidad
        if self.fall_speed < 0.3:
            self.set_music('music_fast')
        else:
            self.set_music('music_slow')

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if self.state == "playing":
                self.run_game_loop(events)
            elif self.state == "menu":
                self.run_menu_loop(events)
            elif self.state == "game_over":
                self.run_game_over_loop(events)
            elif self.state == "paused":
                self.run_pause_loop(events)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        quit()
        
    def run_game_loop(self, events):
        self.update_bg_figures()
        self.fall_time += self.clock.get_rawtime()
        self.update_particles()

        # Si hay líneas para animar, solo animar y esperar
        if self.board.lines_to_clear:
            if self.board.clear_animation_timer < 6:  # 6 frames de animación
                self.board.animate_clear()
                self.draw()
                pygame.time.delay(60)  # Pequeña pausa para la animación
                return
            else:
                filas_eliminadas = list(self.board.lines_to_clear)
                cleared = self.board.clear_lines()
                if cleared > 0:
                    self.play_sound("clear")
                    self.lines += cleared
                    if self.game_mode != 2:
                        self.score += [0, 40, 100, 300, 1200][cleared] * self.level
                    self.level = self.lines // 10 + 1 if self.game_mode != 2 else 1
                    # Partículas de limpieza de línea
                    for row in filas_eliminadas:
                        self.spawn_line_clear_particles(row)
                    # Combo visual si se limpian 2+ líneas
                    if cleared >= 2:
                        self.spawn_combo_particles(filas_eliminadas)
                    # Probabilidad de power-up
                    if random.random() < 0.4 and self.game_mode != 2:
                        self.board.place_random_powerup()
                self.fall_time = 0

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_piece_left()
                elif event.key == pygame.K_RIGHT:
                    self.move_piece_right()
                elif event.key == pygame.K_DOWN:
                    self.move_piece_down()
                    self.fall_time = 0
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key == pygame.K_c:
                    self.hold_piece()
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.state = "paused"
                elif event.key == pygame.K_m:
                    self.toggle_mute()
                elif event.key == pygame.K_s:
                    self.stats_screen = not self.stats_screen
                elif event.key == pygame.K_r and self.stats_screen:
                    self.reset_stats()
                    self.reset_config()

        if self.fall_time / 1000 > self.fall_speed:
            self.fall_time = 0
            # Antes de mover hacia abajo, checar si hay líneas para limpiar
            if not self.board.lines_to_clear:
                self.move_piece_down()
                # Si hay líneas para limpiar, iniciar animación
                if self.board.check_lines_to_clear() > 0:
                    return

        self.update_speed()
        if self.game_mode != 2:
            self.check_powerup_collection()
        self.draw()

    def run_menu_loop(self, events):
        self.update_bg_figures()
        if self.menu_transition > 0:
            self.menu_transition -= 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.game_mode = (self.game_mode + 1) % len(self.mode_names)
                if event.key == pygame.K_RETURN:
                    self.selected_theme = THEME_LIST[self.menu_option]
                    self.theme = THEMES[self.selected_theme]
                    self.menu_transition = 20
                    self.state = "playing"
                    self.piece_pop_timer = 10
                if event.key == pygame.K_q:
                    self.state = "quit"
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_UP:
                    self.menu_option = (self.menu_option - 1) % len(THEME_LIST)
                if event.key == pygame.K_DOWN:
                    self.menu_option = (self.menu_option + 1) % len(THEME_LIST)
                if event.key == pygame.K_a:
                    self.accessibility_mode = (self.accessibility_mode + 1) % 3
                    self.apply_accessibility()
                if event.key == pygame.K_s:
                    self.stats_screen = not self.stats_screen
                if event.key == pygame.K_r and self.stats_screen:
                    self.reset_stats()
                    self.reset_config()
        if self.stats_screen:
            self.draw_stats_screen()
        else:
            self.draw_menu()

    def run_game_over_loop(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = "playing"
                if event.key == pygame.K_m:
                    self.reset_game()
                    self.state = "menu"
        
        self.draw_game_over()

    def run_pause_loop(self, events):
        if self.pause_transition < 20:
            self.pause_transition += 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.state = "playing"
                    self.pause_transition = 0
        self.draw_pause()

    def draw_text(self, text, size, color, x, y, center=False, font_name=None, right=False, bg=None):
        font = pygame.font.Font(font_name if font_name else pygame.font.get_default_font(), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        elif right:
            text_rect.topright = (x, y)
        else:
            text_rect.topleft = (x, y)
        if bg:
            bg_rect = text_rect.inflate(16, 8)
            s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            s.fill(bg)
            self.screen.blit(s, bg_rect.topleft)
        self.screen.blit(text_surface, text_rect)

    def draw_next_piece(self):
        self.draw_text("Next", 24, WHITE, WIDTH - 125, 50, center=True)
        shape = self.next_piece.shape
        start_x = WIDTH - 125 - (len(shape[0]) * GRID_SIZE) / 2
        start_y = 100
        self.draw_piece_preview(self.next_piece, start_x, start_y)

    def draw_held_piece(self):
        self.draw_text("Hold", 24, WHITE, 125, 50, center=True)
        if self.held_piece:
            shape = self.held_piece.shape
            start_x = 125 - (len(shape[0]) * GRID_SIZE) / 2
            start_y = 100
            self.draw_piece_preview(self.held_piece, start_x, start_y)
            
    def draw_piece_preview(self, piece, start_x, start_y):
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen, 
                        piece.color, 
                        (start_x + col_idx * GRID_SIZE, start_y + row_idx * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    )

    def draw_menu(self):
        self.update_bg_figures()
        self.screen.fill(self.theme['background'])
        self.draw_animated_bg()
        # Título
        self.draw_text("TETRIS", 80, MENU_TITLE_COLOR, WIDTH / 2, HEIGHT / 6, center=True)
        # Modo de juego
        self.draw_text(f"Modo: {self.mode_names[self.game_mode]} (Tab para cambiar)", 28, (60, 60, 200), WIDTH/2, HEIGHT/3 - 40, center=True)
        # Opciones principales
        self.draw_text("Press ENTER to Start", 32, MENU_OPTION_COLOR, WIDTH / 2, HEIGHT / 3, center=True)
        self.draw_text("Press Q to Quit", 32, MENU_OPTION_COLOR, WIDTH / 2, HEIGHT / 3 + 40, center=True)
        # High Score arriba a la derecha con fondo semitransparente y alineado a la derecha
        self.draw_text(f"High Score: {self.high_score}", 30, (255,255,0), WIDTH - 20, 20, right=True, bg=(0,0,0,180))
        # Panel de selección de tema
        panel_x = WIDTH / 2 - 150
        panel_y = HEIGHT / 2
        panel_w = 300
        panel_h = 60 + 40 * len(THEME_LIST)
        pygame.draw.rect(self.screen, (220, 220, 220), (panel_x, panel_y, panel_w, panel_h), border_radius=16)
        self.draw_text("Selecciona un tema:", 28, (60, 60, 60), WIDTH / 2, panel_y + 30, center=True)
        for idx, name in enumerate(THEME_LIST):
            color = MENU_OPTION_SELECTED_COLOR if idx == self.menu_option else (60, 60, 60)
            bg_rect = pygame.Rect(panel_x + 30, panel_y + 60 + idx * 40, panel_w - 60, 34)
            if idx == self.menu_option:
                pygame.draw.rect(self.screen, (255, 230, 230), bg_rect, border_radius=8)
            self.draw_text(name.capitalize(), 26, color, WIDTH / 2, panel_y + 77 + idx * 40, center=True)
        self.draw_text("S: Estadísticas", 22, (60,60,60), WIDTH/2, HEIGHT-90, center=True)
        self.draw_text("Accesibilidad: A para cambiar", 22, (60,60,60), WIDTH/2, HEIGHT-60, center=True)
        modo = ["Normal", "Alto Contraste", "Daltónico"][self.accessibility_mode]
        self.draw_text(f"Modo: {modo}", 22, (60,60,60), WIDTH/2, HEIGHT-35, center=True)
        self.draw_text(f"Tip: {self.tip}", 20, (80,80,80), WIDTH/2, HEIGHT-10, center=True)

    def draw_game_over(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", 80, RED, WIDTH / 2, HEIGHT / 4, center=True)
        self.draw_text(f"Your Score: {self.score}", 40, WHITE, WIDTH / 2, HEIGHT / 2, center=True)
        self.draw_text(f"Time: {self.format_time(self.elapsed_time)}", 35, WHITE, WIDTH / 2, HEIGHT / 2 + 40, center=True)
        self.draw_text(f"High Score: {self.high_score}", 30, SCORE_COLOR, WIDTH / 2, HEIGHT / 2 + 80, center=True)
        self.draw_text("Press ENTER to Play Again", 25, MENU_OPTION_COLOR, WIDTH / 2, HEIGHT * 0.75, center=True)
        self.draw_text("Press M to return to Menu", 25, MENU_OPTION_COLOR, WIDTH / 2, HEIGHT * 0.75 + 40, center=True)
        self.draw_text(f"Tip: {self.tip}", 22, (255,255,0), WIDTH/2, HEIGHT-30, center=True)

    def draw_pause(self):
        alpha = min(180, self.pause_transition*9)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,alpha))
        self.screen.blit(s, (0,0))
        font = pygame.font.Font(None, 80)
        text = font.render("PAUSA", True, MENU_TITLE_COLOR)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20 - self.pause_transition))
        self.screen.blit(text, text_rect)
        font2 = pygame.font.Font(None, 36)
        t2 = font2.render("Presiona P o ESC para continuar", True, WHITE)
        t2_rect = t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 40 + self.pause_transition))
        self.screen.blit(t2, t2_rect)

    def draw(self):
        self.update_bg_figures()
        self.screen.fill(self.theme['background'])
        self.draw_animated_bg()
        ox, oy = self.shake_offset
        game_surface = self.screen.subsurface(( (WIDTH-SCREEN_WIDTH)//2 + ox, (HEIGHT-SCREEN_HEIGHT)//2 + oy, SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.fill(BLACK)
        self.board.draw(game_surface, grid_color=self.theme['grid'])
        
        # Dibujar la pieza fantasma (ghost piece)
        ghost_y = self.current_piece.y
        while self.board.is_valid_move(self.current_piece, self.current_piece.x, ghost_y + 1):
            ghost_y += 1
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    px = (self.current_piece.x + col_idx) * GRID_SIZE
                    py = (ghost_y + row_idx) * GRID_SIZE
                    pygame.draw.rect(
                        game_surface,
                        self.theme['ghost'],
                        (px, py, GRID_SIZE, GRID_SIZE),
                        border_radius=6
                    )

        # Dibujar la pieza activa con borde brillante
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    px = (self.current_piece.x + col_idx) * GRID_SIZE
                    py = (self.current_piece.y + row_idx) * GRID_SIZE
                    color = self.theme['piece_colors'][self.current_piece.shape_name]
                    pygame.draw.rect(
                        game_surface,
                        color,
                        (px, py, GRID_SIZE, GRID_SIZE)
                    )
                    # Borde brillante
                    pygame.draw.rect(
                        game_surface,
                        ACTIVE_PIECE_OUTLINE_COLOR,
                        (px, py, GRID_SIZE, GRID_SIZE),
                        2
                    )
        
        # UI minimalista para Zen
        if self.game_mode == 2:
            # Ubico el texto a la derecha del tablero
            base_x = (WIDTH + SCREEN_WIDTH)//2 + 40
            base_y = (HEIGHT - SCREEN_HEIGHT)//2 + 100
            self.draw_text(f"Modo: Zen (Sin score, sin fin)", 28, (60, 200, 60), base_x, base_y, center=False)
            self.draw_text(f"Líneas: {self.lines}", 30, WHITE, base_x, base_y + 50, center=False)
            self.draw_text(f"Tiempo: {self.format_time(self.elapsed_time)}", 30, WHITE, base_x, base_y + 90, center=False)
        else:
            if self.game_mode == 1:
                self.draw_text(f"Modo: Maratón (Infinito)", 28, (60, 60, 200), WIDTH//2, 10, center=True)
            self.draw_text(f"Score: {self.score}", 30, WHITE, 125, HEIGHT - 120, center=True)
            self.draw_text(f"Lines: {self.lines}", 30, WHITE, 125, HEIGHT - 80, center=True)
            self.draw_text(f"Level: {self.level}", 30, WHITE, 125, HEIGHT - 40, center=True)
            self.draw_text(f"Time: {self.format_time(self.elapsed_time)}", 25, WHITE, 125, HEIGHT, center=True)
            self.draw_text(f"High Score: {self.high_score}", 25, SCORE_COLOR, WIDTH - 125, HEIGHT - 40, center=True)
        
        self.draw_next_piece()
        self.draw_held_piece()
        
        # Partículas
        self.draw_particles()
        # Combo text
        if hasattr(self, 'combo_text_timer') and self.combo_text_timer > 0:
            font = pygame.font.Font(None, 60)
            text = font.render("COMBO!", True, (255, 100, 100))
            x, y = self.combo_text_pos
            text_rect = text.get_rect(center=(x, y - (40 - self.combo_text_timer)))
            alpha = int(255 * (self.combo_text_timer / 40))
            s = pygame.Surface(text_rect.size, pygame.SRCALPHA)
            s.fill((0,0,0,0))
            s.blit(text, (0,0))
            s.set_alpha(alpha)
            self.screen.blit(s, text_rect.topleft)
            self.combo_text_timer -= 1
        
        # High Score flash
        if self.highscore_flash_timer > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((255,255,0, min(180, self.highscore_flash_timer*6)))
            self.screen.blit(s, (0,0))
            self.highscore_flash_timer -= 1
        
        # Pieza nueva pop
        if self.piece_pop_timer > 0:
            for row_idx, row in enumerate(self.current_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        px = (self.current_piece.x + col_idx) * GRID_SIZE + (WIDTH - SCREEN_WIDTH)//2 + ox
                        py = (self.current_piece.y + row_idx) * GRID_SIZE + (HEIGHT - SCREEN_HEIGHT)//2 + oy
                        scale = 1.0 + 0.2 * (self.piece_pop_timer/8)
                        rect = pygame.Rect(px, py, GRID_SIZE, GRID_SIZE)
                        rect.inflate_ip(GRID_SIZE*(scale-1), GRID_SIZE*(scale-1))
                        color = self.theme['piece_colors'][self.current_piece.shape_name]
                        pygame.draw.rect(self.screen, color, rect)
            self.piece_pop_timer -= 1
        
    def move_piece_left(self):
        if self.board.is_valid_move(self.current_piece, self.current_piece.x - 1, self.current_piece.y):
            self.current_piece.x -= 1

    def move_piece_right(self):
        if self.board.is_valid_move(self.current_piece, self.current_piece.x + 1, self.current_piece.y):
            self.current_piece.x += 1

    def move_piece_down(self):
        if self.board.is_valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
        else:
            self.lock_piece_with_effect()
            self.play_sound("drop")
            self.board.check_lines_to_clear()
            self.current_piece = self.next_piece
            self.next_piece = Piece()
            self.can_swap_hold = True
            self.piece_pop_timer = 8
            # SOLO en modo Zen: si la nueva pieza no cabe, libera la mitad superior del tablero
            if self.game_mode == 2 and not self.board.is_valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                # Libera la mitad superior
                for y in range(GRID_HEIGHT // 2):
                    for x in range(GRID_WIDTH):
                        self.board.grid[y][x] = BLACK
            elif self.game_mode != 2 and not self.board.is_valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                self.state = "game_over"
                self.play_sound("game_over")
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                    self.highscore_flash_timer = 40
                    self.play_sound("combo")

    def rotate_piece(self):
        # Create a temporary piece for rotation check
        temp_piece = Piece(self.current_piece.shape_name)
        temp_piece.shape = [list(row) for row in self.current_piece.shape]
        temp_piece.rotation = self.current_piece.rotation
        temp_piece.x = self.current_piece.x
        temp_piece.y = self.current_piece.y
        
        # Rotate the temporary piece
        temp_piece.shape = [list(row) for row in zip(*temp_piece.shape[::-1])]
        temp_piece.rotation = (temp_piece.rotation + 1) % 4
        
        if self.board.is_valid_move(temp_piece, temp_piece.x, temp_piece.y):
            self.current_piece.shape = temp_piece.shape
            self.current_piece.rotation = temp_piece.rotation
            self.play_sound("rotate")
        else: # Wall kick basic implementation
            # Try moving left
            if self.board.is_valid_move(temp_piece, temp_piece.x - 1, temp_piece.y):
                self.current_piece.x -= 1
                self.current_piece.shape = temp_piece.shape
                self.current_piece.rotation = temp_piece.rotation
                self.play_sound("rotate")
            # Try moving right
            elif self.board.is_valid_move(temp_piece, temp_piece.x + 1, temp_piece.y):
                self.current_piece.x += 1
                self.current_piece.shape = temp_piece.shape
                self.current_piece.rotation = temp_piece.rotation
                self.play_sound("rotate")
    
    def hard_drop(self):
        self.hard_drop_trail = []
        y = self.current_piece.y
        while self.board.is_valid_move(self.current_piece, self.current_piece.x, y + 1):
            y += 1
            self.hard_drop_trail.append((self.current_piece.x, y))
        self.current_piece.y = y
        self.draw()
        pygame.display.flip()
        pygame.time.delay(80)
        self.hard_drop_trail = []
        self.play_sound("hard_drop")
        self.move_piece_down()

    def hold_piece(self):
        if self.can_swap_hold:
            if self.held_piece is None:
                self.held_piece = Piece(self.current_piece.shape_name)
                self.current_piece = self.next_piece
                self.next_piece = Piece()
            else:
                self.current_piece, self.held_piece = self.held_piece, Piece(self.current_piece.shape_name)
            
            # Reset position for the new piece
            self.current_piece.x = GRID_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
            self.current_piece.y = 0

            # Check if the new piece is in a valid spot
            if not self.board.is_valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                # Swap back if it's not valid (should be rare)
                self.current_piece, self.held_piece = self.held_piece, self.current_piece
            else:
                self.can_swap_hold = False 

    def lock_piece_with_effect(self):
        original_y = self.current_piece.y
        # Rebote: sube y baja la pieza rápidamente
        for offset in [-1, 0, 1, 0]:
            self.current_piece.y = original_y + offset
            self.draw()
            pygame.display.flip()
            pygame.time.delay(40)
        self.current_piece.y = original_y
        # Pulso: destello blanco
        for _ in range(2):
            self.draw_piece_pulse(color=(255,255,255))
            pygame.display.flip()
            pygame.time.delay(40)
            self.draw()
            pygame.display.flip()
            pygame.time.delay(40)
        # Partículas de aterrizaje
        self.spawn_piece_land_particles(self.current_piece)
        # Finalmente bloquear la pieza
        self.board.lock_piece(self.current_piece)

    def draw_piece_pulse(self, color):
        self.screen.fill(GRAY)
        game_surface = self.screen.subsurface(( (WIDTH-SCREEN_WIDTH)//2, (HEIGHT-SCREEN_HEIGHT)//2, SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.fill(BLACK)
        self.board.draw(game_surface)
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    px = (self.current_piece.x + col_idx) * GRID_SIZE
                    py = (self.current_piece.y + row_idx) * GRID_SIZE
                    pygame.draw.rect(
                        game_surface,
                        color,
                        (px, py, GRID_SIZE, GRID_SIZE)
                    )
                    pygame.draw.rect(
                        game_surface,
                        ACTIVE_PIECE_OUTLINE_COLOR,
                        (px, py, GRID_SIZE, GRID_SIZE),
                        2
                    ) 

    def check_powerup_collection(self):
        # Verifica si la pieza actual recoge un power-up
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = self.current_piece.x + col_idx
                    y = self.current_piece.y + row_idx
                    tipo = self.board.get_powerup_at(x, y)
                    if tipo:
                        self.activate_powerup(tipo, x, y)
                        self.board.remove_powerup(x, y)

    def activate_powerup(self, tipo, x, y):
        if tipo == 'col_clear':
            for row in self.board.grid:
                row[x] = BLACK
            self.score += 100
            self.play_sound("powerup")
            self.spawn_powerup_particles(x, y, (255, 215, 0))
        elif tipo == 'slow_time':
            self.slow_time_timer = pygame.time.get_ticks() + 10000
            self.play_sound("powerup")
            self.spawn_powerup_particles(x, y, (0, 255, 255))
        elif tipo == 'bomb':
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        self.board.grid[ny][nx] = BLACK
            self.score += 150
            self.play_sound("powerup")
            self.spawn_powerup_particles(x, y, (255, 80, 80))
            self.shake_timer = 10

    def generate_bg_figures(self, n=12):
        # Genera figuras con posiciones, velocidades y tipo
        figures = []
        for _ in range(n):
            kind = random.choice(['circle', 'rect', 'line'])
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            size = random.randint(30, 80)
            color = self.theme['grid']
            figures.append({'kind': kind, 'x': x, 'y': y, 'dx': dx, 'dy': dy, 'size': size, 'color': color})
        return figures

    def update_bg_figures(self):
        for fig in self.animated_bg_figures:
            fig['x'] += fig['dx']
            fig['y'] += fig['dy']
            # Rebote en los bordes
            if fig['x'] < 0 or fig['x'] > WIDTH:
                fig['dx'] *= -1
            if fig['y'] < 0 or fig['y'] > HEIGHT:
                fig['dy'] *= -1
            # Oscilar color suavemente
            base = self.theme['grid']
            t = pygame.time.get_ticks() / 1000.0
            osc = int(40 * math.sin(t + fig['x'] + fig['y']))
            fig['color'] = tuple(min(255, max(0, c + osc)) for c in base)

    def draw_animated_bg(self):
        for fig in self.animated_bg_figures:
            if fig['kind'] == 'circle':
                pygame.draw.circle(self.screen, fig['color'], (int(fig['x']), int(fig['y'])), fig['size']//2, 2)
            elif fig['kind'] == 'rect':
                pygame.draw.rect(self.screen, fig['color'], (int(fig['x']), int(fig['y']), fig['size'], fig['size']), 2)
            elif fig['kind'] == 'line':
                angle = (pygame.time.get_ticks() / 1000.0) % (2*math.pi)
                x2 = int(fig['x'] + math.cos(angle) * fig['size'])
                y2 = int(fig['y'] + math.sin(angle) * fig['size'])
                pygame.draw.line(self.screen, fig['color'], (int(fig['x']), int(fig['y'])), (x2, y2), 2) 

    def toggle_mute(self):
        self.music_muted = not self.music_muted
        self.effects_muted = self.music_muted
        pygame.mixer.music.set_volume(0 if self.music_muted else 0.4) 

    def spawn_line_clear_particles(self, row_idx):
        # Genera partículas a lo largo de la fila eliminada
        for x in range(GRID_WIDTH):
            px = (x * GRID_SIZE) + (WIDTH - SCREEN_WIDTH)//2 + GRID_SIZE//2
            py = (row_idx * GRID_SIZE) + (HEIGHT - SCREEN_HEIGHT)//2 + GRID_SIZE//2
            for _ in range(6):
                dx = random.uniform(-2, 2)
                dy = random.uniform(-3, -1)
                color = (255, 255, 180)
                size = random.randint(3, 6)
                life = random.randint(18, 28)
                self.particles.append(Particle(px, py, color, dx, dy, life, size))

    def spawn_piece_land_particles(self, piece):
        # Partículas en la base de la pieza al aterrizar
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    px = (piece.x + col_idx) * GRID_SIZE + (WIDTH - SCREEN_WIDTH)//2 + GRID_SIZE//2
                    py = (piece.y + row_idx) * GRID_SIZE + (HEIGHT - SCREEN_HEIGHT)//2 + GRID_SIZE - 2
                    for _ in range(2):
                        dx = random.uniform(-1, 1)
                        dy = random.uniform(-2, -0.5)
                        color = (200, 200, 255)
                        size = random.randint(2, 4)
                        life = random.randint(10, 18)
                        self.particles.append(Particle(px, py, color, dx, dy, life, size))

    def spawn_powerup_particles(self, x, y, color):
        # Partículas al recoger un power-up
        px = x * GRID_SIZE + (WIDTH - SCREEN_WIDTH)//2 + GRID_SIZE//2
        py = y * GRID_SIZE + (HEIGHT - SCREEN_HEIGHT)//2 + GRID_SIZE//2
        for _ in range(12):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 3)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.randint(3, 6)
            life = random.randint(16, 24)
            self.particles.append(Particle(px, py, color, dx, dy, life, size))

    def spawn_combo_particles(self, row_idxs):
        # Partículas extra y texto animado para combos
        for row_idx in row_idxs:
            for _ in range(18):
                px = random.randint(0, GRID_WIDTH-1) * GRID_SIZE + (WIDTH - SCREEN_WIDTH)//2 + GRID_SIZE//2
                py = row_idx * GRID_SIZE + (HEIGHT - SCREEN_HEIGHT)//2 + GRID_SIZE//2
                dx = random.uniform(-2.5, 2.5)
                dy = random.uniform(-4, -1)
                color = (255, 100, 100)
                size = random.randint(4, 8)
                life = random.randint(22, 32)
                self.particles.append(Particle(px, py, color, dx, dy, life, size))
        # Texto animado
        self.combo_text_timer = 40
        self.combo_text_pos = (WIDTH//2, (row_idxs[0] + row_idxs[-1])//2 * GRID_SIZE + (HEIGHT - SCREEN_HEIGHT)//2)
        self.shake_timer = 12  # Activa vibración

    def update_particles(self):
        # Actualiza y elimina partículas muertas
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if self.shake_timer > 0:
            self.shake_offset = (random.randint(-6,6), random.randint(-6,6))
            self.shake_timer -= 1
        else:
            self.shake_offset = (0,0)

    def draw_particles(self):
        # Dibuja todas las partículas
        for p in self.particles:
            p.draw(self.screen) 

    def apply_accessibility(self):
        if self.accessibility_mode == 1:
            # Alto contraste
            self.theme = {
                **THEMES[self.selected_theme],
                'background': (0,0,0),
                'grid': (255,255,255),
                'piece_colors': {k: (255,255,255) for k in THEMES[self.selected_theme]['piece_colors']},
                'ghost': (255,255,0)
            }
        elif self.accessibility_mode == 2:
            # Daltónico (paleta amigable)
            self.theme = {
                **THEMES[self.selected_theme],
                'piece_colors': {
                    'I': (0, 255, 255),
                    'O': (255, 255, 0),
                    'T': (255, 0, 255),
                    'S': (0, 255, 0),
                    'Z': (255, 128, 0),
                    'J': (0, 0, 255),
                    'L': (128, 128, 128)
                },
                'ghost': (255,255,255)
            }
        else:
            self.theme = THEMES[self.selected_theme] 

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {
            'games_played': 0,
            'lines_cleared': 0,
            'tetrises': 0,
            'combos': 0,
            'max_combo': 0,
            'total_time': 0,
            'high_score': 0
        }

    def save_stats(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        data = {
            'theme': self.selected_theme,
            'music_muted': self.music_muted,
            'effects_muted': self.effects_muted,
            'accessibility_mode': self.accessibility_mode
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)

    def reset_stats(self):
        self.stats = {
            'games_played': 0,
            'lines_cleared': 0,
            'tetrises': 0,
            'combos': 0,
            'max_combo': 0,
            'total_time': 0,
            'high_score': 0
        }
        self.save_stats()

    def reset_config(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        self.config = {}
        self.save_config()

    def draw_stats_screen(self):
        self.screen.fill((30,30,30))
        self.draw_text("ESTADÍSTICAS", 60, (255,255,0), WIDTH/2, 60, center=True)
        y = 140
        self.draw_text(f"Partidas jugadas: {self.stats['games_played']}", 32, WHITE, WIDTH/2, y, center=True); y+=40
        self.draw_text(f"Líneas totales: {self.stats['lines_cleared']}", 32, WHITE, WIDTH/2, y, center=True); y+=40
        self.draw_text(f"Tetrises logrados: {self.stats['tetrises']}", 32, WHITE, WIDTH/2, y, center=True); y+=40
        self.draw_text(f"Combos máximos: {self.stats['max_combo']}", 32, WHITE, WIDTH/2, y, center=True); y+=40
        self.draw_text(f"Tiempo total jugado: {self.format_time(self.stats['total_time'])}", 32, WHITE, WIDTH/2, y, center=True); y+=40
        self.draw_text(f"High Score: {self.stats['high_score']}", 32, SCORE_COLOR, WIDTH/2, y, center=True); y+=40
        self.draw_text("R: Resetear estadísticas/configuración", 24, (255,100,100), WIDTH/2, HEIGHT-60, center=True)
        self.draw_text("S: Volver al menú", 24, (200,200,200), WIDTH/2, HEIGHT-30, center=True) 