import pygame
import random

# Инициализация pygame
pygame.init()

# Константы
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
SIDEBAR_WIDTH = 200

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - голубой
    (255, 255, 0),  # O - жёлтый
    (128, 0, 128),  # T - фиолетовый
    (0, 255, 0),    # S - зелёный
    (255, 0, 0),    # Z - красный
    (0, 0, 255),    # J - синий
    (255, 165, 0),  # L - оранжевый
]

# Фигуры (тетрамино)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]


class Tetromino:
    def __init__(self, shape_index):
        self.shape_index = shape_index
        self.shape = [row[:] for row in SHAPES[shape_index]]
        self.color = COLORS[shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """Поворот фигуры по часовой стрелке"""
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[self.shape[rows - 1 - j][i] for j in range(rows)] for i in range(cols)]
        return rotated


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + SIDEBAR_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Тетрис")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        """Сброс игры"""
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # мс

    def new_piece(self):
        """Создание новой фигуры"""
        return Tetromino(random.randint(0, len(SHAPES) - 1))

    def valid_move(self, piece, x, y, shape=None):
        """Проверка допустимости хода"""
        if shape is None:
            shape = piece.shape
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return False
        return True

    def lock_piece(self):
        """Фиксация фигуры на поле"""
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + row_idx
                    grid_x = self.current_piece.x + col_idx
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.game_over = True

    def clear_lines(self):
        """Удаление заполненных линий"""
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        # Подсчёт очков
        lines_count = len(lines_to_clear)
        if lines_count > 0:
            self.lines_cleared += lines_count
            score_table = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += score_table.get(lines_count, 0) * self.level
            
            # Повышение уровня
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)

    def drop_piece(self):
        """Падение фигуры на одну клетку"""
        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
            return True
        else:
            self.lock_piece()
            return False

    def hard_drop(self):
        """Мгновенное падение"""
        while self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
            self.score += 2
        self.lock_piece()

    def draw_block(self, x, y, color):
        """Рисование одного блока"""
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
        pygame.draw.rect(self.screen, color, rect)
        # Эффект объёма
        pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=3)

    def draw_grid(self):
        """Рисование игрового поля"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.draw_block(x, y, self.grid[y][x])
        
        # Граница поля
        pygame.draw.rect(self.screen, WHITE, 
                        (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

    def draw_piece(self, piece, offset_x=0, offset_y=0, ghost=False):
        """Рисование фигуры"""
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + col_idx + offset_x
                    y = piece.y + row_idx + offset_y
                    if y >= 0:
                        if ghost:
                            color = tuple(c // 3 for c in piece.color)
                        else:
                            color = piece.color
                        self.draw_block(x, y, color)

    def draw_ghost_piece(self):
        """Рисование призрачной фигуры (подсказка)"""
        ghost_y = self.current_piece.y
        while self.valid_move(self.current_piece, self.current_piece.x, ghost_y + 1):
            ghost_y += 1
        self.draw_piece(self.current_piece, offset_x=0, offset_y=ghost_y - self.current_piece.y, ghost=True)

    def draw_sidebar(self):
        """Рисование боковой панели"""
        sidebar_x = SCREEN_WIDTH + 10
        
        # Следующая фигура
        next_label = self.font.render("След.", True, WHITE)
        self.screen.blit(next_label, (sidebar_x, 10))
        
        if self.next_piece:
            for row_idx, row in enumerate(self.next_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            sidebar_x + col_idx * BLOCK_SIZE,
                            50 + row_idx * BLOCK_SIZE,
                            BLOCK_SIZE - 1, BLOCK_SIZE - 1
                        )
                        pygame.draw.rect(self.screen, self.next_piece.color, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=3)
        
        # Счёт
        score_label = self.font.render(f"Счёт: {self.score}", True, WHITE)
        self.screen.blit(score_label, (sidebar_x, 180))
        
        # Уровень
        level_label = self.font.render(f"Уровень: {self.level}", True, WHITE)
        self.screen.blit(level_label, (sidebar_x, 220))
        
        # Линии
        lines_label = self.font.render(f"Линии: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_label, (sidebar_x, 260))
        
        # Управление
        controls = [
            "Управление:",
            "← → : Движение",
            "↑ : Поворот",
            "↓ : Ускорить",
            "Пробел : Сброс",
            "R : Рестарт",
            "ESC : Выход"
        ]
        for i, text in enumerate(controls):
            label = pygame.font.Font(None, 24).render(text, True, GRAY)
            self.screen.blit(label, (sidebar_x, 320 + i * 25))

    def draw_game_over(self):
        """Рисование экрана Game Over"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        restart_text = self.font.render("Нажмите R для рестарта", True, WHITE)
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw(self):
        """Отрисовка всего"""
        self.screen.fill(BLACK)
        self.draw_grid()
        
        if not self.game_over:
            self.draw_ghost_piece()
            self.draw_piece(self.current_piece)
        
        self.draw_sidebar()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()

    def handle_input(self):
        """Обработка ввода"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece.x - 1, self.current_piece.y):
                            self.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece.x + 1, self.current_piece.y):
                            self.current_piece.x += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                            self.current_piece.y += 1
                            self.score += 1
                    elif event.key == pygame.K_UP:
                        rotated = self.current_piece.rotate()
                        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, rotated):
                            self.current_piece.shape = rotated
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
        
        return True

    def run(self):
        """Основной игровой цикл"""
        running = True
        while running:
            dt = self.clock.tick(60)
            running = self.handle_input()
            
            if not self.game_over:
                self.fall_time += dt
                if self.fall_time >= self.fall_speed:
                    self.drop_piece()
                    self.fall_time = 0
            
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
