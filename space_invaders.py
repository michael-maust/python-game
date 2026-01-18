import pygame
import random
import sys

# Initialize Pygame
pygame.init()

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

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        # Draw player ship (triangle shape)
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        # Draw body
        pygame.draw.rect(screen, GREEN, (self.x + self.width // 4, self.y + self.height // 2, 
                                         self.width // 2, self.height // 2))

class Bullet:
    def __init__(self, x, y, is_player=True):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED if is_player else -ENEMY_BULLET_SPEED
        self.is_player = is_player
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        color = YELLOW if self.is_player else RED
        pygame.draw.rect(screen, color, self.rect)
    
    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, direction):
        self.x += direction
        self.rect.x = self.x
    
    def move_down(self):
        self.y += 20
        self.rect.y = self.y
    
    def draw(self, screen):
        # Draw enemy ship
        pygame.draw.rect(screen, RED, self.rect)
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 3, self.y + self.height // 3), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 2 * self.width // 3, self.y + self.height // 3), 3)
        # Draw body detail
        pygame.draw.rect(screen, BLUE, (self.x + self.width // 4, self.y + self.height // 2, 
                                        self.width // 2, self.height // 2))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 20)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.enemy_direction = 1
        self.game_over = False
        self.won = False
        
        # Create enemies
        start_x = (SCREEN_WIDTH - (ENEMY_COLS * ENEMY_SPACING)) // 2
        start_y = 50
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = start_x + col * ENEMY_SPACING
                y = start_y + row * ENEMY_SPACING
                self.enemies.append(Enemy(x, y))
    
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
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
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
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # Check bullet-player collisions
        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
        
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
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if not self.game_over:
            self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw score and lives
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(lives_text, (10, 50))
        else:
            # Game over screen
            if self.won:
                game_over_text = self.font.render("YOU WIN!", True, GREEN)
            else:
                game_over_text = self.font.render("GAME OVER", True, RED)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
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

