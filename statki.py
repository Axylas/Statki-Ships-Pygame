import pygame
import json
import sys
import os
from pygame.locals import *
from assets.inc.components import Slider, CheckBox, Text, Button, InputBox, CheckBox_Effect, Slider_Effects
import math
import random
import uuid

def resource_path(nazwa_pliku):
    # Jeśli aplikacja jest "zamrożona" (skompilowana przez PyInstaller)
    if getattr(sys, 'frozen', False):
        # Pobierz ścieżkę do katalogu, w którym znajduje się skompilowany plik .exe
        biezacy_katalog = os.path.dirname(sys.executable)
    else:
        # Pobierz ścieżkę do katalogu, w którym znajduje się aktualnie uruchamiany skrypt
        biezacy_katalog = os.path.dirname(os.path.abspath(__file__))
    
    # Połącz ścieżkę katalogu z nazwą pliku
    return os.path.join(biezacy_katalog, nazwa_pliku)

# Ścieżki - uwzględniające czy skompilowany program
# Tła
bgimage = resource_path("assets/images/b.jpg")
bginfo = resource_path("assets/images/b_info.jpg")
bglevel = resource_path("assets/images/b2.jpg")
bgsetup = resource_path("assets/images/b3.jpg")
bgsettings = resource_path("assets/images/b4.jpg")
bggame = resource_path("assets/images/b5.jpg")
bgwin = resource_path("assets/images/win.jpg")
bglose = resource_path("assets/images/lose.jpg")

# Statki
ship = resource_path("assets/images/ships/ship")
broken_ship = resource_path("assets/images/ships/ship")
# Chybienie
miss_photo = resource_path("assets/images/miss.png")

# Ikonka
icon = resource_path("assets/images/icon.png")

# Pliki Dźwiękowe
# Muzyka
music1 = resource_path('assets/music/background_music_1.mp3')
music2 = resource_path('assets/music/background_music_2.mp3')
music3 = resource_path('assets/music/background_music_3.mp3')
music4 = resource_path('assets/music/background_music_4.mp3')
music5 = resource_path('assets/music/background_music_5.mp3')

# Dźwięki
# Strzał
hit_sound1 = resource_path('assets/music/effects/hit1.mp3')
hit_sound2 = resource_path('assets/music/effects/hit2.mp3')
hit_sound3 = resource_path('assets/music/effects/hit3.mp3')
# Chybienie
miss_sound1 = resource_path('assets/music/effects/miss1.mp3')
miss_sound2 = resource_path('assets/music/effects/miss2.mp3')
miss_sound3 = resource_path('assets/music/effects/miss3.mp3')
# Zatopienie
sunk_sound1 = resource_path('assets/music/effects/sunk1.mp3')
sunk_sound2 = resource_path('assets/music/effects/sunk2.mp3')
esteregg1 = resource_path("assets/music/effects/jacksparrow1.mp3")
esteregg2 = resource_path("assets/music/effects/jacksparrow2.mp3")
button_sound = resource_path("assets/music/button.mp3")

# Czcionki
font1 = resource_path("assets/settings/fonts/BlackRose.ttf")
font2 = resource_path("assets/settings/fonts/JackPirate.ttf")

# Pliki json
settings_path = resource_path('assets/settings/settings.json')
savegame_path = resource_path('assets/player/savegame.json')

hit_sounds = [hit_sound1, hit_sound2, hit_sound3]
miss_sounds = [miss_sound1, miss_sound2, miss_sound3]
sunk_sounds = [sunk_sound1, sunk_sound2]


pygame.init()

# Rozmiary ekranu
WIDTH = 1920
HEIGHT = 1080
CELL_SIZE = 60
GRID_ORIGIN_X, GRID_ORIGIN_Y = 500, 130  # Punkt początkowy dla planszy

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bitwa Morska")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (70, 70, 70)
LIGHT_GRAY = (200, 200, 200)
HOVER_COLOR = (150, 150, 150)
NAVY = (0, 0, 128)
RED = (255, 0, 0)
SEA_COLOR = (106, 160, 204, 128)
SEA_COLOR2 = (77, 116, 148, 128)
GREEN = (25, 148, 30)

# Ładowanie tła
bg_image = pygame.image.load(bgimage)
b_info = pygame.image.load(bginfo)
bg_image2 = pygame.image.load(bglevel)
bg_image3 = pygame.image.load(bgsetup)
bg_image4 = pygame.image.load(bgsettings)
bg_image5 = pygame.image.load(bggame)
bg_image_win = pygame.image.load(bgwin)
bg_image_lose = pygame.image.load(bglose)

# Ładowanie ustawień z pliku
with open(settings_path, 'r') as f:
    settings = json.load(f)

playlist = [music1, music2, music3, music4, music5]
current_track = 0
def play_music():
    global current_track
    pygame.mixer.music.load(playlist[current_track])
    pygame.mixer.music.play()
    current_track = (current_track + 1) % len(playlist)

play_music()  # Rozpoczęcie odtwarzania pierwszego utworu
pygame.mixer.music.set_endevent(pygame.USEREVENT)
pygame.mixer.music.set_volume(settings['music_volume'])

if not settings['music_on']:
    pygame.mixer.music.pause()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)


class LoadingScreen:
    def __init__(self, win):
        self.win = win
        self.font = pygame.font.Font(font1, 36)
        self.sequences = [
            "Projekt opracowany na potrzeby studiów.\nAutor: Krzysztof Ambroziak\nII Rok Studia Niestacjonarne, Informatyka", 
            "Bitwa Morska: Na Karaibach"
        ]
        self.current_sequence = 0
        self.timer = 0
        self.fade_timer = 0
        self.glow_surface = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)

    def draw_glow(self, x, y, radius):
        pygame.draw.circle(self.glow_surface, (0, 0, 0, 51), (x, y), radius)

    def display(self):
        self.win.fill((0, 0, 0))

        lines = self.sequences[self.current_sequence].split('\n')
        total_height = len(lines) * self.font.get_linesize() + 100
        start_y = HEIGHT // 2 - total_height // 2

        # Rysowanie tekstu z płynną animacją falowania
        for i, line in enumerate(lines):
            y_offset = math.sin(pygame.time.get_ticks() / 200 + i) * 3
            text = self.font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 4 + 300, start_y + i * self.font.get_linesize() + y_offset))
            self.win.blit(text, text_rect)

        # Efekt fade
        if self.fade_timer < 1000:
            alpha = (1 - self.fade_timer / 1000.0) * 255
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            self.win.blit(fade_surface, (0, 0))

    def update(self, dt):
        self.timer += dt
        self.fade_timer += dt

        if self.timer > 4000:  # Czas trwania każdej sekwencji
            self.timer = 0
            self.fade_timer = 0
            self.current_sequence += 1
            if self.current_sequence >= len(self.sequences):
                self.current_sequence = 0
                return True
        return False
    
    def skip_or_advance_sequence(self):
        self.current_sequence += 1
        if self.current_sequence >= len(self.sequences):
            self.current_sequence = 0
            return True
        else:
            self.timer = 0
            self.fade_timer = 0
            return False




class Board:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 20, bold=True)  # Czcionka z pogrubieniem
        self.grid = [[None for _ in range(10)] for _ in range(10)]
        self.sea_image = pygame.image.load("assets/images/water.png")
        self.sea_image_scaled = pygame.transform.scale(self.sea_image, (CELL_SIZE, CELL_SIZE))

    def draw(self, surface):
        for x in range(10):
            for y in range(10):
                rect = pygame.Rect(GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                surface.blit(self.sea_image_scaled, rect.topleft)
                pygame.draw.rect(surface, WHITE, rect, 1)

        # Rysowanie oznaczeń literowych i numerycznych
        for i in range(10):
            letter = chr(65 + i)  # Litery A-J
            number = str(i + 1)  # Numery 1-10
            letter_text = self.font.render(letter, True, WHITE)
            number_text = self.font.render(number, True, WHITE)
            # Dodanie poświaty
            letter_shadow = self.font.render(letter, True, BLACK)
            number_shadow = self.font.render(number, True, BLACK)
            surface.blit(letter_shadow, (GRID_ORIGIN_X + i * CELL_SIZE + 12, GRID_ORIGIN_Y - 30))
            surface.blit(number_shadow, (GRID_ORIGIN_X - 30, GRID_ORIGIN_Y + i * CELL_SIZE + 10))
            surface.blit(letter_text, (GRID_ORIGIN_X + i * CELL_SIZE + 10, GRID_ORIGIN_Y - 30))
            surface.blit(number_text, (GRID_ORIGIN_X - 30, GRID_ORIGIN_Y + i * CELL_SIZE + 10))

    def draw_board(self, surface, board_data, offset_x, offset_y, ships=None):
        scaled_miss_image = self.load_miss_image()
        for x in range(10):
            for y in range(10):
                rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                surface.blit(self.sea_image_scaled, rect.topleft)
                pygame.draw.rect(surface, WHITE, rect, 1)

                # Rysowanie oznaczeń trafień i pudłów
                if board_data[x][y] == 'H':
                    if ships and not self.is_part_of_sunken_ship(x, y, ships):
                        pygame.draw.circle(surface, RED, rect.center, CELL_SIZE // 2)
                elif board_data[x][y] == 'M':
                    surface.blit(scaled_miss_image, rect.topleft)

        # Rysowanie oznaczeń literowych i numerycznych
        for i in range(10):
            letter = chr(65 + i)  # Litery A-J
            number = str(i + 1)  # Numery 1-10
            letter_text = self.font.render(letter, True, WHITE)
            number_text = self.font.render(number, True, WHITE)
            # Dodanie poświaty
            letter_shadow = self.font.render(letter, True, BLACK)
            number_shadow = self.font.render(number, True, BLACK)
            surface.blit(letter_shadow, (GRID_ORIGIN_X + i * CELL_SIZE + 12, GRID_ORIGIN_Y - 30))
            surface.blit(number_shadow, (GRID_ORIGIN_X - 30, GRID_ORIGIN_Y + i * CELL_SIZE + 10))
            surface.blit(letter_text, (GRID_ORIGIN_X + i * CELL_SIZE + 10, GRID_ORIGIN_Y - 30))
            surface.blit(number_text, (GRID_ORIGIN_X - 30, GRID_ORIGIN_Y + i * CELL_SIZE + 10))

    def load_miss_image(self):
        # Załaduj obrazek z dysku
        miss_image = pygame.image.load(miss_photo)

        # Skaluj obrazek do rozmiaru komórki
        scaled_miss_image = pygame.transform.scale(miss_image, (CELL_SIZE, CELL_SIZE))

        return scaled_miss_image
    
    def is_part_of_sunken_ship(self, x, y, ships):
        for ship in ships:
            if ship.is_sunk():
                if (x, y) in ship.get_segments():
                    return True
        return False

class ShipShow:
    def __init__(self, length, x, y):
        self.length = length
        self.rect = pygame.Rect(x, y, length * CELL_SIZE, CELL_SIZE)
        try:
            self.image = pygame.image.load(f"{ship}{length}c.png")
            self.image = pygame.transform.scale(self.image, (self.rect.height, self.rect.width))  # Skalowanie
            self.image = pygame.transform.rotate(self.image, -90)  # Obracanie obrazka o 90 stopni w lewo
        except pygame.error:
            self.image = None

    def draw(self, surface, count):
        if self.image:
            surface.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(surface, DARK_GRAY, self.rect)

        count_text = Text(f'x{count}', self.rect.x + self.rect.width + 10, self.rect.y + self.rect.height / 2)
        count_text.display(surface)

class Ship:
    def __init__(self, length, x, y, is_new=True):
        self.id = str(uuid.uuid4())
        self.length = length
        self.horizontal = True
        self.rect = pygame.Rect(x, y, length * CELL_SIZE, CELL_SIZE)
        self.color = GREEN
        self.sunk_color = RED
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_new = is_new
        self.collided = False
        self.segments_hit = [False] * length 
        self.rotated = False

        # Ładowanie zdjęć statków
        try:
            self.image = pygame.image.load(f"{ship}{length}c.png")
            self.broken_image = pygame.image.load(f"{broken_ship}{length}c_broken.png")  # Nowa grafika dla zatopionego statku
        except pygame.error:
            self.image = None
            self.broken_image = None

    def draw(self, surface):
        # Utworzenie powierzchni z przeźroczystością dla tła statku
        ship_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        if self.is_sunk():
            ship_surface.fill((self.sunk_color[0], self.sunk_color[1], self.sunk_color[2], 51))  # 80% przeźroczystość
        else:
            ship_surface.fill((self.color[0], self.color[1], self.color[2], 51))  # 80% przeźroczystość

        current_image = self.broken_image if self.is_sunk() else self.image

        if current_image:
            # Obróć obrazek o 90 stopni w lewo tylko, gdy statek jest poziomy
            if self.horizontal:
                ship_image = pygame.transform.rotate(current_image, -90)
                ship_image = pygame.transform.scale(ship_image, (self.rect.width, self.rect.height))
            else:
                ship_image = pygame.transform.scale(current_image, (self.rect.width, self.rect.height))

            ship_surface.blit(ship_image, (0, 0))  # Nakładanie zdjęcia na powierzchnię statku

        if self.collided:
            # Nakładanie czerwonej warstwy w przypadku kolizji
            red_overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 128))  # 50% przeźroczystości
            ship_surface.blit(red_overlay, (0, 0))

        # Rysowanie całego statku na głównej powierzchni
        surface.blit(ship_surface, self.rect.topleft)

    def handle_event(self, event, board_rect, other_ships):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1 and not self.dragging:  # LPM
                    self.dragging = True
                    mouse_x, mouse_y = event.pos
                    self.drag_offset_x = self.rect.x - mouse_x
                    self.drag_offset_y = self.rect.y - mouse_y
                elif event.button == 3 and not self.rotated:  # PPM - obrót statku
                    self.horizontal = not self.horizontal
                    self.rect.size = self.rect.size[::-1]
                    self.ensure_on_board(board_rect)
                    self.rotated = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.rotated = False
            if self.dragging:
                self.dragging = False
                self.snap_to_grid(board_rect)
                self.ensure_on_board(board_rect)

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            new_x = mouse_x + self.drag_offset_x
            new_y = mouse_y + self.drag_offset_y
            self.rect.topleft = (new_x, new_y)


        # Sprawdzenie kolizji z innymi statkami
        for other_ship in other_ships:
            if other_ship != self and self.rect.colliderect(other_ship.rect):
                self.collided = True
                break
        else:
            self.collided = False

    def snap_to_grid(self, board_rect):
        # Dopasowanie statku do najbliższej kratki na planszy
        self.rect.x = round((self.rect.x - board_rect.x) / CELL_SIZE) * CELL_SIZE + board_rect.x
        self.rect.y = round((self.rect.y - board_rect.y) / CELL_SIZE) * CELL_SIZE + board_rect.y

    def ensure_on_board(self, board_rect):
        # Zapewnienie, że statek nie wyjdzie poza planszę
        if self.horizontal:
            max_x = board_rect.right - self.rect.width
            self.rect.x = min(max(self.rect.x, board_rect.x), max_x)

            # Ograniczenie Y do granic planszy
            max_y = board_rect.bottom - CELL_SIZE
            self.rect.y = min(max(self.rect.y, board_rect.y), max_y)
        else:
            max_y = board_rect.bottom - self.rect.height
            self.rect.y = min(max(self.rect.y, board_rect.y), max_y)

            # Ograniczenie X do granic planszy
            max_x = board_rect.right - CELL_SIZE
            self.rect.x = min(max(self.rect.x, board_rect.x), max_x)

    def is_valid_placement(self, other_ships):
        for other_ship in other_ships:
            if other_ship != self and self.rect.colliderect(other_ship.rect):
                return False
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'length': self.length,
            'x': self.rect.x,
            'y': self.rect.y,
            'horizontal': self.horizontal,
            'is_new': self.is_new
        }
    
    @staticmethod
    def from_dict(data, board_rect):
        ship = Ship(data['length'], data['x'], data['y'], data.get('is_new', True))
        ship.id = data['id']
        ship.horizontal = data['horizontal']
        if ship.horizontal:
            ship.rect.width, ship.rect.height = ship.length * CELL_SIZE, CELL_SIZE
        else:
            ship.rect.width, ship.rect.height = CELL_SIZE, ship.length * CELL_SIZE
        ship.ensure_on_board(board_rect)
        ship.snap_to_grid(board_rect)
        return ship
    
    def get_segments(self):
        segments = []
        for i in range(self.length):
            x = (self.rect.x - GRID_ORIGIN_X) // CELL_SIZE
            y = (self.rect.y - GRID_ORIGIN_Y) // CELL_SIZE
            if self.horizontal:
                segments.append((x + i, y))
            else:
                segments.append((x, y + i))
        return segments
    
    def hit_segment(self, segment):
        # Oznaczamy trafiony segment
        self.segments_hit[segment] = True

    def is_sunk(self):
        return all(self.segments_hit)


            

class Game:
    def __init__(self, player_ships=None, difficulty=None, menu=None):
        if player_ships is None and difficulty is None and menu is not None:
            # Wczytywanie gry
            self.load_game()
            self.menu = menu
        else:
            # Nowa gra
            self.player_ships = player_ships or []
            self.difficulty = difficulty
            self.computer_ships = self.generate_computer_ships()
            self.player_board = [['' for _ in range(10)] for _ in range(10)]
            self.computer_board = [['' for _ in range(10)] for _ in range(10)]
            self.current_turn = 'player'
            self.computer_hits = []  # Lista trafień komputera
            self.computer_misses = []  # Lista chybień komputera
            self.target_mode = False  # Czy komputer jest w "trybie celowania"
            self.consecutive_misses = 0
            self.menu = menu
            self.active_player_ships = list(player_ships)  # Kopia listy statków gracza
            self.active_computer_ships = list(self.computer_ships)  # Kopia listy statków komputera
            

        # Wczytywanie ustawień
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        self.effect_volume = settings['effect_volume']
        self.effect_on = settings['effect_on']
        if self.effect_on:
            self.sound_hit = pygame.mixer.Sound(random.choice(hit_sounds))
            self.sound_miss = pygame.mixer.Sound(random.choice(miss_sounds))
            self.sound_sunk = pygame.mixer.Sound(random.choice(sunk_sounds))
            pygame.mixer.Sound.set_volume(self.sound_hit, self.effect_volume)
            pygame.mixer.Sound.set_volume(self.sound_miss, self.effect_volume)
            pygame.mixer.Sound.set_volume(self.sound_sunk, self.effect_volume)
        self.save_game_button = Button("Zapisz", 600, 750, 200, 50, action=self.save_game, font=font2, sound=button_sound)
        self.button_main_menu = Button("Wyjdź", 850, 750, 200, 50, action=self.main_menu, font=font2, sound=button_sound)

    def generate_computer_ships(self):
        computer_ships = []
        ship_lengths = [5, 4, 3, 2, 2, 1, 1]  # Zaktualizowana lista długości statków

        for length in ship_lengths:
            placed = False
            while not placed:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                horizontal = random.choice([True, False])

                new_ship = Ship(length, GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y + y * CELL_SIZE)
                new_ship.horizontal = horizontal
                if horizontal:
                    new_ship.rect.width, new_ship.rect.height = length * CELL_SIZE, CELL_SIZE
                else:
                    new_ship.rect.width, new_ship.rect.height = CELL_SIZE, length * CELL_SIZE

                # Sprawdzenie, czy statek jest na planszy i nie koliduje z innymi
                if new_ship.rect.right <= GRID_ORIGIN_X + 10 * CELL_SIZE and \
                new_ship.rect.bottom <= GRID_ORIGIN_Y + 10 * CELL_SIZE and \
                new_ship.is_valid_placement(computer_ships):
                    computer_ships.append(new_ship)
                    placed = True

        return computer_ships


    def player_turn(self, x, y):
        if self.computer_board[x][y] == '':
            self.check_hit(x, y, self.computer_ships, self.computer_board)
            self.display_board_after_shot('player')
            pygame.time.wait(1500)
            self.next_turn()

    def computer_turn(self):
        # Logika dla poszczególnych poziomów trudności (Łatwy, Średni, Trudny)
        self.computer_make_shot()
        self.display_board_after_shot('computer')
        pygame.time.wait(1500)
        self.next_turn()

    def computer_make_shot(self):
        # Wybieranie odpowiedniej metody strzelania w zależności od poziomu trudności
        if self.difficulty == 'Łatwy':
            self.computer_turn_easy()
        elif self.difficulty == 'Średni':
            self.computer_turn_medium()
        elif self.difficulty == 'Trudny':
            self.computer_turn_hard()
        
    def computer_turn_easy(self):
        # Sprawdzenie, czy są dostępne kraty do strzelania
        if not self.are_targets_available():
            # Jeśli nie ma dostępnych krat, kończ turę
            return None

        while True:
            x, y = random.randint(0, 9), random.randint(0, 9)
            # Sprawdzenie czy kratka jest na planszy i czy nie była celem strzału
            if 0 <= x < 10 and 0 <= y < 10 and (x, y) not in self.computer_hits and (x, y) not in self.computer_misses:
                return self.check_hit(x, y, self.player_ships, self.player_board)



    def computer_turn_medium(self):
        if self.target_mode and self.are_targets_available():
            return self.focus_fire()
        else:
            return self.computer_turn_easy()



    def computer_turn_hard(self):
        if self.target_mode and self.are_targets_available():
            return self.focus_fire()
        else:
            return self.advanced_shooting_strategy()
        
    def are_targets_available(self):
        # Sprawdzenie, czy są dostępne kraty do strzelania
        for x in range(10):
            for y in range(10):
                if (x, y) not in self.computer_hits and (x, y) not in self.computer_misses:
                    return True
        return False

    def focus_fire(self):
        if not self.computer_hits:
            return self.computer_turn_easy()

        # Znalezienie wszystkich kierunków, w których można kontynuować strzał
        last_hit = self.computer_hits[-1]
        potential_targets = []

        # Sprawdzanie, czy w linii są kolejne trafienia
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            new_x, new_y = last_hit[0] + dx, last_hit[1] + dy
            if 0 <= new_x < 10 and 0 <= new_y < 10 and (new_x, new_y) not in self.computer_hits and (new_x, new_y) not in self.computer_misses:
                potential_targets.append((new_x, new_y))

        # Wybieranie najlepszego celu
        if potential_targets:
            return self.check_hit(*random.choice(potential_targets), self.player_ships, self.player_board)
        else:
            return self.computer_turn_easy()


    def sort_targets_by_probability(self, targets):
        # Sortowanie potencjalnych celów na podstawie ich prawdopodobieństwa trafienia
        sorted_targets = []
        for target in targets:
            if self.is_high_probability_target(target):
                sorted_targets.append(target)
        return sorted_targets + [target for target in targets if target not in sorted_targets]

    def is_high_probability_target(self, target):
        x, y = target
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            adjacent = (x + dx, y + dy)
            if adjacent in self.computer_hits:
                opposite = (x - dx, y - dy)
                if 0 <= opposite[0] < 10 and 0 <= opposite[1] < 10:
                    if opposite not in self.computer_hits and opposite not in self.computer_misses:
                        # Sprawdzanie czy na przeciwległym końcu trafienia jest wolne miejsce
                        return True
                continue

            # Sprawdzanie czy są dwa trafienia w linii z wolnym miejscem po obu stronach
            next_adjacent = (x + 2*dx, y + 2*dy)
            if next_adjacent in self.computer_hits:
                opposite = (x - dx, y - dy)
                next_opposite = (x + 3*dx, y + 3*dy)
                if 0 <= opposite[0] < 10 and 0 <= opposite[1] < 10 and \
                0 <= next_opposite[0] < 10 and 0 <= next_opposite[1] < 10:
                    if opposite not in self.computer_hits and opposite not in self.computer_misses and \
                    next_opposite not in self.computer_hits and next_opposite not in self.computer_misses:
                        # Sprawdzanie wolnych miejsc na obu końcach linii trafień
                        return True
        return False


    def find_closest_free_spot(self):
        last_hit = self.computer_hits[-1]
        # Szukanie najbliższego wolnego miejsca na planszy
        for distance in range(1, 10):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    x, y = last_hit[0] + dx, last_hit[1] + dy
                    if 0 <= x < 10 and 0 <= y < 10 and (x, y) not in self.computer_hits and (x, y) not in self.computer_misses:
                        return self.check_hit(x, y, self.player_ships, self.player_board)
        # W przypadku braku wolnych miejsc, powrót do losowego strzelania
        return self.computer_turn_easy()

            
    def advanced_shooting_strategy(self):
        most_promising_target = None
        highest_score = -1

        for x in range(10):
            for y in range(10):
                if (x, y) not in self.computer_hits and (x, y) not in self.computer_misses:
                    score = self.calculate_target_score(x, y)
                    if score > highest_score:
                        highest_score = score
                        most_promising_target = (x, y)
        
        if most_promising_target:
            return self.check_hit(most_promising_target[0], most_promising_target[1], self.player_ships, self.player_board)
        else:
            return self.computer_turn_easy()  # Revert to easy mode if no promising target
            
    def calculate_target_score(self, x, y):
        score = 0
        remaining_ship_lengths = self.get_remaining_ship_lengths()

        # Preferuj kratki, które mogą pomieścić pozostałe statki
        for length in remaining_ship_lengths:
            if self.can_accommodate_ship(x, y, length):
                score += 1

        # Dodaj punkty za sąsiedztwo z dotychczasowymi trafieniami
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (x + dx, y + dy) in self.computer_hits:
                score += 2

        return score
    
    def get_remaining_ship_lengths(self):
        # Zwróć listę długości pozostałych statków
        remaining_lengths = []
        for ship in self.active_player_ships:
            if not ship.is_sunk():
                remaining_lengths.append(ship.length)
        return remaining_lengths

    def can_accommodate_ship(self, x, y, length):
        # Sprawdź, czy statek o danej długości może być umieszczony w danej lokalizacji
        for dx, dy in [(1, 0), (0, 1)]:
            fit = True
            for i in range(length):
                nx, ny = x + i*dx, y + i*dy
                if nx >= 10 or ny >= 10 or (nx, ny) in self.computer_hits or (nx, ny) in self.computer_misses:
                    fit = False
                    break
            if fit:
                return True
        return False




    def check_hit(self, x, y, ships, board):
        hit = False
        hit_ship = None

        for ship in ships:
            if ship.rect.collidepoint((GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y + y * CELL_SIZE)):
                hit = True
                hit_ship = ship
                break

        board[x][y] = 'H' if hit else 'M'

        if hit:
            if self.current_turn == 'computer':
                self.computer_hits.append((x, y))
                self.target_mode = True
                self.consecutive_misses = 0
            if self.effect_on and not hit_ship.is_sunk():
                self.play_hit_sound()

            segment_index = hit_ship.get_segments().index((x, y))
            hit_ship.hit_segment(segment_index)
            if hit and hit_ship.is_sunk():
                if self.current_turn == 'player':
                    self.active_computer_ships = [s for s in self.active_computer_ships if s.id != hit_ship.id]
                    if self.effect_on:
                        self.play_hit_sound(volume_reduction=(hit_ship.length == 5))
                        self.play_sunk_sound(ship_length=hit_ship.length)
                else:
                    self.active_player_ships = [s for s in self.active_player_ships if s.id != hit_ship.id]
                    if self.effect_on:
                        self.play_hit_sound(volume_reduction=(hit_ship.length == 5))
                        self.play_sunk_sound(ship_length=hit_ship.length)


        else:
            self.computer_misses.append((x, y))
            if self.target_mode:
                self.consecutive_misses += 1
                if self.consecutive_misses >= 3:
                    self.target_mode = False
                    self.consecutive_misses = 0
            if self.effect_on:
                self.play_miss_sound()

        return hit

    def play_hit_sound(self, volume_reduction=False):
        if self.effect_on:
            sound_hit = pygame.mixer.Sound(random.choice(hit_sounds))
            volume = self.effect_volume * 0.2 if volume_reduction else self.effect_volume
            pygame.mixer.Sound.set_volume(sound_hit, volume)
            sound_hit.play()

    def play_miss_sound(self):
        if self.effect_on:
            sound_miss = pygame.mixer.Sound(random.choice(miss_sounds))
            pygame.mixer.Sound.set_volume(sound_miss, self.effect_volume)
            sound_miss.play()

    def play_sunk_sound(self, ship_length=0):
        if self.effect_on:
            if ship_length == 5 and self.current_turn == 'player':
                special_sound = pygame.mixer.Sound(esteregg1)
                pygame.mixer.Sound.set_volume(special_sound, self.effect_volume)
                special_sound.play()
            elif ship_length == 5 and self.current_turn == 'computer':
                special_sound = pygame.mixer.Sound(esteregg2)
                pygame.mixer.Sound.set_volume(special_sound, self.effect_volume)
                special_sound.play()
            else:
                sound_sunk = pygame.mixer.Sound(random.choice(sunk_sounds))
                pygame.mixer.Sound.set_volume(sound_sunk, self.effect_volume)
                sound_sunk.play()



        

    def get_adjacent_coordinates(self, coordinate):
        # Zwraca listę sąsiednich koordynatów
        x, y = coordinate
        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(x, y) for x, y in adjacent if 0 <= x < 10 and 0 <= y < 10]

    def is_promising_target(self, x, y):
        # Bardziej zaawansowana heurystyka dla poziomu "Trudny"
        if (x, y) in self.computer_hits or (x, y) in self.computer_misses:
            return False

        # Zwiększenie prawdopodobieństwa strzelania w pobliżu ostatniego trafienia
        if self.target_mode and self.computer_hits:
            last_hit = self.computer_hits[-1]
            if abs(x - last_hit[0]) <= 1 and abs(y - last_hit[1]) <= 1:
                return True

        # Unikanie strzelania w miejsca już sprawdzone
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if 0 <= x + dx < 10 and 0 <= y + dy < 10:
                if (x + dx, y + dy) in self.computer_misses:
                    return False
        return True

    def check_winner(self):
        # Sprawdzenie, czy któryś z graczy zatopił wszystkie statki przeciwnika
        player_hits = sum(row.count('H') for row in self.computer_board)
        computer_hits = sum(row.count('H') for row in self.player_board)

        if player_hits >= 18:  # Gracz zatopił wszystkie statki komputera
            return 'player'
        elif computer_hits >= 18:  # Komputer zatopił wszystkie statki gracza
            return 'computer'
        return None

    def next_turn(self):
        # Sprawdzenie zwycięzcy
        winner = self.check_winner()
        if winner:
            self.end_game(winner)
            print(f"Wygrał : {winner}")
            return

        # Zmiana tury
        self.current_turn = 'computer' if self.current_turn == 'player' else 'player'


    def update(self, event):
        if self.current_turn == 'player':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = (mouse_x - GRID_ORIGIN_X) // CELL_SIZE, (mouse_y - GRID_ORIGIN_Y) // CELL_SIZE
                if 0 <= grid_x < 10 and 0 <= grid_y < 10:
                    self.player_turn(grid_x, grid_y)
        elif self.current_turn == 'computer':
            pygame.time.wait(1500)  # Zmniejszono opóźnienie na 1 sekundę dla lepszego doświadczenia
            self.computer_turn()
            winner = self.check_winner()  # Sprawdzenie zwycięzcy po każdym strzale
            if winner:
                self.end_game(winner)
        self.save_game_button.handle_event(event)
        self.button_main_menu.handle_event(event)

    def display(self, surface):
        surface.blit(bg_image5, (0, 0))  # Ładowanie obrazu tła
        board = Board()
        if self.current_turn == 'player':
            # Wyświetlanie planszy komputera (bez statków)
            computer_view_board = self.get_view_board_with_sunken_ships(self.computer_board, self.computer_ships)
            board.draw_board(surface, computer_view_board, GRID_ORIGIN_X, GRID_ORIGIN_Y, ships=self.computer_ships)
            self.save_game_button.display(surface)
            self.button_main_menu.display(surface)
            # Rysowanie tylko zatopionych statków komputera
            for ship in self.computer_ships:
                if ship.is_sunk():
                    ship.draw(surface)
            computer_ships_count = self.get_active_ships_count(self.active_computer_ships)
            self.display_ships(surface, computer_ships_count, 20, "Pozostałe statki Komputera:")
        else:
            # Wyświetlanie planszy gracza (z jego statkami)
            board.draw_board(surface, self.player_board, GRID_ORIGIN_X, GRID_ORIGIN_Y, ships=self.player_ships)
            for ship in self.player_ships:
                ship.draw(surface)  # Rysowanie statków gracza
            # Wyświetlanie pozostałych statków Gracza
            player_ships_count = self.get_active_ships_count(self.active_player_ships)
            self.display_ships(surface, player_ships_count, 20, "Pozostałe statki Gracza:")


        turn_text = Text(f"Tura: {'Gracza' if self.current_turn == 'player' else 'Komputera'}", WIDTH // 2 - 280, 30, font_size=36, font=font2)
        turn_text.display(surface)
        difficult_level = Text(f"Grasz na poziomie : {self.difficulty}", WIDTH // 2 + 190, 30, font_size=36, font=font2)
        difficult_level.display(surface)

    def get_view_board_with_sunken_ships(self, board, ships):
        view_board = [['' for _ in range(10)] for _ in range(10)]
        for x in range(10):
            for y in range(10):
                if board[x][y] == 'H' or board[x][y] == 'M':
                    view_board[x][y] = board[x][y]

        for ship in ships:
            if ship.is_sunk():
                for seg_x, seg_y in ship.get_segments():
                    view_board[seg_x][seg_y] = 'H'  

        return view_board


    def display_ships(self, surface, ships_count, start_x, title):
        title_text = Text(title, start_x, 60, font_size=24, font=font2)
        title_text.display(surface)

        # Wyświetlanie statków
        for length, count in ships_count.items():
            ship_show = ShipShow(length, start_x, 80 + length * 60)
            ship_show.draw(surface, count)

    def get_active_ships_count(self, ships):
        count_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for ship in ships:
            if not ship.is_sunk():
                count_dict[ship.length] += 1
        return count_dict
        


    def display_board_after_shot(self, turn):
        # Aktualizacja wyświetlania planszy po strzale
        self.display(win)
        pygame.display.flip()
    
    def end_game(self, winner):
        if winner == 'player':
            self.menu.active_menu = 'win'
            self.menu.draw_win_game()
        else:
            self.menu.active_menu = 'lose'
            self.menu.draw_lose_game()
    
    def main_menu(self):
        self.save_game()
        if self.menu:
            self.menu.active_menu = 'main'

    def save_game(self):
        save_data = {
            'player_ships': [ship.to_dict() for ship in self.player_ships],
            'computer_ships': [ship.to_dict() for ship in self.computer_ships],
            'difficulty': self.difficulty,
            'player_board': self.player_board,
            'computer_board': self.computer_board,
            'current_turn': self.current_turn,
            'computer_hits': self.computer_hits,
            'computer_misses': self.computer_misses,
            'target_mode': self.target_mode,
            'consecutive_misses': self.consecutive_misses,
            'active_player_ships': [ship.to_dict() for ship in self.active_player_ships],
            'active_computer_ships': [ship.to_dict() for ship in self.active_computer_ships]
        }
        with open(savegame_path, 'w') as f:
            json.dump(save_data, f, indent=4)


    def load_game(self):
        with open(savegame_path, 'r') as f:
            save_data = json.load(f)

        # Tworzenie prostokąta reprezentującego obszar planszy
        board_rect = pygame.Rect(GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE * 10, CELL_SIZE * 10)

        # Wczytywanie statków gracza i komputera z zapisu
        self.player_ships = [Ship.from_dict(ship_data, board_rect) for ship_data in save_data['player_ships']]
        self.computer_ships = [Ship.from_dict(ship_data, board_rect) for ship_data in save_data['computer_ships']]

        # Przywracanie pozostałych elementów stanu gry
        self.difficulty = save_data['difficulty']
        self.player_board = save_data['player_board']
        self.computer_board = save_data['computer_board']
        self.current_turn = save_data['current_turn']
        self.computer_hits = save_data.get('computer_hits', [])
        self.computer_misses = save_data.get('computer_misses', [])
        self.target_mode = save_data.get('target_mode', False)
        self.consecutive_misses = save_data.get('consecutive_misses', 0)
        self.active_player_ships = [Ship.from_dict(ship_data, board_rect) for ship_data in save_data['active_player_ships']]
        self.active_computer_ships = [Ship.from_dict(ship_data, board_rect) for ship_data in save_data['active_computer_ships']]

        # Aktualizacja statusu segmentów trafionych/zatopionych
        self.update_ships_status(self.player_board, self.player_ships)
        self.update_ships_status(self.computer_board, self.computer_ships)
        # Aktualizacja list trafień i chybień komputera
        self.update_computer_shots(self.player_board)

        # Usuwanie pliku zapisu po wczytaniu (opcjonalnie, zależy od wymagań gry)
        os.remove(savegame_path)

    def update_ships_status(self, board, ships):
        for ship in ships:
            for seg_x, seg_y in ship.get_segments():
                if board[seg_x][seg_y] == 'H':
                    ship.hit_segment(ship.get_segments().index((seg_x, seg_y)))

    def update_computer_shots(self, board):
        self.computer_hits.clear()
        self.computer_misses.clear()
        for x in range(10):
            for y in range(10):
                if board[x][y] == 'H':
                    self.computer_hits.append((x, y))
                elif board[x][y] == 'M':
                    self.computer_misses.append((x, y))


class Menu:
    def __init__(self):
        self.active_menu = 'main'
        self.difficulty_level = None
        self.fade_state = None
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.last_active_menu = None  # Dodane do śledzenia ostatniego aktywnego menu
        self.randomize_button_pressed = False
        self.reset_button_pressed = False

        

        
        # Główne Menu
        self.play_game_button = Button("Graj", ((WIDTH // 8)-100), 200, 200, 50, action=self.draw_difficulty_menu, font=font2, sound=button_sound)
        self.settings_button = Button("Ustawienia", ((WIDTH // 8)-100), 260, 200, 50, action=self.settings, font=font2, sound=button_sound)
        self.player_name = settings['player_name']
        self.exit_button = Button("Wyjdź z gry",((WIDTH // 8)-100), 800, 200, 50, action=self.exit_game, font=font2, sound=button_sound)
        self.info_button = Button("Informacje", ((WIDTH // 8)-100), 460, 200, 50, action=self.draw_info_screen, font=font2, sound=button_sound)
        self.load_game_button = Button("Wczytaj", ((WIDTH // 8)-100), 320, 200, 50, action=self.load_game, font=font2, sound=button_sound)

        # Menu Ustawień
        self.back_settings_button = Button("Wstecz", 100, 550, 200, 50, action=self.draw_main_menu, font=font2, sound=button_sound)
        self.volume_slider = Slider(100, 350, 300, 0, 1, settings['music_volume'])
        self.music_checkbox = CheckBox(150, 170, settings['music_on'])
        self.settings_volume_text = Text("Głośność Muzyki", 100, 250, font=font2)
        self.settings_music_text = Text("Włączyć Muzykę?", 100, 100, font=font2)
        self.settings_effect_text = Text("Włączyć Efekty Dźwiękowe?", 500, 100, font=font2)
        self.effect_checkbox = CheckBox_Effect(550, 170, settings['effect_on'])
        self.settings_effect_volume_text = Text("Głośność Efektów", 500, 250, font=font2)
        self.effect_volume_slider = Slider_Effects(500, 350, 300, 0, 1, settings['effect_volume'])

        # Menu Wyboru Poziomu Trudności
        self.back_difficulty_button = Button("Wstecz", (WIDTH // 4 + 200), 550, 200, 50, action=self.draw_main_menu, font=font2, sound=button_sound)
        self.difficulty_text = Text("Wybierz poziom trudności", (WIDTH // 4 + 130), 100, font=font2)
        self.easy_button = Button("Łatwy", (WIDTH // 4 + 200), 200, 200, 50, action=lambda: self.set_difficulty('Łatwy'), font=font2, sound=button_sound)
        self.medium_button = Button("Średni", (WIDTH // 4 + 200), 260, 200, 50, action=lambda: self.set_difficulty('Średni'), font=font2, sound=button_sound)
        self.hard_button = Button("Trudny", (WIDTH // 4 + 200), 320, 200, 50, action=lambda: self.set_difficulty('Trudny'), font=font2, sound=button_sound)

        # Menu Informacje 
        self.back_info_button = Button("Wstecz", ((WIDTH // 8)-100), 700, 200, 50, action=self.draw_main_menu, font=font2, sound=button_sound)
        self.info_text = """Projekt "Bitwa Morska" wykorzystuje Python i Pygame.
        \nW rolach głównych:
        \n- Autor - Krzysztof Ambroziak
        \n- Język Programowania  - Python 3.11
        \n- Biblioteka Główna - PyGame
        \n- Muzyka - Hans Zimmer
        \n- Efekty Dźwiekowe - Stock
        \n- Jack Sparrow - Johnny Depp
        \n
        \n
        \n Ciekawostka nr 1: 
        \n Gra miała mieć moduł sieciowy.
        \n
        \n
        \n Ciekawostka nr 2:
        \n Powstawanie gry pochłonęło około 13h pracy.
        \n
        \n
        \n Ciekawostka nr 3:
        \n Niektóre statki w tej grze mają więcej linii kodu niż Titanic!
        \n
        \n
        \n- KONIEC 
        \n
        \n
        \n żaden statek nie ucierpiał podczas zdjęć
        \n to co widzicie na ekranie to efekty specjalne"""
        self.info_text_position = HEIGHT  # Startowa pozycja tekstu

        # Menu Ustawiania Statków
        self.randomize_button = Button("Ustaw Losowo", ((WIDTH // 5) - 300), 750, 200, 50, action=self.randomize_ships, font=font2, sound=button_sound)
        self.reset_button = Button("Resetuj", ((WIDTH // 5)-100), 750, 200, 50, action=self.reset_ships, font=font2, sound=button_sound)
        self.play_button = Button("Graj", ((WIDTH // 5) + 100), 750, 200, 50, action=self.play_game, font=font2, sound=button_sound)
        self.back_setup_button = Button("Wstecz", ((WIDTH // 5) + 500), 750, 200, 50, action=self.back_setup_button_f, font=font2, sound=button_sound)
        

        # Koniec
        self.back_endgame_button = Button("Wstecz", ((WIDTH // 8)-100), 750, 200, 50, action=self.draw_main_menu, font=font2, sound=button_sound)
        # Wygrana
        self.win_text1 = Text("Udało Ci się zatopić statki wroga!", 100, 250, font=font2)
        self.win_text2 = Text("Ocean jest Twój!", 100, 300, font=font2)
        # Przegrana
        self.lose_text1 = Text("...Zatopiono Twoją flotę...", 680, 50, font=font2)
        self.lose_text2 = Text("...jesteś na Krańcu Świata...", 650, 100, font=font2)

    def start_fade(self):
        self.fade_state = {'progress': 0, 'duration': 500}

    def apply_fade(self):
        if self.fade_state and self.fade_state['progress'] < self.fade_state['duration']:
            alpha = 255 * (1 - self.fade_state['progress'] / self.fade_state['duration'])
            self.fade_surface.set_alpha(alpha)
            win.blit(self.fade_surface, (0, 0))
            self.fade_state['progress'] += 16.67
        else:
            self.fade_state = None

    def change_menu(self, new_menu):
        if self.active_menu != new_menu:
            self.active_menu = new_menu
            self.start_fade()

    def draw_main_menu(self):
        self.change_menu('main')
        self.play_game_button.display(screen)
        self.settings_button.display(screen)
        self.exit_button.display(screen)
        self.info_button.display(screen)
        if os.path.exists(savegame_path):  # Sprawdzenie, czy istnieje zapis gry
            self.load_game_button.y = 260
            self.settings_button.y = 320
            self.load_game_button.display(screen)
        else:
            self.settings_button.y = 260
    
    # Metoda do obsługi wczytywania gry
    def load_game(self):
        self.game = Game(menu=self)
        self.active_menu = 'game'

    def draw_info_screen(self):
        self.change_menu('info')
        win.blit(b_info, (0, 0))
        if self.last_active_menu != self.active_menu:
            self.info_text_position = HEIGHT  # Reset pozycji tekstu przy wejściu na ekran
            self.last_active_menu = self.active_menu

        self.info_text_position -= 2  # Przewijanie tekstu w górę

        lines = self.info_text.split('\n')
        line_height = 20
        total_text_height = len(lines) * line_height

        # Sprawdzenie, czy cały tekst został przewinięty i resetowanie pozycji
        if self.info_text_position + total_text_height < 0:
            self.info_text_position = HEIGHT

        for i, line in enumerate(lines):
            text_obj = Text(line, WIDTH // 4, self.info_text_position + i * line_height, font_size=36)
            text_obj.display(win)

        self.back_info_button.display(win)

    def settings(self):
        self.change_menu('settings')
        win.blit(bg_image4, (0, 0))
        self.volume_slider.display(screen)
        self.music_checkbox.display(screen)
        self.back_settings_button.display(screen)
        self.settings_volume_text.display(screen)
        self.settings_music_text.display(screen)
        self.settings_effect_text.display(screen)
        self.effect_checkbox.display(screen)
        self.settings_effect_volume_text.display(screen)
        self.effect_volume_slider.display(screen)

    def draw_difficulty_menu(self):
        self.active_menu = 'difficulty'
        win.blit(bg_image2, (0, 0))
        self.back_difficulty_button.display(screen)
        self.difficulty_text.display(screen)
        self.easy_button.display(screen)
        self.medium_button.display(screen)
        self.hard_button.display(screen)

    def draw_ship_setup_menu(self):
        self.active_menu = 'setup'
        win.blit(bg_image3, (0, 0))
        self.reset_button.display(screen)
        self.play_button.display(screen)
        self.randomize_button.display(screen)
        self.back_setup_button.display(screen)
        self.difficulty_level_text = Text(f"Poziom Trudności: {self.difficulty_level}", (WIDTH // 4 + 130), 30, font=font2)
        self.difficulty_level_text.display(screen)
        board = Board()
        board.draw(win)
        
        # Aktualizacja listy statków do wyświetlenia i obsługa statków do przeciągania
        if not hasattr(self, 'ship_shows'):
            # Zdefiniowanie statków: 1x5, 1x4, 1x3, 2x2, 2x1
            ship_lengths = [5, 4, 3, 2, 2, 1, 1]
            self.ship_shows = [ShipShow(length, 50, 500 - (length + 1) * 70) for length in ship_lengths]
            self.ships = []
            # Dostosowanie dostępnych statków
            self.available_ships = {1: 2, 2: 2, 3: 1, 4: 1, 5: 1}

        for ship_show in self.ship_shows:
            ship_show.draw(win, self.available_ships[ship_show.length])

        for ship in self.ships:
            ship.draw(win)

    def play_game(self):
        win.blit(bg_image5, (0, 0))
        # Zapisanie statków gracza i inicjalizacja gry
        player_ships = self.ships
        self.game = Game(player_ships, self.difficulty_level, menu=self)
        self.active_menu = 'game'
        self.board = Board()

    def draw_win_game(self):
        self.active_menu = 'win'
        win.blit(bg_image_win, (0, 0))
        self.back_endgame_button.display(screen)
        self.win_text1.display(screen)
        self.win_text2.display(screen)
        self.reset_ships()

    def draw_lose_game(self):
        self.active_menu = 'lose'
        win.blit(bg_image_lose, (0, 0))
        self.back_endgame_button.display(screen)
        self.lose_text1.display(screen)
        self.lose_text2.display(screen)
        self.reset_ships()

        


    def display(self):
        if self.active_menu == 'main':
            self.draw_main_menu()
        elif self.active_menu == 'difficulty':
            self.draw_difficulty_menu()
        elif self.active_menu == 'setup':
            self.draw_ship_setup_menu()
        elif self.active_menu == 'settings':
            self.settings()
        elif self.active_menu == 'info':
            self.draw_info_screen()
        elif self.active_menu == 'game':
            self.game.display(win)
        elif self.active_menu == 'win':
            self.draw_win_game()
        elif self.active_menu == 'lose':
            self.draw_lose_game()
        
        # Aplikowanie efektu fade (jeśli aktywny)
        if self.last_active_menu != self.active_menu:
            self.start_fade()
            self.last_active_menu = self.active_menu

        if self.fade_state:
            self.apply_fade()

    def handle_event(self, event):
        if self.active_menu == 'main':
            self.play_game_button.handle_event(event)
            self.settings_button.handle_event(event)
            self.exit_button.handle_event(event)
            self.info_button.handle_event(event)
            self.load_game_button.handle_event(event)
        elif self.active_menu == 'settings':
            self.back_settings_button.handle_event(event)
            self.volume_slider.handle_event(event)
            self.music_checkbox.handle_event(event)
            self.effect_checkbox.handle_event(event)
            self.effect_volume_slider.handle_event(event)
        elif self.active_menu == 'info':
            self.back_info_button.handle_event(event)
        elif self.active_menu == 'difficulty':
            self.back_difficulty_button.handle_event(event)
            self.easy_button.handle_event(event)
            self.medium_button.handle_event(event)
            self.hard_button.handle_event(event)
        elif self.active_menu == 'win':
            self.back_endgame_button.handle_event(event)
        elif self.active_menu == 'lose':
            self.back_endgame_button.handle_event(event)
        elif self.active_menu == 'setup':
            if event.type == pygame.MOUSEBUTTONUP:
                if self.reset_button_pressed:
                    self.reset_button_pressed = False
                elif self.randomize_button_pressed:
                    self.randomize_button_pressed = False

            self.randomize_button.handle_event(event)
            self.reset_button.handle_event(event)
            self.play_button.handle_event(event)
            self.back_setup_button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for ship_show in self.ship_shows:
                    if ship_show.rect.collidepoint(event.pos) and self.available_ships[ship_show.length] > 0:
                        new_ship = Ship(ship_show.length, event.pos[0], event.pos[1])
                        self.ships.append(new_ship)
                        break
            
            board_rect = pygame.Rect(GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE * 10, CELL_SIZE * 10)
            for ship in list(self.ships):
                ship.handle_event(event, board_rect, self.ships)

                if not ship.dragging and event.type == pygame.MOUSEBUTTONUP:
                    if ship.is_valid_placement(self.ships):
                        if ship.is_new:
                            self.available_ships[ship.length] -= 1
                            ship.is_new = False
                    else:
                        if ship.is_new:
                            self.ships.remove(ship)
                        else:
                            self.available_ships[ship.length] += 1
                            self.ships.remove(ship)
        elif self.active_menu == 'game':
            self.game.update(event)

    
    def set_difficulty(self, level):
        self.difficulty_level = level
        print(f"Wybrano poziom trudności: {self.difficulty_level}")
        self.draw_ship_setup_menu()

    def reset_ships(self):
        self.reset_button_pressed = True
        self.ships = []
        self.available_ships = {1: 2, 2: 2, 3: 1, 4: 1, 5: 1}

    def randomize_ships(self):
        self.reset_ships()
        self.randomize_button_pressed = True
        
        for length, count in self.available_ships.items():
            for _ in range(count):
                placed = False
                while not placed:
                    x = random.randint(0, 9)
                    y = random.randint(0, 9)
                    horizontal = random.choice([True, False])

                    # Utwórz tymczasowy statek z odpowiednią orientacją
                    temp_ship = Ship(length, GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y + y * CELL_SIZE)
                    temp_ship.horizontal = horizontal
                    if horizontal:
                        temp_ship.rect.width, temp_ship.rect.height = length * CELL_SIZE, CELL_SIZE
                    else:
                        temp_ship.rect.width, temp_ship.rect.height = CELL_SIZE, length * CELL_SIZE

                    # Sprawdź, czy statek mieści się na planszy
                    if (temp_ship.rect.right <= GRID_ORIGIN_X + 10 * CELL_SIZE and
                            temp_ship.rect.bottom <= GRID_ORIGIN_Y + 10 * CELL_SIZE and
                            temp_ship.is_valid_placement(self.ships)):
                        self.ships.append(temp_ship)
                        placed = True


    def back_setup_button_f(self):
        self.reset_ships()
        self.draw_difficulty_menu()

    

    def exit_game(self):
        pygame.quit()
        sys.exit()

def main():
    running = True
    clock = pygame.time.Clock()
    menu = Menu()
    loading_screen = LoadingScreen(win)
    loading_done = False
    pygame_icon = pygame.image.load(icon)
    pygame.display.set_icon(pygame_icon)

    while running:
        dt = clock.tick(144)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == pygame.USEREVENT:  # Zdarzenie zakończenia utworu
                play_music()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                if not loading_done:
                    loading_done = loading_screen.skip_or_advance_sequence()

        if not loading_done:
            loading_done = loading_screen.update(dt)
            loading_screen.display()
        else:
            win.blit(bg_image, (0, 0))
            menu.handle_event(event)
            menu.display()

        pygame.display.flip()

if __name__ == '__main__':
    main()


