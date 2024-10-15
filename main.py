import pygame
import random
import time

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Ширина и высота экрана
screen_width = 640
screen_height = 520
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Лабиринт')

# Цвета
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Параметры стен и дверей
line_width = 10
line_gap = 40
line_offset = 20
door_width = 40
max_openings_per_line = 5

# Параметры игрока и начальная позиция
player_radius = 10
player_speed = 2
player_x = screen_width - 12
player_y = screen_height - 60

# Загрузка и масштабирование фонового изображения
background_image = pygame.image.load('background.jpg')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height - 40))

# Загрузка и настройка музыки
pygame.mixer.music.load('game_music.mp3')  # Фоновая музыка
victory_sound = pygame.mixer.Sound('victory_sound.mp3')  # Звук победы
defeat_sound = pygame.mixer.Sound('defeat_sound.mp3')  # Звук поражения

# Начало воспроизведения фоновой музыки
pygame.mixer.music.play(-1)  # Цикл бесконечно

# Переменные управления звуком и паузой
is_muted = False
is_paused = False

# Функция для отрисовки стен
def draw_walls():
    lines = []
    for i in range(0, screen_width, line_gap):
        num_openings = random.randint(1, max_openings_per_line)
        openings = sorted(random.sample(range(line_offset + door_width, screen_height - line_offset - door_width - 40), num_openings))

        last_opening_bottom = 0
        for opening_top in openings:
            # Верхний сегмент стены
            if last_opening_bottom < opening_top:
                lines.append(pygame.Rect(i, last_opening_bottom, line_width, opening_top - last_opening_bottom))
            last_opening_bottom = opening_top + door_width
        # Нижний сегмент стены
        if last_opening_bottom < screen_height - 40:
            lines.append(pygame.Rect(i, last_opening_bottom, line_width, screen_height - last_opening_bottom - 40))
    return lines

# Функция для отображения текста
def show_message(message):
    font = pygame.font.Font(None, 74)
    text = font.render(message, True, white)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.fill(black)
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.delay(5000)  # Подождать 5 секунд

# Функция для обработки паузы и звука
def handle_buttons():
    global is_paused, is_muted
    mouse_pos = pygame.mouse.get_pos()
    # Проверка кнопки паузы
    if pause_button_rect.collidepoint(mouse_pos):
        is_paused = not is_paused  # Переключить состояние паузы
        if is_paused:
            pygame.mixer.music.pause()  # Пауза музыки
        else:
            if not is_muted:  # Если звук не выключен, возобновить музыку
                pygame.mixer.music.unpause()
    # Проверка кнопки звука
    elif mute_button_rect.collidepoint(mouse_pos):
        is_muted = not is_muted  # Переключить состояние звука
        if is_muted:
            pygame.mixer.music.pause()  # Пауза музыки
            victory_sound.stop()  # Остановить звук победы
            defeat_sound.stop()  # Остановить звук поражения
        else:
            pygame.mixer.music.unpause()  # Возобновить музыку

# Основная функция
def main():
    global player_x, player_y
    lines = draw_walls()  # Отрисовка стен
    clock = pygame.time.Clock()

    # Кнопки паузы и звука
    global pause_button_rect, mute_button_rect
    pause_button_rect = pygame.Rect(screen_width - 210, screen_height - 35, 80, 30)
    mute_button_rect = pygame.Rect(screen_width - 120, screen_height - 35, 80, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_buttons()  # Обработка нажатий кнопок

        if is_paused:
            continue  # Пропустить остальную логику, если игра на паузе

        # Движение игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > player_radius:
            player_x -= player_speed
        elif keys[pygame.K_RIGHT] and player_x < screen_width - player_radius:
            player_x += player_speed
        elif keys[pygame.K_UP] and player_y > player_radius:
            player_y -= player_speed
        elif keys[pygame.K_DOWN] and player_y < screen_height - player_radius - 40:  # Учитывать пространство для кнопок
            player_y += player_speed

        # Проверка столкновений игрока со стенами
        player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
        collided = False

        for line in lines:
            if line.colliderect(player_rect):
                collided = True
                break

        # Проверка столкновения с нижней стеной (поражение)
        if collided:
            pygame.mixer.music.pause()  # Остановить текущую музыку
            if not is_muted:  # Проверить, что звук не выключен
                defeat_sound.play()  # Проиграть звук поражения
            show_message("Проигрыш!")  # Показать сообщение о поражении
            break  # Выйти из цикла игры

        # Проверка столкновения с левой стеной (победа)
        if player_rect.colliderect(pygame.Rect(0, 0, line_width, screen_height)):
            pygame.mixer.music.stop()  # Остановить текущую музыку
            if not is_muted:  # Проверить, что звук не выключен
                victory_sound.play()  # Проиграть звук победы
            show_message("Победа!")  # Показать сообщение о победе
            break  # Выйти из цикла игры

        # Очистка экрана
        screen.blit(background_image, (0, 0))

        # Отрисовка стен
        for line in lines:
            pygame.draw.rect(screen, red, line)

        # Отрисовка игрока
        pygame.draw.circle(screen, green, (player_x, player_y), player_radius)

        # Отрисовка кнопок
        pygame.draw.rect(screen, blue, pause_button_rect)
        pygame.draw.rect(screen, blue, mute_button_rect)

        # Текст кнопок
        font = pygame.font.Font(None, 36)  # Шрифт для кнопок
        pause_text = font.render("Пауза", True, white)
        mute_text = font.render("Звук", True, white)
        pause_text_rect = pause_text.get_rect(center=pause_button_rect.center)
        mute_text_rect = mute_text.get_rect(center=mute_button_rect.center)
        screen.blit(pause_text, pause_text_rect)
        screen.blit(mute_text, mute_text_rect)

        pygame.display.update()
        clock.tick(60)  # Поддержка 60 кадров в секунду

# Запуск основной функции
if __name__ == "__main__":
    main()
