"""
Аладдин - Приключения в Аграбе
Платформер в стиле Sega Aladdin

УПРАВЛЕНИЕ:
    ← / →        - Бег влево/вправо
    ↑            - Прыжок (на земле) / Двойной прыжок (в воздухе)
    ↓            - Лазание вниз по лестнице
    Пробел       - Атака мечом
    X            - Dash (рывок с неуязвимостью)
    Z            - Удар в прыжке (мощная атака в воздухе)
    C            - Огненный шар (магическая атака)
    V            - Магия (временное усиление, тратит 50 супер-метра)
    A            - Активация телепорта (на 3 уровне)
    SPACE        - Следующий уровень (после победы)
    R            - Рестарт игры (после проигрыша/победы)

ОСОБЕННОСТИ:
    - 3 уровня с разным дизайном
    - Бонусные комнаты с сундуками
    - Лестницы для лазания (1 и 2 уровни)
    - Телепорты (3 уровень)
    - Пружины для супер-прыжка
    - Комбо-удары с множителем очков
    - Супер-метр для особых атак
    - Система частиц и звуковые эффекты

ВРАГИ:
    - Стражники (зелёные с копьём) - 2 попадания
    - Летучие враги (фиолетовые) - 1 попадание
    - Босс Джафар (3 уровень) - 10 попаданий
"""

import pygame
import random
import math
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Аладдин - Приключения в Аграбе')

# Цвета
SKY_BLUE = (135, 206, 235)
SAND = (237, 201, 175)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
SILVER = (192, 192, 192)
DARK_PURPLE = (60, 0, 60)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)

# Параметры игрока
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

# Система частиц
class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Гравитация для частиц
        self.lifetime -= 1
        
    def draw(self, surface):
        alpha = self.lifetime / self.max_lifetime
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y, vx, vy, color, lifetime=30, size=5):
        self.particles.append(Particle(x, y, vx, vy, color, lifetime, size))
        
    def add_explosion(self, x, y, color, count=15):
        for _ in range(count):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            self.add_particle(x, y, vx, vy, color, random.randint(20, 40), random.randint(3, 8))
            
    def add_sword_trail(self, x, y, facing_right):
        vx = 3 if facing_right else -3
        self.add_particle(x, y, vx, 0, WHITE, 15, 4)
        
    def add_magic_effect(self, x, y, color):
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            vx = math.cos(angle) * 3
            vy = math.sin(angle) * 3
            self.add_particle(x, y, vx, vy, color, 40, 6)
        
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


# Звуковой менеджер
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
        
    def create_sounds(self):
        self.sounds['jump'] = self.create_beep(400, 0.1, 'sine')
        self.sounds['coin'] = self.create_beep(800, 0.15, 'square')
        self.sounds['hit'] = self.create_beep(150, 0.2, 'sawtooth')
        self.sounds['sword'] = self.create_beep(600, 0.08, 'triangle')
        self.sounds['powerup'] = self.create_beep(500, 0.3, 'sine')
        self.sounds['damage'] = self.create_beep(200, 0.3, 'sawtooth')
        self.sounds['win'] = self.create_beep(600, 0.5, 'sine')
        self.sounds['magic'] = self.create_beep(700, 0.2, 'sine')
        self.sounds['dash'] = self.create_beep(300, 0.15, 'triangle')
        
    def create_beep(self, freq, duration, wave_type):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray(n_samples * 2)
        
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'sine':
                value = int(10000 * math.sin(2 * math.pi * freq * t))
            elif wave_type == 'square':
                value = 10000 if math.sin(2 * math.pi * freq * t) > 0 else -10000
            elif wave_type == 'sawtooth':
                value = int(10000 * (2 * (t * freq - math.floor(t * freq + 0.5))))
            elif wave_type == 'triangle':
                value = int(10000 * (2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1))
            else:
                value = 0
            
            value = max(-32767, min(32767, value))
            struct = __import__('struct')
            packed = struct.pack('<h', value)
            buf[i * 2:i * 2 + 2] = packed
            
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(0.3)
        return sound
    
    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()


# Менеджер комбо
class ComboManager:
    def __init__(self):
        self.combo_count = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.last_hit_time = 0
        
    def add_hit(self, current_time):
        if current_time - self.last_hit_time < 2000:
            self.combo_count += 1
            if self.combo_count > self.max_combo:
                self.max_combo = self.combo_count
        else:
            self.combo_count = 1
        self.last_hit_time = current_time
        self.combo_timer = 120
        
    def update(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
            
    def get_multiplier(self):
        if self.combo_count >= 10:
            return 3.0
        elif self.combo_count >= 5:
            return 2.0
        elif self.combo_count >= 3:
            return 1.5
        return 1.0
    
    def reset(self):
        self.combo_count = 0
        self.combo_timer = 0


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True
        self.is_attacking = False
        self.attack_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.health = 3
        self.max_health = 3
        self.attack_hit = False
        self.combo_count = 0
        self.super_attack_ready = False
        self.super_meter = 0
        self.max_super_meter = 100
        self.double_jump_available = False
        self.high_jump = False
        
        # Боевые приёмы
        self.dash_available = True
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.is_dashing = False
        self.jump_attack = False
        self.can_jump_attack = True
        
        # Магия
        self.magic_mode = False
        self.magic_timer = 0
        self.fireball_available = True
        self.fireball_cooldown = 0
        
        # Анимация
        self.frame_index = 0
        self.animation_timer = 0
        self.state = "idle"
        
    def update(self, platforms, keys):
        dx = 0
        
        # Dash (уклонение)
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.invincible = True
            dx = PLAYER_SPEED * 3 if self.facing_right else -PLAYER_SPEED * 3
            if self.dash_timer == 0:
                self.is_dashing = False
                self.invincible = False
        else:
            # Обычное движение
            if keys[pygame.K_LEFT]:
                dx = -PLAYER_SPEED
                self.facing_right = False
                self.state = "run" if self.on_ground else "jump"
            elif keys[pygame.K_RIGHT]:
                dx = PLAYER_SPEED
                self.facing_right = True
                self.state = "run" if self.on_ground else "jump"
            else:
                self.state = "idle" if self.on_ground else "jump"
        
        # Кулдауны
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_cooldown <= 0:
            self.dash_available = True
            
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        if self.fireball_cooldown <= 0:
            self.fireball_available = True
            
        # Магия
        if self.magic_timer > 0:
            self.magic_timer -= 1
            if self.magic_timer <= 0:
                self.magic_mode = False
        
        # Атака мечом
        if keys[pygame.K_SPACE] and self.attack_timer == 0 and self.dash_timer == 0:
            self.is_attacking = True
            self.attack_timer = 25
            self.attack_hit = False
            self.state = "attack"
            self.combo_count = min(self.combo_count + 1, 5)
            
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 15 and not self.attack_hit:
                self.attack_hit = True
            if self.attack_timer == 0:
                self.is_attacking = False
                self.attack_hit = False
        
        # Супер-атака
        if self.super_meter >= self.max_super_meter:
            self.super_attack_ready = True
        
        # Неуязвимость
        if self.invincible and self.dash_timer == 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        self.rect.x += dx
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        
        prev_y = self.rect.y
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and prev_y + self.rect.height <= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.double_jump_available = True
                    self.can_jump_attack = True
                elif self.vel_y < 0 and prev_y >= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        # Анимация
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 4
            
    def do_jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE * (1.2 if self.high_jump else 1.0)
            self.on_ground = False
            self.state = "jump"
            self.double_jump_available = True
            self.can_jump_attack = True
            return True
        elif self.double_jump_available:
            self.vel_y = JUMP_FORCE * 0.8
            self.double_jump_available = False
            self.state = "jump"
            return True
        return False
        
    def do_dash(self):
        if self.dash_available and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = 15
            self.dash_cooldown = 60
            self.dash_available = False
            return True
        return False
    
    def do_jump_attack(self):
        if self.can_jump_attack and not self.on_ground:
            self.is_attacking = True
            self.attack_timer = 20
            self.attack_hit = True
            self.jump_attack = True
            self.can_jump_attack = False
            return True
        return False
        
    def do_fireball(self):
        if self.fireball_available:
            self.fireball_cooldown = 90
            self.fireball_available = False
            return True
        return False
        
    def activate_magic(self):
        if self.super_meter >= 50:
            self.super_meter -= 50
            self.magic_mode = True
            self.magic_timer = 300  # 5 секунд
            return True
        return False
            
    def draw(self, surface):
        # Мигание при неуязвимости
        if self.invincible and self.invincible_timer % 4 < 2 and self.dash_timer == 0:
            return
            
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        # Аура при магии
        if self.magic_mode:
            pygame.draw.ellipse(surface, CYAN, (x - 15, y - 15, w + 30, h + 30), 3)
        
        # След от dash
        if self.is_dashing:
            for i in range(3):
                alpha = i * 30
                color = (255, 255, 255, alpha)
                offset_x = -i * 10 if self.facing_right else i * 10
                pygame.draw.rect(surface, (200, 200, 200), (x + offset_x, y, w, h))
        
        # Ноги
        leg_offset = 0
        if self.state == "run" and not self.is_dashing:
            leg_offset = int(5 * math.sin(self.frame_index * math.pi / 2))
        
        pygame.draw.rect(surface, DARK_BROWN, (x + 5, y + h - 15 - leg_offset, 12, 15))
        pygame.draw.rect(surface, DARK_BROWN, (x + w - 17, y + h - 15 + leg_offset, 12, 15))
        
        # Тело
        color = RED if not self.magic_mode else CYAN
        pygame.draw.rect(surface, color, (x, y + 20, w, h - 35))
        pygame.draw.rect(surface, GOLD, (x, y + 35, w, 8))
        
        # Голова
        head_rect = pygame.Rect(x + 5, y - 10, 30, 30)
        pygame.draw.rect(surface, SAND, head_rect)
        
        # Тюрбан
        pygame.draw.rect(surface, WHITE, (x + 3, y - 15, 34, 10))
        pygame.draw.circle(surface, GOLD, (x + 18, y - 20), 5)
        
        # Глаза
        eye_x = x + 22 if self.facing_right else x + 8
        pygame.draw.circle(surface, BLACK, (eye_x, y + 5), 3)
        
        # Меч
        if self.is_attacking:
            sword_x = self.rect.right if self.facing_right else self.rect.left - 35
            sword_len = 35 + self.combo_count * 5
            
            if self.jump_attack:
                # Удар в прыжке - меч больше
                sword_len += 20
                color = GOLD
            elif self.magic_mode:
                color = CYAN
            else:
                color = WHITE
            
            pygame.draw.rect(surface, GOLD, (sword_x, y + 25, 10, 8))
            
            if self.facing_right:
                points = [(sword_x + 10, y + 25), (sword_x + sword_len, y + 29), (sword_x + 10, y + 33)]
            else:
                points = [(sword_x, y + 25), (sword_x, y + 33), (sword_x - sword_len, y + 29)]
            pygame.draw.polygon(surface, color, points)
    
    def add_super_meter(self, amount):
        self.super_meter = min(self.max_super_meter, self.super_meter + amount)
        
    def use_super_attack(self):
        if self.super_attack_ready:
            self.super_meter = 0
            self.super_attack_ready = False
            return True
        return False
                    
    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = 60
            self.combo_count = 0
            return True
        return False


# Огненный шар
class Fireball:
    def __init__(self, x, y, facing_right):
        self.rect = pygame.Rect(x, y, 30, 20)
        self.speed = 10 if facing_right else -10
        self.facing_right = facing_right
        self.lifetime = 60
        self.damage = 2
        
    def update(self):
        self.rect.x += self.speed
        self.lifetime -= 1
        
    def draw(self, surface):
        # Огненный шар с анимацией
        offset = random.randint(-2, 2)
        pygame.draw.ellipse(surface, ORANGE, (self.rect.x, self.rect.y + offset, 30, 20))
        pygame.draw.ellipse(surface, YELLOW, (self.rect.x + 5, self.rect.y + offset + 3, 20, 14))
        pygame.draw.ellipse(surface, WHITE, (self.rect.x + 10, self.rect.y + offset + 5, 10, 10))
        
    def is_alive(self):
        return self.lifetime > 0 and 0 < self.rect.x < WIDTH


# Сундук с сокровищами
class TreasureChest:
    def __init__(self, x, y, contents):
        self.rect = pygame.Rect(x, y, 40, 30)
        self.contents = contents  # 'health', 'coins', 'super'
        self.opened = False
        
    def draw(self, surface):
        if self.opened:
            # Открытый сундук
            pygame.draw.rect(surface, BROWN, (self.rect.x, self.rect.y + 15, 40, 15))
            pygame.draw.rect(surface, DARK_BROWN, (self.rect.x, self.rect.y, 40, 15))
        else:
            # Закрытый сундук
            pygame.draw.rect(surface, BROWN, (self.rect.x, self.rect.y, 40, 30))
            pygame.draw.rect(surface, GOLD, (self.rect.x + 15, self.rect.y + 12, 10, 8))
            # Замок
            pygame.draw.circle(surface, GOLD, (self.rect.x + 20, self.rect.y + 16), 4)
            
    def open(self):
        if not self.opened:
            self.opened = True
            return self.contents
        return None


# Бонусный уровень (секретная комната)
class BonusRoom:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.chests = []
        self.enemies = []
        self.coins = []
        self.exit_x = x + width - 50
        self.exit_y = y + height - 50
        
    def draw(self, surface):
        # Границы комнаты
        pygame.draw.rect(surface, DARK_BROWN, self.rect, 5)
        
        # Выход
        pygame.draw.rect(surface, BROWN, (self.exit_x, self.exit_y, 40, 50))
        
        for chest in self.chests:
            chest.draw(surface)


# Глобальные менеджеры
sound_manager = None
combo_manager = None
particle_system = None


# Остальные классы
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.float_offset = random.random() * math.pi * 2
        self.collected = False
        
    def update(self):
        self.float_offset += 0.15
        
    def draw(self, surface):
        if self.collected:
            return
        y_offset = int(4 * abs(math.sin(self.float_offset)))
        cx, cy = self.rect.centerx, self.rect.centery - y_offset
        pygame.draw.circle(surface, GOLD, (cx, cy), 10)
        pygame.draw.circle(surface, (255, 255, 150), (cx - 3, cy - 3), 4)
        pygame.draw.circle(surface, WHITE, (cx - 2, cy - 2), 2)


class HealthPotion:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 30)
        self.float_offset = 0
        self.collected = False
        
    def update(self):
        self.float_offset += 0.1
        
    def draw(self, surface):
        if self.collected:
            return
        y_offset = int(3 * abs(math.sin(self.float_offset)))
        x, y = self.rect.x, self.rect.y + 5 - y_offset
        pygame.draw.rect(surface, (100, 100, 255), (x + 8, y + 10, 9, 15))
        pygame.draw.rect(surface, BROWN, (x + 10, y + 5, 5, 5))
        pygame.draw.circle(surface, (150, 150, 255), (x + 12, y + 15), 6)
        pygame.draw.circle(surface, WHITE, (x + 10, y + 13), 2)


class ShieldBonus:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.float_offset = 0
        self.collected = False
        
    def update(self):
        self.float_offset += 0.1
        
    def draw(self, surface):
        if self.collected:
            return
        y_offset = int(3 * abs(math.sin(self.float_offset)))
        cx, cy = self.rect.centerx, self.rect.centery - y_offset
        pygame.draw.polygon(surface, (100, 100, 200), [(cx, cy + 15), (cx - 12, cy + 5), (cx - 12, cy - 10), (cx + 12, cy - 10), (cx + 12, cy + 5)])
        pygame.draw.polygon(surface, GOLD, [(cx, cy + 15), (cx - 12, cy + 5), (cx - 12, cy - 10), (cx + 12, cy - 10), (cx + 12, cy + 5)], 2)
        pygame.draw.rect(surface, WHITE, (cx - 3, cy - 8, 6, 16))
        pygame.draw.rect(surface, WHITE, (cx - 8, cy - 3, 16, 6))


class SuperMeterBonus:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.float_offset = 0
        self.collected = False
        
    def update(self):
        self.float_offset += 0.1
        
    def draw(self, surface):
        if self.collected:
            return
        y_offset = int(3 * abs(math.sin(self.float_offset)))
        cx, cy = self.rect.centerx, self.rect.centery - y_offset
        pygame.draw.polygon(surface, PURPLE, [(cx, cy - 12), (cx - 8, cy), (cx, cy + 12), (cx + 8, cy)])
        pygame.draw.polygon(surface, (200, 100, 200), [(cx, cy - 12), (cx - 8, cy), (cx, cy + 12), (cx + 8, cy)], 2)
        pygame.draw.circle(surface, WHITE, (cx - 3, cy - 5), 2)


class Spring:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 20)
        self.compressed = False
        self.compress_timer = 0
        self.cooldown = 0

    def update(self, player):
        global sound_manager
        
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.compressed:
            self.compress_timer -= 1
            if self.compress_timer <= 0:
                self.compressed = False

        if self.cooldown == 0:
            if (player.rect.centerx >= self.rect.left and 
                player.rect.centerx <= self.rect.right and
                player.rect.bottom >= self.rect.top and
                player.rect.bottom <= self.rect.top + 25 and
                player.vel_y >= -5):
                self.compressed = True
                self.cooldown = 30
                player.vel_y = -25
                player.double_jump_available = True
                if sound_manager:
                    sound_manager.play('jump')
                return True
        return False

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        pygame.draw.rect(surface, (100, 100, 100), (x, y + 10, 40, 10))
        height = 5 if self.compressed else 15
        for i in range(5):
            offset = i * 3
            pygame.draw.line(surface, SILVER, (x + 5, y + 10 - offset), (x + 35, y + 10 - offset - height), 4)


# Лестница для лазания
class Ladder:
    def __init__(self, x, y, height):
        self.rect = pygame.Rect(x, y - height, 50, height)
        self.climbing = False
        self.climb_speed = 3
        
    def update(self, player, keys):
        if (player.rect.centerx >= self.rect.left and 
            player.rect.centerx <= self.rect.right and
            player.rect.bottom >= self.rect.top):
            self.climbing = True
            if keys[pygame.K_UP]:
                player.rect.y -= self.climb_speed
                player.vel_y = 0
            if keys[pygame.K_DOWN]:
                player.rect.y += self.climb_speed
                player.vel_y = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.climbing = False
                return False
            return True
        else:
            self.climbing = False
            return False
            
    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        h = self.rect.height
        
        pygame.draw.line(surface, BROWN, (x, y), (x, y + h), 6)
        pygame.draw.line(surface, BROWN, (x + 50, y), (x + 50, y + h), 6)
        
        for i in range(0, h, 20):
            pygame.draw.line(surface, DARK_BROWN, (x, y + i), (x + 50, y + i), 4)


# Телепорт
class Teleporter:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 50, 70)
        self.target_x = target_x
        self.target_y = target_y
        self.timer = 0
        self.activation_delay = 30  # 0.5 секунды при 60 FPS
        self.activating = False  # Флаг активации

    def activate(self, player):
        # Проверяем, что игрок достаточно близко к порталу
        center_dist_x = abs(player.rect.centerx - self.rect.centerx)
        center_dist_y = abs(player.rect.centery - self.rect.centery)
        
        if center_dist_x < 60 and center_dist_y < 80:
            self.activating = True
            self.timer += 1
            if self.timer >= self.activation_delay:
                player.rect.x = self.target_x
                player.rect.y = self.target_y
                player.vel_y = 0
                self.timer = 0
                self.activating = False
                return True
        else:
            self.timer = 0
            self.activating = False
        return False
    
    def update(self):
        # Постепенный сброс таймера если не активируется
        if not self.activating and self.timer > 0:
            self.timer -= 1
    
    def draw(self, surface):
        x, y = self.rect.x, self.rect.y

        intensity = int(100 + 100 * math.sin(pygame.time.get_ticks() / 50))
        color = (intensity, intensity, 255) if self.timer > 0 else (100, 100, 255)

        pygame.draw.ellipse(surface, color, (x, y, 50, 70))
        pygame.draw.ellipse(surface, (150, 150, 255), (x + 5, y + 5, 40, 60), 2)

        if self.timer > 20:
            pygame.draw.ellipse(surface, WHITE, (x + 15, y + 20, 20, 30))

        if self.timer > 0:
            bar_width = int(40 * (self.timer / self.activation_delay))
            pygame.draw.rect(surface, GOLD, (x + 5, y - 10, bar_width, 5))


class Enemy:
    def __init__(self, x, y, patrol_distance, enemy_type="guard"):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.speed = 2 if enemy_type == "guard" else 3
        self.direction = 1
        self.type = enemy_type
        self.health = 2 if enemy_type == "guard" else 1
        self.frame_index = 0
        self.hit_flash = 0
        
    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
        self.frame_index = (self.frame_index + 1) % 4
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
    def take_hit(self):
        self.hit_flash = 10
        
    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            color = WHITE
        else:
            color = None
        
        if self.type == "guard":
            leg_offset = int(4 * math.sin(self.frame_index * math.pi / 2))
            pygame.draw.rect(surface, DARK_GREEN, (x + 5, y + 35 - leg_offset, 12, 15))
            pygame.draw.rect(surface, DARK_GREEN, (x + 23, y + 35 + leg_offset, 12, 15))
            pygame.draw.rect(surface, GREEN, (x, y + 15, 40, 25))
            pygame.draw.rect(surface, SAND, (x + 5, y, 30, 20))
            pygame.draw.rect(surface, WHITE, (x + 3, y - 3, 34, 8))
            pygame.draw.circle(surface, RED, (x + 12, y + 10), 3)
            pygame.draw.circle(surface, RED, (x + 28, y + 10), 3)
            pygame.draw.line(surface, BROWN, (x + 35, y + 20), (x + 35, y - 10), 3)
            pygame.draw.polygon(surface, SILVER, [(x + 35, y - 10), (x + 30, y), (x + 40, y)])
        else:
            wing_offset = int(8 * math.sin(self.frame_index * math.pi / 2))
            pygame.draw.ellipse(surface, PURPLE, (x - 5, y + 10 - wing_offset, 15, 20))
            pygame.draw.ellipse(surface, PURPLE, (x + 30, y + 10 + wing_offset, 15, 20))
            pygame.draw.ellipse(surface, DARK_PURPLE, (x + 5, y + 15, 30, 25))
            pygame.draw.circle(surface, PURPLE, (x + 20, y + 10), 12)
            pygame.draw.circle(surface, (255, 255, 0), (x + 15, y + 8), 4)
            pygame.draw.circle(surface, (255, 255, 0), (x + 25, y + 8), 4)
            pygame.draw.circle(surface, BLACK, (x + 15, y + 8), 2)
            pygame.draw.circle(surface, BLACK, (x + 25, y + 8), 2)


class Boss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 100)
        self.health = 10
        self.max_health = 10
        self.timer = 0
        self.direction = 1
        self.speed = 1.5
        self.min_x = 100
        self.max_x = WIDTH - 100
        self.hit_flash = 0

    def update(self):
        self.timer += 1
        if self.timer % 120 < 60:
            if self.rect.left <= self.min_x:
                self.direction = 1
            elif self.rect.right >= self.max_x:
                self.direction = -1
            self.rect.x += self.speed * self.direction
        self.rect.x = max(self.min_x, min(self.rect.x, self.max_x - self.rect.width))
        if self.hit_flash > 0:
            self.hit_flash -= 1
            
    def take_hit(self):
        self.hit_flash = 10

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            body_color = WHITE
        else:
            body_color = PURPLE
        
        pygame.draw.rect(surface, body_color, (x, y + 40, 80, 60))
        pygame.draw.polygon(surface, DARK_PURPLE, [(x, y + 100), (x + 40, y + 40), (x + 80, y + 100)])
        pygame.draw.rect(surface, SAND, (x + 15, y, 50, 45))
        pygame.draw.rect(surface, BLACK, (x + 20, y - 30, 40, 35))
        pygame.draw.circle(surface, GOLD, (x + 40, y - 35), 8)
        pygame.draw.arc(surface, BLACK, (x + 25, y + 25, 30, 15), 3.14, 0, 3)
        pygame.draw.ellipse(surface, (255, 200, 0), (x + 22, y + 12, 12, 8))
        pygame.draw.ellipse(surface, (255, 200, 0), (x + 46, y + 12, 12, 8))
        pygame.draw.circle(surface, BLACK, (x + 28, y + 16), 3)
        pygame.draw.circle(surface, BLACK, (x + 52, y + 16), 3)
        pygame.draw.polygon(surface, BLACK, [(x + 25, y + 35), (x + 40, y + 55), (x + 55, y + 35)])
        
        bar_width = 100
        bar_x = WIDTH // 2 - bar_width // 2
        pygame.draw.rect(surface, RED, (bar_x, 20, bar_width, 8))
        pygame.draw.rect(surface, GREEN, (bar_x, 20, bar_width * self.health / self.max_health, 8))
        pygame.draw.rect(surface, WHITE, (bar_x, 20, bar_width, 8), 2)


class Platform:
    def __init__(self, x, y, width, height, platform_type="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        
    def draw(self, surface):
        if self.type == "ground":
            pygame.draw.rect(surface, DARK_GREEN, self.rect)
            pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top, self.rect.width, 10))
        elif self.type == "stone":
            pygame.draw.rect(surface, (128, 128, 128), self.rect)
            for i in range(0, self.rect.width, 30):
                for j in range(0, self.rect.height, 20):
                    pygame.draw.rect(surface, (100, 100, 100), (self.rect.left + i, self.rect.top + j, 28, 18), 2)
        else:
            pygame.draw.rect(surface, BROWN, self.rect)
            pygame.draw.line(surface, SAND, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.bonuses = []
        self.springs = []
        self.chests = []
        self.ladders = []
        self.teleporters = []
        self.bonus_rooms = []
        self.boss = None
        self.start_pos = (100, HEIGHT - 150)
        self.background_color = SKY_BLUE

        self.create_level()

    def create_level(self):
        if self.level_num == 1:
            self.background_color = SKY_BLUE

            self.platforms.append(Platform(0, HEIGHT - 50, WIDTH, 50, "ground"))
            self.platforms.append(Platform(200, HEIGHT - 150, 150, 20))
            self.platforms.append(Platform(450, HEIGHT - 250, 150, 20))
            self.platforms.append(Platform(100, HEIGHT - 350, 200, 20))
            self.platforms.append(Platform(550, HEIGHT - 400, 200, 20))
            self.platforms.append(Platform(300, HEIGHT - 500, 200, 20))

            self.coins.extend([Coin(250, HEIGHT - 190), Coin(500, HEIGHT - 290), Coin(150, HEIGHT - 390),
                              Coin(600, HEIGHT - 440), Coin(700, HEIGHT - 440), Coin(350, HEIGHT - 540), Coin(400, HEIGHT - 540)])

            self.enemies.extend([Enemy(300, HEIGHT - 100, 100, "guard"), Enemy(500, HEIGHT - 300, 80, "guard")])
            self.bonuses.extend([HealthPotion(50, HEIGHT - 90), SuperMeterBonus(750, HEIGHT - 90)])
            self.springs.append(Spring(650, HEIGHT - 50))
            
            # Лестницы
            self.ladders.append(Ladder(380, HEIGHT - 50, 100))
            self.ladders.append(Ladder(530, HEIGHT - 250, 100))

            # Бонусная комната
            bonus_room = BonusRoom(50, 50, 150, 100)
            bonus_room.chests.append(TreasureChest(100, 100, 'health'))
            bonus_room.coins.append(Coin(80, 120))
            bonus_room.coins.append(Coin(120, 120))
            self.bonus_rooms.append(bonus_room)

        elif self.level_num == 2:
            self.background_color = (50, 50, 80)
            self.start_pos = (50, HEIGHT - 150)

            self.platforms.append(Platform(0, HEIGHT - 50, WIDTH, 50, "stone"))
            self.platforms.append(Platform(150, HEIGHT - 140, 120, 20, "stone"))
            self.platforms.append(Platform(350, HEIGHT - 220, 120, 20, "stone"))
            self.platforms.append(Platform(550, HEIGHT - 300, 120, 20, "stone"))
            self.platforms.append(Platform(350, HEIGHT - 380, 120, 20, "stone"))
            self.platforms.append(Platform(150, HEIGHT - 460, 120, 20, "stone"))
            self.platforms.append(Platform(500, HEIGHT - 520, 250, 20, "stone"))

            self.coins.extend([Coin(200, HEIGHT - 180), Coin(400, HEIGHT - 260), Coin(600, HEIGHT - 340),
                              Coin(400, HEIGHT - 420), Coin(200, HEIGHT - 500), Coin(550, HEIGHT - 560),
                              Coin(650, HEIGHT - 560), Coin(700, HEIGHT - 560)])

            self.enemies.extend([Enemy(200, HEIGHT - 100, 80, "guard"), Enemy(400, HEIGHT - 280, 60, "fly"),
                                Enemy(600, HEIGHT - 360, 60, "fly")])
            self.bonuses.extend([HealthPotion(30, HEIGHT - 90), ShieldBonus(700, HEIGHT - 90), SuperMeterBonus(350, HEIGHT - 260)])
            self.springs.append(Spring(100, HEIGHT - 50))
            
            # Лестницы
            self.ladders.append(Ladder(250, HEIGHT - 50, 140))
            self.ladders.append(Ladder(500, HEIGHT - 300, 80))

        elif self.level_num == 3:
            self.background_color = (180, 150, 200)
            self.start_pos = (100, HEIGHT - 150)

            self.platforms.append(Platform(0, HEIGHT - 50, WIDTH, 50, "stone"))
            self.platforms.append(Platform(100, HEIGHT - 180, 150, 20, "stone"))
            self.platforms.append(Platform(550, HEIGHT - 180, 150, 20, "stone"))
            self.platforms.append(Platform(300, HEIGHT - 300, 200, 20, "stone"))

            self.coins.extend([Coin(150, HEIGHT - 220), Coin(600, HEIGHT - 220),
                              Coin(350, HEIGHT - 340), Coin(400, HEIGHT - 340), Coin(450, HEIGHT - 340)])

            self.boss = Boss(WIDTH - 150, HEIGHT - 150)
            self.bonuses.append(SuperMeterBonus(350, HEIGHT - 340))
            
            # Телепорты на 3 уровне
            self.teleporters.append(Teleporter(50, HEIGHT - 120, 700, HEIGHT - 230))
            self.teleporters.append(Teleporter(700, HEIGHT - 250, 50, HEIGHT - 200))


class Game:
    def __init__(self):
        global sound_manager, combo_manager, particle_system
        sound_manager = SoundManager()
        combo_manager = ComboManager()
        particle_system = ParticleSystem()
        
        self.current_level = 1
        self.level = Level(self.current_level)
        self.player = Player(*self.level.start_pos)
        self.fireballs = []
        self.score = 0
        self.level_complete = False
        self.game_over = False
        self.victory = False
        self.boss_defeated = False
        self.in_bonus_room = False
        self.current_bonus_room = None
        
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        self.level = Level(level_num)
        self.player.rect.x, self.player.rect.y = self.level.start_pos
        self.player.vel_y = 0
        self.player.combo_count = 0
        self.player.super_meter = 0
        self.fireballs = []
        self.level_complete = False
        combo_manager.reset()
        particle_system = ParticleSystem()
        
    def check_collisions(self):
        # Пружины
        for spring in self.level.springs:
            spring.update(self.player)
        
        # Огненные шары
        for fireball in self.fireballs[:]:
            fireball.update()
            if not fireball.is_alive():
                self.fireballs.remove(fireball)
                continue
                
            # Попадание огненного шара во врагов
            for enemy in self.level.enemies[:]:
                if fireball.rect.colliderect(enemy.rect):
                    enemy.health -= fireball.damage
                    enemy.take_hit()
                    particle_system.add_explosion(fireball.rect.centerx, fireball.rect.centery, ORANGE, 10)
                    if fireball in self.fireballs:
                        self.fireballs.remove(fireball)
                    if enemy.health <= 0:
                        self.level.enemies.remove(enemy)
                        self.score += int(50 * combo_manager.get_multiplier())
                        particle_system.add_explosion(enemy.rect.centerx, enemy.rect.centery, GREEN, 20)
                    break
                    
            # Попадание в босса
            if self.level.boss and fireball in self.fireballs:
                if fireball.rect.colliderect(self.level.boss.rect):
                    self.level.boss.health -= fireball.damage
                    self.level.boss.take_hit()
                    particle_system.add_explosion(fireball.rect.centerx, fireball.rect.centery, ORANGE, 10)
                    if fireball in self.fireballs:
                        self.fireballs.remove(fireball)
                    if self.level.boss.health <= 0:
                        self.boss_defeated = True
                        self.level.boss = None
                        self.score += 500
                        particle_system.add_explosion(self.level.boss.rect.centerx, self.level.boss.rect.centery, PURPLE, 50)
                        sound_manager.play('win')
        
        # Монетки
        for coin in self.level.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.score += int(10 * combo_manager.get_multiplier())
                sound_manager.play('coin')
                combo_manager.add_hit(pygame.time.get_ticks())
                self.player.add_super_meter(5)
                particle_system.add_particle(coin.rect.centerx, coin.rect.centery, 0, -3, GOLD, 20, 4)
                
        # Бонусы
        for bonus in self.level.bonuses:
            if not bonus.collected and self.player.rect.colliderect(bonus.rect):
                bonus.collected = True
                sound_manager.play('powerup')
                particle_system.add_magic_effect(bonus.rect.centerx, bonus.rect.centery, GOLD)
                if isinstance(bonus, HealthPotion):
                    self.player.health = min(self.player.health + 1, self.player.max_health)
                    self.score += 25
                elif isinstance(bonus, ShieldBonus):
                    self.player.invincible = True
                    self.player.invincible_timer = 300
                    self.score += 25
                elif isinstance(bonus, SuperMeterBonus):
                    self.player.add_super_meter(30)
                    self.score += 25
        
        # Сундуки
        for chest in self.level.chests:
            if not chest.opened and self.player.rect.colliderect(chest.rect):
                contents = chest.open()
                sound_manager.play('powerup')
                particle_system.add_magic_effect(chest.rect.centerx, chest.rect.centery, GOLD)
                if contents == 'health':
                    self.player.health = min(self.player.health + 1, self.player.max_health)
                elif contents == 'super':
                    self.player.add_super_meter(50)
                self.score += 100
        
        # Враги
        for enemy in self.level.enemies[:]:
            if self.player.is_attacking and self.player.attack_hit:
                attack_range = 70 + self.player.combo_count * 8
                hit = False
                
                if self.player.facing_right:
                    if (enemy.rect.left < self.player.rect.right + attack_range and
                        enemy.rect.right > self.player.rect.right and
                        abs(enemy.rect.centery - self.player.rect.centery) < 50):
                        hit = True
                else:
                    if (enemy.rect.right > self.player.rect.left - attack_range and
                        enemy.rect.left < self.player.rect.left and
                        abs(enemy.rect.centery - self.player.rect.centery) < 50):
                        hit = True

                if hit:
                    enemy.health -= 1
                    enemy.take_hit()
                    sound_manager.play('sword')
                    particle_system.add_sword_trail(self.player.rect.centerx, self.player.rect.centery, self.player.facing_right)
                    if enemy.health <= 0:
                        self.level.enemies.remove(enemy)
                        self.score += int(50 * combo_manager.get_multiplier())
                        combo_manager.add_hit(pygame.time.get_ticks())
                        self.player.add_super_meter(20)
                        particle_system.add_explosion(enemy.rect.centerx, enemy.rect.centery, GREEN, 20)
            elif self.player.rect.colliderect(enemy.rect):
                if self.player.take_damage(1):
                    sound_manager.play('damage')
                    self.score = max(0, self.score - 10)
                    combo_manager.reset()
                    particle_system.add_explosion(self.player.rect.centerx, self.player.rect.centery, RED, 15)
        
        # Босс
        if self.level.boss:
            boss = self.level.boss
            if self.player.is_attacking and self.player.attack_hit:
                attack_range = 80
                hit = False
                
                if self.player.facing_right:
                    if (boss.rect.left < self.player.rect.right + attack_range and
                        boss.rect.right > self.player.rect.right and
                        abs(boss.rect.centery - self.player.rect.centery) < 80):
                        hit = True
                else:
                    if (boss.rect.right > self.player.rect.left - attack_range and
                        boss.rect.left < self.player.rect.left and
                        abs(boss.rect.centery - self.player.rect.centery) < 80):
                        hit = True

                if hit:
                    boss.health -= 1
                    boss.take_hit()
                    sound_manager.play('sword')
                    self.score += 10
                    combo_manager.add_hit(pygame.time.get_ticks())
                    particle_system.add_sword_trail(self.player.rect.centerx, self.player.rect.centery, self.player.facing_right)
            elif self.player.rect.colliderect(boss.rect):
                if self.player.take_damage(1):
                    sound_manager.play('damage')
                    self.score = max(0, self.score - 10)
                    combo_manager.reset()
                    particle_system.add_explosion(self.player.rect.centerx, self.player.rect.centery, RED, 15)

            if boss.health <= 0:
                self.boss_defeated = True
                self.level.boss = None
                self.score += 500
                sound_manager.play('win')
                particle_system.add_explosion(boss.rect.centerx, boss.rect.centery, PURPLE, 50)
                
        # Падение
        if self.player.rect.top > HEIGHT:
            self.player.health -= 1
            sound_manager.play('damage')
            if self.player.health <= 0:
                self.game_over = True
            else:
                self.player.rect.x, self.player.rect.y = self.level.start_pos
                self.player.vel_y = 0
                combo_manager.reset()
                
        # Проверка завершения уровня
        all_coins = all(c.collected for c in self.level.coins)
        all_enemies = len(self.level.enemies) == 0
        
        if self.level.boss:
            if self.boss_defeated:
                self.level_complete = True
        else:
            if all_coins and all_enemies:
                self.level_complete = True
                
        if self.level_complete and self.current_level == 3:
            self.victory = True
            
        if self.player.health <= 0:
            self.game_over = True
            
    def next_level(self):
        self.current_level += 1
        if self.current_level > 3:
            self.victory = True
        else:
            self.load_level(self.current_level)
            
    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        
        # Здоровье
        for i in range(self.player.max_health):
            color = RED if i < self.player.health else (100, 100, 100)
            pygame.draw.circle(screen, color, (20 + i * 25, 20), 10)
            pygame.draw.circle(screen, WHITE, (20 + i * 25, 20), 10, width=2)
        
        # Счёт
        score_text = font.render(f"Счёт: {self.score}", True, BLACK)
        screen.blit(score_text, (WIDTH - 150, 10))
        
        # Уровень
        level_text = font.render(f"Уровень: {self.current_level}", True, BLACK)
        screen.blit(level_text, (WIDTH // 2 - 60, 10))
        
        # Комбо
        if combo_manager.combo_count >= 2:
            combo_text = font.render(f"Комбо x{combo_manager.combo_count}!", True, RED)
            screen.blit(combo_text, (WIDTH // 2 - 50, 50))
            
        # Супер-метр
        meter_width = 100
        meter_height = 10
        meter_x = 10
        meter_y = HEIGHT - 60
        pygame.draw.rect(screen, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))
        fill_width = meter_width * self.player.super_meter / self.player.max_super_meter
        color = GOLD if self.player.super_attack_ready else PURPLE
        pygame.draw.rect(screen, color, (meter_x, meter_y, fill_width, meter_height))
        pygame.draw.rect(screen, WHITE, (meter_x, meter_y, meter_width, meter_height), 2)
        
        if self.player.super_attack_ready:
            super_text = font.render("SUPER!", True, GOLD)
            screen.blit(super_text, (meter_x + 20, meter_y - 25))
        
        # Кулдауны
        ability_y = HEIGHT - 30
        dash_text = font.render(f"Dash: {'✓' if self.player.dash_available else '○'}", True, CYAN if self.player.dash_available else (100, 100, 100))
        screen.blit(dash_text, (10, ability_y))
        
        fireball_text = font.render(f"Огонь: {'✓' if self.player.fireball_available else '○'}", True, ORANGE if self.player.fireball_available else (100, 100, 100))
        screen.blit(fireball_text, (120, ability_y))
        
    def draw_level_complete(self):
        font = pygame.font.Font(None, 72)
        text = font.render("УРОВЕНЬ ПРОЙДЕН!", True, GOLD)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        cont_text = font_small.render("Нажмите SPACE для следующего уровня", True, BLACK)
        cont_rect = cont_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(cont_text, cont_rect)
        
    def draw_game_over(self):
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Нажмите R для рестарта", True, BLACK)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)
        
    def draw_victory(self):
        font = pygame.font.Font(None, 72)
        text = font.render("ПОБЕДА!", True, GOLD)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        score_text = font_small.render(f"Итоговый счёт: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(score_text, score_rect)
        
        combo_text = font_small.render(f"Макс комбо: {combo_manager.max_combo}", True, BLACK)
        combo_rect = combo_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
        screen.blit(combo_text, combo_rect)
        
        restart_text = font_small.render("Нажмите R для новой игры", True, BLACK)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
        screen.blit(restart_text, restart_rect)
        
    def restart(self):
        self.__init__()
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        level_transition_timer = 0
        jump_pressed = False

        while running:
            clock.tick(60)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.game_over or self.victory):
                        self.restart()
                    if event.key == pygame.K_SPACE and self.level_complete and not self.victory:
                        if level_transition_timer > 30:
                            self.next_level()
                            level_transition_timer = 0
                    # Прыжок
                    if event.key == pygame.K_UP and not jump_pressed:
                        jump_pressed = True
                        if self.player.do_jump():
                            if sound_manager:
                                sound_manager.play('jump')
                    # Dash (уклонение) - клавиша X
                    if event.key == pygame.K_x:
                        if self.player.do_dash():
                            if sound_manager:
                                sound_manager.play('dash')
                    # Удар в прыжке - клавиша Z
                    if event.key == pygame.K_z:
                        if self.player.do_jump_attack():
                            if sound_manager:
                                sound_manager.play('sword')
                    # Огненный шар - клавиша C
                    if event.key == pygame.K_c:
                        if self.player.do_fireball():
                            fireball = Fireball(
                                self.player.rect.right if self.player.facing_right else self.player.rect.left,
                                self.player.rect.centery,
                                self.player.facing_right
                            )
                            self.fireballs.append(fireball)
                            if sound_manager:
                                sound_manager.play('magic')
                            particle_system.add_magic_effect(self.player.rect.centerx, self.player.rect.centery, ORANGE)
                    # Магия - клавиша V
                    if event.key == pygame.K_v:
                        if self.player.activate_magic():
                            if sound_manager:
                                sound_manager.play('powerup')
                            particle_system.add_magic_effect(self.player.rect.centerx, self.player.rect.centery, CYAN)
                    # Телепорт - клавиша A
                    if event.key == pygame.K_a:
                        for teleporter in self.level.teleporters:
                            if teleporter.activate(self.player):
                                if sound_manager:
                                    sound_manager.play('powerup')
                                particle_system.add_magic_effect(teleporter.rect.centerx, teleporter.rect.centery, CYAN)
                                break

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        jump_pressed = False

            if not self.game_over and not self.victory:
                if not self.level_complete:
                    self.player.update(self.level.platforms, keys)
                    # Лестницы
                    on_ladder = False
                    for ladder in self.level.ladders:
                        if ladder.update(self.player, keys):
                            on_ladder = True
                    # Телепорты
                    for teleporter in self.level.teleporters:
                        teleporter.update()
                    for coin in self.level.coins:
                        coin.update()
                    for bonus in self.level.bonuses:
                        bonus.update()
                    for enemy in self.level.enemies:
                        enemy.update()
                    if self.level.boss:
                        self.level.boss.update()

                    combo_manager.update()
                    self.check_collisions()
                    particle_system.update()
                else:
                    level_transition_timer += 1

            screen.fill(self.level.background_color)

            for platform in self.level.platforms:
                platform.draw(screen)

            for ladder in self.level.ladders:
                ladder.draw(screen)

            for spring in self.level.springs:
                spring.draw(screen)

            for coin in self.level.coins:
                coin.draw(screen)

            for bonus in self.level.bonuses:
                bonus.draw(screen)
                
            for chest in self.level.chests:
                chest.draw(screen)

            for enemy in self.level.enemies:
                enemy.draw(screen)

            if self.level.boss:
                self.level.boss.draw(screen)

            for fireball in self.fireballs:
                fireball.draw(screen)
                
            for teleporter in self.level.teleporters:
                teleporter.draw(screen)

            self.player.draw(screen)

            # Частицы
            particle_system.draw(screen)

            self.draw_hud()

            if self.level_complete and not self.victory:
                self.draw_level_complete()
            if self.game_over:
                self.draw_game_over()
            elif self.victory:
                self.draw_victory()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
