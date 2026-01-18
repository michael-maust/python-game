import pygame
import random
import sys
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 150, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_RED = (150, 0, 0)

# Player settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40

# Bullet settings
BULLET_SPEED = 7
BULLET_WIDTH = 4
BULLET_HEIGHT = 10

# Enemy settings
ENEMY_SPEED = 1
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_ROWS = 5
ENEMY_COLS = 10
ENEMY_SPACING = 60

# Enemy bullet settings
ENEMY_BULLET_SPEED = 3
ENEMY_SHOOT_CHANCE = 0.0005  # Probability per frame

# Particle settings
PARTICLE_COUNT = 15
PARTICLE_LIFETIME = 30

# Sound generation functions
def generate_shoot_sound():
    """Generate a shooting sound effect"""
    duration = 0.1
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = np.zeros((frames, 2), dtype=np.int16)
    max_sample = 2**(16 - 1) - 1
    
    for i in range(frames):
        # High frequency beep
        wave = int(max_sample * 0.3 * math.sin(2 * math.pi * 800 * i / sample_rate))
        arr[i][0] = wave
        arr[i][1] = wave
    
    sound = pygame.sndarray.make_sound(arr)
    sound.set_volume(0.3)
    return sound

def generate_explosion_sound():
    """Generate an explosion sound effect"""
    duration = 0.3
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = np.zeros((frames, 2), dtype=np.int16)
    max_sample = 2**(16 - 1) - 1
    
    for i in range(frames):
        # Noise-like explosion sound
        decay = 1.0 - (i / frames)
        freq = 200 + random.randint(-50, 50)
        wave = int(max_sample * 0.4 * decay * math.sin(2 * math.pi * freq * i / sample_rate))
        # Add some noise
        noise = random.randint(-1000, 1000) * decay
        arr[i][0] = int(wave + noise)
        arr[i][1] = int(wave + noise)
    
    sound = pygame.sndarray.make_sound(arr)
    sound.set_volume(0.4)
    return sound

def generate_background_music():
    """Generate background music"""
    duration = 2.0
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = np.zeros((frames, 2), dtype=np.int16)
    max_sample = 2**(16 - 1) - 1
    
    # Create a simple bass line
    notes = [220, 247, 262, 294, 330]  # A, B, C, D, E
    note_duration = frames // len(notes)
    
    for note_idx, freq in enumerate(notes):
        start_frame = note_idx * note_duration
        end_frame = min(start_frame + note_duration, frames)
        for i in range(start_frame, end_frame):
            wave = int(max_sample * 0.1 * math.sin(2 * math.pi * freq * i / sample_rate))
            arr[i][0] = wave
            arr[i][1] = wave
    
    sound = pygame.sndarray.make_sound(arr)
    sound.set_volume(0.2)
    return sound

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
        self.color = random.choice([YELLOW, ORANGE, RED, WHITE])
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.vy += 0.1  # Gravity effect
    
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = tuple(min(255, max(0, c)) for c in self.color[:3])
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
    
    def is_alive(self):
        return self.lifetime > 0

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.engine_glow = 0
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x
        self.rect.y = self.y
        self.engine_glow = (self.engine_glow + 5) % 360
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw engine glow (animated)
        glow_size = 8 + int(3 * math.sin(math.radians(self.engine_glow)))
        pygame.draw.circle(screen, CYAN, (center_x, self.y + self.height + 5), glow_size)
        pygame.draw.circle(screen, YELLOW, (center_x, self.y + self.height + 5), glow_size // 2)
        
        # Draw main body (detailed ship)
        # Main hull
        hull_points = [
            (center_x, self.y),
            (self.x + self.width * 0.2, self.y + self.height * 0.3),
            (self.x, self.y + self.height * 0.7),
            (self.x + self.width * 0.3, self.y + self.height),
            (self.x + self.width * 0.7, self.y + self.height),
            (self.x + self.width, self.y + self.height * 0.7),
            (self.x + self.width * 0.8, self.y + self.height * 0.3)
        ]
        pygame.draw.polygon(screen, GREEN, hull_points)
        pygame.draw.polygon(screen, DARK_GREEN, hull_points, 2)
        
        # Cockpit window
        pygame.draw.ellipse(screen, CYAN, (self.x + self.width * 0.35, self.y + self.height * 0.2, 
                                          self.width * 0.3, self.height * 0.25))
        pygame.draw.ellipse(screen, LIGHT_BLUE, (self.x + self.width * 0.4, self.y + self.height * 0.25, 
                                                 self.width * 0.2, self.height * 0.15))
        
        # Wing details
        pygame.draw.line(screen, YELLOW, (self.x + self.width * 0.2, self.y + self.height * 0.5),
                        (self.x + self.width * 0.2, self.y + self.height * 0.8), 2)
        pygame.draw.line(screen, YELLOW, (self.x + self.width * 0.8, self.y + self.height * 0.5),
                        (self.x + self.width * 0.8, self.y + self.height * 0.8), 2)
        
        # Gun turrets
        pygame.draw.rect(screen, DARK_GREEN, (self.x + self.width * 0.15, self.y + self.height * 0.6, 
                                             self.width * 0.1, self.height * 0.2))
        pygame.draw.rect(screen, DARK_GREEN, (self.x + self.width * 0.75, self.y + self.height * 0.6, 
                                             self.width * 0.1, self.height * 0.2))
        
        # Engine details
        pygame.draw.rect(screen, ORANGE, (self.x + self.width * 0.4, self.y + self.height * 0.85, 
                                         self.width * 0.2, self.height * 0.15))

class Bullet:
    def __init__(self, x, y, is_player=True):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED if is_player else -ENEMY_BULLET_SPEED
        self.is_player = is_player
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.trail = []
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        # Add trail effect
        self.trail.append((self.x + self.width // 2, self.y + self.height))
        if len(self.trail) > 5:
            self.trail.pop(0)
    
    def draw(self, screen):
        if self.is_player:
            # Player bullet - energy beam style
            # Trail
            for i, (tx, ty) in enumerate(self.trail):
                alpha = i / len(self.trail) if len(self.trail) > 0 else 0
                size = int(self.width * alpha)
                if size > 0:
                    pygame.draw.circle(screen, CYAN, (int(tx), int(ty)), size)
            
            # Main bullet
            pygame.draw.rect(screen, YELLOW, self.rect)
            pygame.draw.rect(screen, WHITE, (self.x + 1, self.y, self.width - 2, self.height // 2))
            # Glow effect
            glow_rect = pygame.Rect(self.x - 1, self.y - 1, self.width + 2, self.height + 2)
            pygame.draw.rect(screen, CYAN, glow_rect, 1)
        else:
            # Enemy bullet - plasma style
            # Trail
            for i, (tx, ty) in enumerate(self.trail):
                alpha = i / len(self.trail) if len(self.trail) > 0 else 0
                size = int(self.width * alpha)
                if size > 0:
                    pygame.draw.circle(screen, RED, (int(tx), int(ty)), size)
            
            # Main bullet
            pygame.draw.ellipse(screen, RED, self.rect)
            pygame.draw.ellipse(screen, ORANGE, (self.x + 1, self.y + 1, self.width - 2, self.height - 2))
            # Glow effect
            glow_rect = pygame.Rect(self.x - 1, self.y - 1, self.width + 2, self.height + 2)
            pygame.draw.ellipse(screen, RED, glow_rect, 1)
    
    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.animation_offset = random.randint(0, 360)
    
    def update(self, direction):
        self.x += direction
        self.rect.x = self.x
        self.animation_offset = (self.animation_offset + 2) % 360
    
    def move_down(self):
        self.y += 20
        self.rect.y = self.y
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Animated glow effect
        glow_intensity = 0.5 + 0.3 * math.sin(math.radians(self.animation_offset))
        
        # Main body - alien ship shape
        # Top part (head)
        head_points = [
            (center_x, self.y),
            (self.x + self.width * 0.2, self.y + self.height * 0.3),
            (self.x + self.width * 0.4, self.y + self.height * 0.2),
            (self.x + self.width * 0.6, self.y + self.height * 0.2),
            (self.x + self.width * 0.8, self.y + self.height * 0.3)
        ]
        pygame.draw.polygon(screen, RED, head_points)
        
        # Body (main rectangle with details)
        body_rect = pygame.Rect(self.x + self.width * 0.15, self.y + self.height * 0.3, 
                               self.width * 0.7, self.height * 0.5)
        pygame.draw.rect(screen, DARK_RED, body_rect)
        pygame.draw.rect(screen, RED, body_rect, 2)
        
        # Glowing eyes (animated)
        eye_size = 4 + int(2 * math.sin(math.radians(self.animation_offset)))
        left_eye_x = self.x + self.width * 0.3
        right_eye_x = self.x + self.width * 0.7
        eye_y = self.y + self.height * 0.4
        
        pygame.draw.circle(screen, YELLOW, (int(left_eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(screen, WHITE, (int(left_eye_x), int(eye_y)), eye_size // 2)
        pygame.draw.circle(screen, YELLOW, (int(right_eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(screen, WHITE, (int(right_eye_x), int(eye_y)), eye_size // 2)
        
        # Mouth/teeth
        mouth_y = self.y + self.height * 0.6
        for i in range(3):
            tooth_x = self.x + self.width * 0.3 + i * self.width * 0.15
            pygame.draw.polygon(screen, WHITE, [
                (tooth_x, mouth_y),
                (tooth_x + self.width * 0.05, mouth_y + self.height * 0.1),
                (tooth_x - self.width * 0.05, mouth_y + self.height * 0.1)
            ])
        
        # Tentacles/legs
        for i in range(4):
            tentacle_x = self.x + self.width * 0.2 + i * self.width * 0.2
            tentacle_start_y = self.y + self.height * 0.8
            tentacle_end_y = self.y + self.height
            pygame.draw.line(screen, PURPLE, (tentacle_x, tentacle_start_y), 
                           (tentacle_x, tentacle_end_y), 2)
            pygame.draw.circle(screen, PURPLE, (int(tentacle_x), int(tentacle_end_y)), 3)
        
        # Decorative details
        pygame.draw.line(screen, BLUE, (self.x + self.width * 0.25, self.y + self.height * 0.5),
                        (self.x + self.width * 0.75, self.y + self.height * 0.5), 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load sounds
        self.shoot_sound = generate_shoot_sound()
        self.explosion_sound = generate_explosion_sound()
        self.background_music = generate_background_music()
        self.music_channel = None
        
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 20)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.enemy_direction = 1
        self.game_over = False
        self.won = False
        self.star_field = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 
                           random.randint(1, 3)) for _ in range(100)]
        
        # Create enemies
        start_x = (SCREEN_WIDTH - (ENEMY_COLS * ENEMY_SPACING)) // 2
        start_y = 50
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * ENEMY_SPACING
                y = start_y + row * ENEMY_SPACING
                self.enemies.append(Enemy(x, y))
        
        # Start background music
        if self.music_channel:
            self.music_channel.stop()
        self.music_channel = self.background_music.play(-1)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y, True))
                    # Play shoot sound
                    self.shoot_sound.play()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_m:
                    # Toggle music
                    if self.music_channel and self.music_channel.get_busy():
                        self.music_channel.stop()
                    else:
                        self.music_channel = self.background_music.play(-1)
        return True
    
    def update(self):
        if self.game_over:
            return
        
        # Update star field animation
        self.star_field = [(x, (y + 0.5) % SCREEN_HEIGHT, size) for x, y, size in self.star_field]
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)
        
        # Check bullet-enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    # Create explosion particles
                    for _ in range(PARTICLE_COUNT):
                        self.particles.append(Particle(enemy.x + enemy.width // 2, 
                                                      enemy.y + enemy.height // 2))
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    # Play explosion sound
                    self.explosion_sound.play()
                    break
        
        # Check bullet-player collisions
        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                # Create explosion particles
                for _ in range(PARTICLE_COUNT):
                    self.particles.append(Particle(self.player.x + self.player.width // 2, 
                                                  self.player.y + self.player.height // 2))
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                # Play explosion sound
                self.explosion_sound.play()
                if self.lives <= 0:
                    self.game_over = True
                    if self.music_channel:
                        self.music_channel.stop()
        
        # Move enemies
        move_down = False
        for enemy in self.enemies:
            if (enemy.x <= 0 and self.enemy_direction < 0) or \
               (enemy.x >= SCREEN_WIDTH - ENEMY_WIDTH and self.enemy_direction > 0):
                move_down = True
                break
        
        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy.move_down()
        
        for enemy in self.enemies:
            enemy.update(self.enemy_direction)
        
        # Enemy shooting
        for enemy in self.enemies:
            if random.random() < ENEMY_SHOOT_CHANCE:
                bullet_x = enemy.x + enemy.width // 2 - BULLET_WIDTH // 2
                bullet_y = enemy.y + enemy.height
                self.enemy_bullets.append(Bullet(bullet_x, bullet_y, False))
        
        # Check if enemies reached player
        for enemy in self.enemies:
            if enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                break
        
        # Check win condition
        if len(self.enemies) == 0:
            self.game_over = True
            self.won = True
            if self.music_channel:
                self.music_channel.stop()
    
    def draw(self):
        # Draw star field background
        self.screen.fill(BLACK)
        for star_x, star_y, star_size in self.star_field:
            pygame.draw.circle(self.screen, WHITE, (int(star_x), int(star_y)), star_size)
        
        if not self.game_over:
            # Draw particles (explosions)
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw bullets
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            # Draw player
            self.player.draw(self.screen)
            
            # Draw UI with better styling
            # Score background
            score_bg = pygame.Surface((200, 80))
            score_bg.set_alpha(128)
            score_bg.fill(BLACK)
            self.screen.blit(score_bg, (5, 5))
            
            score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
            self.screen.blit(score_text, (10, 10))
            
            lives_text = self.font.render(f"Lives: {self.lives}", True, GREEN)
            self.screen.blit(lives_text, (10, 50))
            
            # Draw life indicators
            for i in range(self.lives):
                life_x = SCREEN_WIDTH - 60 - i * 20
                pygame.draw.polygon(self.screen, GREEN, [
                    (life_x, SCREEN_HEIGHT - 20),
                    (life_x + 10, SCREEN_HEIGHT - 30),
                    (life_x + 20, SCREEN_HEIGHT - 20)
                ])
        else:
            # Draw particles even in game over
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Game over screen with better styling
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.won:
                game_over_text = self.font.render("YOU WIN!", True, GREEN)
                # Add glow effect
                glow_surf = self.font.render("YOU WIN!", True, YELLOW)
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    glow_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2 + offset[0], 
                                                               SCREEN_HEIGHT // 2 - 50 + offset[1]))
                    self.screen.blit(glow_surf, glow_rect)
            else:
                game_over_text = self.font.render("GAME OVER", True, RED)
                # Add glow effect
                glow_surf = self.font.render("GAME OVER", True, ORANGE)
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    glow_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2 + offset[0], 
                                                               SCREEN_HEIGHT // 2 - 50 + offset[1]))
                    self.screen.blit(glow_surf, glow_rect)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.small_font.render("Press R to Restart | M to Toggle Music", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

