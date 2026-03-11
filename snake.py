import pygame
import random
import sys

# Инициализация pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)


def get_random_position():
    """Генерация случайной позиции в пределах игрового поля."""
    x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
    y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
    return x, y


def draw_snake(snake):
    """Отрисовка змейки."""
    for i, segment in enumerate(snake):
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(screen, color, (*segment, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, WHITE, (*segment, CELL_SIZE, CELL_SIZE), 1)


def draw_food(food):
    """Отрисовка еды."""
    pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, WHITE, (*food, CELL_SIZE, CELL_SIZE), 1)


def draw_score(score):
    """Отрисовка счёта."""
    score_text = font.render(f"Счёт: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))


def draw_game_over(score):
    """Экран проигрыша."""
    screen.fill(BLACK)
    game_over_text = font.render("Игра окончена!", True, RED)
    score_text = font.render(f"Ваш счёт: {score}", True, WHITE)
    restart_text = font.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))
    pygame.display.flip()


def main():
    """Основной цикл игры."""
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL_SIZE, 0)  # Движение вправо
    food = get_random_position()
    score = 0
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # Рестарт игры
                        snake = [(WIDTH // 2, HEIGHT // 2)]
                        direction = (CELL_SIZE, 0)
                        food = get_random_position()
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    # Управление змейкой
                    if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                        direction = (0, -CELL_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                        direction = (0, CELL_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                        direction = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                        direction = (CELL_SIZE, 0)

        if not game_over:
            # Движение змейки
            head_x, head_y = snake[0]
            dir_x, dir_y = direction
            new_head = (head_x + dir_x, head_y + dir_y)

            # Проверка столкновений
            if (new_head in snake or
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT):
                game_over = True
            else:
                snake.insert(0, new_head)

                # Проверка: съела ли змейка еду
                if new_head == food:
                    score += 1
                    food = get_random_position()
                    # Убедиться, что еда не появилась внутри змейки
                    while food in snake:
                        food = get_random_position()
                else:
                    snake.pop()

        # Отрисовка
        screen.fill(BLACK)
        draw_snake(snake)
        draw_food(food)
        draw_score(score)

        if game_over:
            draw_game_over(score)
        else:
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
