import pygame
import random
from .hole import Hole

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (100, 220, 100)


class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height

        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)

        for r in range(rows):
            for c in range(cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

        # Difficulty settings: spawn chance and mole visibility
        self.difficulties = {
            "Easy": (0.01, 60),
            "Medium": (0.02, 45),
            "Hard": (0.04, 30),
        }

        self.difficulty = "Medium"
        self.spawn_chance, self.mole_up_frames = (
            self.difficulties[self.difficulty]
        )

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.score = 0
        self.misses = 0

        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont(
            "Arial", 42, bold=True
        )
        self.small_font = pygame.font.SysFont("Arial", 20)

        # States: playing, game_over, menu
        self.state = "playing"
        self.game_over = False
        self.quit_requested = False

    def start_new_round(self, difficulty):
        self.difficulty = difficulty
        self.spawn_chance, self.mole_up_frames = (
            self.difficulties[difficulty]
        )

        self.score = 0
        self.misses = 0
        self.time_left_frames = self.round_seconds * 60

        for hole in self.holes:
            hole.active = False
            hole.timer = 0

        self.game_over = False
        self.state = "playing"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit_requested = True
            return

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos)

        elif self.state == "game_over":
            if (
                event.type == pygame.KEYDOWN
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.state = "menu"

        elif self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.start_new_round("Easy")
                elif event.key == pygame.K_2:
                    self.start_new_round("Medium")
                elif event.key == pygame.K_3:
                    self.start_new_round("Hard")
                elif event.key in (pygame.K_4, pygame.K_ESCAPE):
                    self.quit_requested = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Match the button positions in render()
                for i, difficulty in enumerate(
                    ["Easy", "Medium", "Hard"]
                ):
                    button = pygame.Rect(
                        self.width // 2 - 120,
                        220 + i * 65,
                        240,
                        48,
                    )

                    if button.collidepoint(x, y):
                        self.start_new_round(difficulty)
                        return

                quit_button = pygame.Rect(
                    self.width // 2 - 120,
                    415,
                    240,
                    48,
                )

                if quit_button.collidepoint(x, y):
                    self.quit_requested = True

    def _handle_click(self, pos):
        for hole in self.holes:
            if hole.active and hole.contains_point(pos):
                if hole.whack():
                    self.score += 1
                    return

        self.misses += 1

    def handle_input(self):
        pass

    def update(self):
        if self.state != "playing":
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.time_left_frames = 0
            self.game_over = True
            self.state = "game_over"

            for hole in self.holes:
                hole.active = False
                hole.timer = 0

            return

        for hole in self.holes:
            hole.update()

            if (
                not hole.active
                and random.random() < self.spawn_chance
            ):
                hole.pop_up(self.mole_up_frames)

    def render(self, screen):
        # Draw the game board
        for hole in self.holes:
            pygame.draw.circle(
                screen,
                DARK_BROWN,
                (hole.center_x, hole.center_y),
                40,
            )

            if hole.active:
                pygame.draw.circle(
                    screen,
                    MOLE_BROWN,
                    (hole.center_x, hole.center_y),
                    32,
                )

        score_text = self.font.render(
            f"Score: {self.score}", True, BLACK
        )
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(
            f"Time: {seconds_left}s", True, BLACK
        )
        screen.blit(
            timer_text,
            (self.width - 140, 10),
        )

        if self.state == "game_over":
            self._draw_overlay(screen)

            title = self.title_font.render(
                "GAME OVER", True, WHITE
            )
            final_score = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            instruction = self.small_font.render(
                "Press any key or click to continue",
                True,
                GRAY,
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 70,
                    )
                ),
            )
            screen.blit(
                final_score,
                final_score.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2,
                    )
                ),
            )
            screen.blit(
                instruction,
                instruction.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 60,
                    )
                ),
            )

        elif self.state == "menu":
            self._draw_overlay(screen)

            title = self.title_font.render(
                "PLAY AGAIN?", True, WHITE
            )
            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, 145)
                ),
            )

            for i, difficulty in enumerate(
                ["Easy", "Medium", "Hard"]
            ):
                button = pygame.Rect(
                    self.width // 2 - 120,
                    220 + i * 65,
                    240,
                    48,
                )

                pygame.draw.rect(
                    screen, DARK_BROWN, button, border_radius=8
                )

                label = self.font.render(
                    difficulty, True, WHITE
                )
                screen.blit(
                    label,
                    label.get_rect(center=button.center),
                )

            quit_button = pygame.Rect(
                self.width // 2 - 120,
                415,
                240,
                48,
            )
            pygame.draw.rect(
                screen, (120, 45, 45),
                quit_button, border_radius=8
            )

            quit_label = self.font.render(
                "Quit", True, WHITE
            )
            screen.blit(
                quit_label,
                quit_label.get_rect(center=quit_button.center),
            )

            hint = self.small_font.render(
                "Press 1, 2, 3 to play | 4 to quit",
                True,
                GRAY,
            )
            screen.blit(
                hint,
                hint.get_rect(
                    center=(self.width // 2, 490)
                ),
            )

    def _draw_overlay(self, screen):
        overlay = pygame.Surface(
            (self.width, self.height)
        )
        overlay.set_alpha(220)
        overlay.fill((30, 30, 30))
        screen.blit(overlay, (0, 0))
