import pygame
from pygame.locals import *
import json
import sys
import os

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

# Czcionki
#font1 = resource_path("assets/settings/fonts/BlackRose.ttf")
#font2 = resource_path("assets/settings/fonts/JackPirate.ttf")

# Pliki json
#settings_path = resource_path('assets/settings/settings.json')

# Zdjęcia
#img1 = resource_path("assets/images/button.png")
#img2 = resource_path("assets/images/button_hover.png")

#DO TESTÓW
# Czcionki
font1 = resource_path("../settings/fonts/BlackRose.ttf")
font2 = resource_path("../settings/fonts/JackPirate.ttf")

# Pliki json
settings_path = resource_path('../settings/settings.json')

# Zdjęcia
img1 = resource_path("../images/button.png")
img2 = resource_path("../images/button_hover.png")

# Wszystkie stałe kolorów i inne zmienne globalne
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (70, 70, 70)
LIGHT_GRAY = (200, 200, 200)
HOVER_COLOR = (150, 150, 150)

image = img1
hover_image = img2

# Ładowanie ustawień z pliku
with open(settings_path, 'r') as f:
    settings = json.load(f)

class Text:
    def __init__(self, text, x, y, font_size=36, font=None):
        self.text = text
        self.x = x
        self.y = y
        self.font = pygame.font.Font(font, font_size)
        
    def display(self, screen):
        text_surface_white = self.font.render(self.text, True, WHITE)
        text_surface_black = self.font.render(self.text, True, BLACK)
        
        offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]  # Przesunięcia dla poświaty

        # Rysowanie poświaty (czarny tekst)
        for offset_x, offset_y in offsets:
            screen.blit(text_surface_black, (self.x + offset_x, self.y + offset_y))

        # Rysowanie głównego tekstu (biały tekst)
        screen.blit(text_surface_white, (self.x, self.y))

class InputBox:
    def __init__(self, x, y, w, h, font_size=36):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = LIGHT_GRAY
        self.color_active = GRAY
        self.color = self.color_inactive
        self.text = ''
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface_white = self.font.render(self.text, True, WHITE)
        self.txt_surface_black = self.font.render(self.text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # Sprawdź czy myszka jest w obrębie prostokąta
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Aktualizacja białego i czarnego tekstu
                self.txt_surface_white = self.font.render(self.text, True, WHITE)
                self.txt_surface_black = self.font.render(self.text, True, BLACK)

    def display(self, screen):
        # Rysuj tło
        pygame.draw.rect(screen, self.color, self.rect)
        # Rysuj poświatę (czarny tekst)
        offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]
        for offset_x, offset_y in offsets:
            screen.blit(self.txt_surface_black, (self.rect.x + 5 + offset_x, self.rect.y + 5 + offset_y))
        # Rysuj główny tekst (biały tekst)
        screen.blit(self.txt_surface_white, (self.rect.x + 5, self.rect.y + 5))
        # Rysuj obramowanie prostokąta
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Button:
    def __init__(self, text, x, y, width, height, action=None, font=None, sound=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.color = GRAY
        self.hover_color = HOVER_COLOR  # Dodaj ciemniejszy kolor dla efektu hover
        self.font = pygame.font.Font(font, 36)
        self.image = pygame.image.load(image) if image else None
        self.hover_image = pygame.image.load(hover_image) if hover_image else None
        self.hover = False
        self.radius = 10  # Zaokrąglenie rogu
        self.pressed = False  # Nowy atrybut do przechowywania stanu przycisku
        self.sound = sound

    def play_sound(self):
        if settings['effect_on'] and self.sound:  # Sprawdź, czy efekty są włączone
            sound_effect = pygame.mixer.Sound(self.sound)
            sound_effect.set_volume(settings['effect_volume'])  # Ustaw głośność
            sound_effect.play()

    def display(self, screen):
        if self.hover and self.hover_image:
            screen.blit(self.hover_image, (self.x, self.y))
        elif self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Opcjonalnie: rysowanie prostokąta, jeśli obrazy nie są dostępne
            color = self.hover_color if self.hover else self.color
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=self.radius)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)


    def handle_event(self, event):
        # Sprawdzanie, czy mysz jest nad przyciskiem
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            self.hover = True
            if event.type == MOUSEBUTTONDOWN:
                self.pressed = True  # Aktualizacja stanu przycisku
                if self.action:
                    self.action()
                    self.pressed = False
                self.play_sound()
            elif event.type == MOUSEBUTTONUP:
                self.pressed = False
        else:
            self.hover = False
            self.pressed = False  

def save_settings():
    """Zapisuje ustawienia do pliku settings.json."""
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, value):
        self.x = x
        self.y = y
        self.width = width
        self.min = min_val
        self.max = max_val
        self.value = value
        self.dragging = False
        self.thumb_radius = 15
        self.font = pygame.font.Font(None, 32)
        self.update_thumb_pos_from_value()

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        # Rysowanie linii
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + self.width, self.y), 3)
        pygame.draw.circle(screen, HOVER_COLOR if self.dragging else GRAY, (int(self.thumb_pos), self.y), self.thumb_radius)

        # Wyświetlanie wartości pod suwakiem
        value_text = str(self.value)
        text_width, text_height = self.font.size(value_text)
        value_position = (self.x + self.width // 2 - text_width // 2, self.y + self.thumb_radius + 5)
        self.draw_text_with_shadow(screen, value_text, value_position)

    def update_thumb_pos_from_value(self):
        """Aktualizuje pozycję kciuka na podstawie wartości suwaka."""
        self.thumb_pos = self.x + (self.value - self.min) * self.width / (self.max - self.min)

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance_to_thumb = abs(mouse_x - self.thumb_pos)
        if event.type == MOUSEBUTTONDOWN:
            if distance_to_thumb <= self.thumb_radius and self.y - self.thumb_radius <= mouse_y <= self.y + self.thumb_radius:
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self.thumb_pos = min(max(mouse_x, self.x), self.x + self.width)
            self.value = self.min + (self.thumb_pos - self.x) * (self.max - self.min) / self.width

            # Zaokrąglamy wartość do najbliższej wartości o kroku 0.1
            self.value = round(self.value, 1)
            self.update_thumb_pos_from_value()

            settings['music_volume'] = self.value
            pygame.mixer.music.set_volume(self.value)

            save_settings()




class CheckBox:
    def __init__(self, x, y, checked):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.checked = checked
        self.font = pygame.font.Font(font1, 32)
        self.released = True 

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height), border_radius=5)
        
        if self.checked:
            checkmark_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(checkmark_surface, WHITE, (10, 20), (15, 30), 4)
            pygame.draw.line(checkmark_surface, WHITE, (15, 30), (30, 10), 4)
            screen.blit(checkmark_surface, (self.x, self.y))

        text = "Tak" if self.checked else "Nie"
        text_width, text_height = self.font.size(text)
        self.draw_text_with_shadow(screen, text, (self.x - text_width - 10, self.y + (self.height - text_height) // 2))

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == MOUSEBUTTONDOWN and self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            if self.released:
                self.checked = not self.checked
                settings['music_on'] = self.checked
                save_settings()

                if self.checked:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
                self.released = False  # Zmiana stanu po obsłużeniu zdarzenia
        elif event.type == MOUSEBUTTONUP:
            self.released = True  # Resetowanie stanu przy zwolnieniu przycisku myszy


class CheckBox_Effect:
    def __init__(self, x, y, checked):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.checked = checked
        self.font = pygame.font.Font(font1, 32)
        self.released = True 

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height), border_radius=5)
        
        if self.checked:
            checkmark_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(checkmark_surface, WHITE, (10, 20), (15, 30), 4)
            pygame.draw.line(checkmark_surface, WHITE, (15, 30), (30, 10), 4)
            screen.blit(checkmark_surface, (self.x, self.y))

        text = "Tak" if self.checked else "Nie"
        text_width, text_height = self.font.size(text)
        self.draw_text_with_shadow(screen, text, (self.x - text_width - 10, self.y + (self.height - text_height) // 2))

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == MOUSEBUTTONDOWN and self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            if self.released:
                self.checked = not self.checked
                settings['effect_on'] = self.checked
                save_settings()
                self.released = False  # Zmiana stanu po obsłużeniu zdarzenia
        elif event.type == MOUSEBUTTONUP:
            self.released = True  # Resetowanie stanu przy zwolnieniu przycisku myszy

class Slider_Effects:
    def __init__(self, x, y, width, min_val, max_val, value):
        self.x = x
        self.y = y
        self.width = width
        self.min = min_val
        self.max = max_val
        self.value = value
        self.dragging = False
        self.thumb_radius = 15
        self.font = pygame.font.Font(None, 32)
        self.update_thumb_pos_from_value()

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        # Rysowanie linii
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + self.width, self.y), 3)
        pygame.draw.circle(screen, HOVER_COLOR if self.dragging else GRAY, (int(self.thumb_pos), self.y), self.thumb_radius)

        # Wyświetlanie wartości pod suwakiem
        value_text = str(self.value)
        text_width, text_height = self.font.size(value_text)
        value_position = (self.x + self.width // 2 - text_width // 2, self.y + self.thumb_radius + 5)
        self.draw_text_with_shadow(screen, value_text, value_position)

    def update_thumb_pos_from_value(self):
        """Aktualizuje pozycję kciuka na podstawie wartości suwaka."""
        self.thumb_pos = self.x + (self.value - self.min) * self.width / (self.max - self.min)

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance_to_thumb = abs(mouse_x - self.thumb_pos)
        if event.type == MOUSEBUTTONDOWN:
            if distance_to_thumb <= self.thumb_radius and self.y - self.thumb_radius <= mouse_y <= self.y + self.thumb_radius:
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self.thumb_pos = min(max(mouse_x, self.x), self.x + self.width)
            self.value = self.min + (self.thumb_pos - self.x) * (self.max - self.min) / self.width

            # Zaokrąglamy wartość do najbliższej wartości o kroku 0.1
            self.value = round(self.value, 1)
            self.update_thumb_pos_from_value()

            settings['effect_volume'] = self.value

            save_settings()