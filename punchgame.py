import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.punch_cooldown = 0
        self.punch_range = 60
        self.is_punching = False
        self.punch_timer = 0
        self.punch_extension = 0  # How far the fist extends
        self.hit_enemies = set()  # Track which enemies were hit in this punch
        self.punch_angle = 0  # Angle toward mouse when punch started
        
    def update(self, enemies):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
        
        # Punch cooldown
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1
            
        # Punch animation
        if self.punch_timer > 0:
            self.punch_timer -= 1
            self.is_punching = True
            # Animate fist extension
            self.punch_extension = (10 - self.punch_timer) * 4
            
            # Check for hits during the entire punch animation
            self.check_punch_hits(enemies)
        else:
            self.is_punching = False
            self.punch_extension = 0
            # Clear hit enemies when punch ends
            if self.punch_timer == 0 and not self.is_punching:
                self.hit_enemies.clear()
    
    def punch(self):
        if self.punch_cooldown <= 0:
            self.punch_cooldown = 20
            self.punch_timer = 10
            self.is_punching = True
            self.hit_enemies.clear()  # Clear previous hits
            
            # Calculate angle to mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            dx = mouse_x - player_center_x
            dy = mouse_y - player_center_y
            self.punch_angle = math.atan2(dy, dx)
    
    def check_punch_hits(self, enemies):
        """Check for collision with enemies during punch animation"""
        if not self.is_punching:
            return
            
        # Get fist position (extends from player center in the direction of punch_angle)
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        fist_x = player_center_x + math.cos(self.punch_angle) * self.punch_extension
        fist_y = player_center_y + math.sin(self.punch_angle) * self.punch_extension
        
        for enemy in enemies:
            if not enemy.alive or id(enemy) in self.hit_enemies:
                continue
                
            # Check if fist overlaps with enemy hitbox
            enemy_center_x = enemy.x + enemy.width // 2
            enemy_center_y = enemy.y + enemy.height // 2
            
            distance = math.sqrt((fist_x - enemy_center_x)**2 + (fist_y - enemy_center_y)**2)
            
            # Hit detection with fist size consideration
            if distance < 35:  # Fist radius + some tolerance
                enemy.take_damage(25)
                self.hit_enemies.add(id(enemy))  # Mark this enemy as hit
    
    def rotate_point(self, x, y, cx, cy, angle):
        """Rotate a point (x, y) around center (cx, cy) by angle"""
        s = math.sin(angle)
        c = math.cos(angle)
        
        # Translate point to origin
        x -= cx
        y -= cy
        
        # Rotate
        new_x = x * c - y * s
        new_y = x * s + y * c
        
        # Translate back
        return new_x + cx, new_y + cy
    
    def draw(self, screen):
        # Draw player body
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        
        # Draw punch effect - human fist
        if self.is_punching:
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            
            # Calculate fist position based on angle
            fist_x = player_center_x + math.cos(self.punch_angle) * self.punch_extension
            fist_y = player_center_y + math.sin(self.punch_angle) * self.punch_extension
            
            # Skin tone color
            SKIN_TONE = (255, 220, 177)
            SKIN_SHADOW = (220, 180, 140)
            
            # Draw arm extending from player to fist
            arm_width = 15
            arm_length = 20
            arm_start_x = player_center_x + math.cos(self.punch_angle) * 25
            arm_start_y = player_center_y + math.sin(self.punch_angle) * 25
            arm_end_x = fist_x - math.cos(self.punch_angle) * arm_length
            arm_end_y = fist_y - math.sin(self.punch_angle) * arm_length
            pygame.draw.line(screen, SKIN_TONE, 
                           (arm_start_x, arm_start_y), 
                           (arm_end_x, arm_end_y), arm_width)
            
            # Define fist shape relative to origin (pointing right)
            # Main fist body (knuckles)
            base_fist_points = [
                (-10, -15),  # Top left
                (15, -15),   # Top right
                (20, -5),    # Right knuckle
                (20, 10),    # Bottom right
                (-10, 10),   # Bottom left
                (-15, 0)     # Left side
            ]
            
            # Rotate and translate fist points
            fist_points = []
            for px, py in base_fist_points:
                rotated_x, rotated_y = self.rotate_point(px, py, 0, 0, self.punch_angle)
                fist_points.append((fist_x + rotated_x, fist_y + rotated_y))
            
            pygame.draw.polygon(screen, SKIN_TONE, fist_points)
            pygame.draw.polygon(screen, SKIN_SHADOW, fist_points, 2)
            
            # Draw thumb
            base_thumb_points = [
                (-10, -5),
                (-18, -8),
                (-18, 5),
                (-10, 8)
            ]
            
            thumb_points = []
            for px, py in base_thumb_points:
                rotated_x, rotated_y = self.rotate_point(px, py, 0, 0, self.punch_angle)
                thumb_points.append((fist_x + rotated_x, fist_y + rotated_y))
            
            pygame.draw.polygon(screen, SKIN_TONE, thumb_points)
            pygame.draw.polygon(screen, SKIN_SHADOW, thumb_points, 2)
            
            # Draw knuckle details (small lines)
            for i in range(3):
                base_x1 = 5 + i * 5
                base_y1 = -15
                base_x2 = 5 + i * 5
                base_y2 = -10
                
                x1, y1 = self.rotate_point(base_x1, base_y1, 0, 0, self.punch_angle)
                x2, y2 = self.rotate_point(base_x2, base_y2, 0, 0, self.punch_angle)
                
                pygame.draw.line(screen, SKIN_SHADOW, 
                               (fist_x + x1, fist_y + y1), 
                               (fist_x + x2, fist_y + y2), 2)
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 5, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.y - 15, bar_width * health_ratio, bar_height))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 2
        self.health = 50
        self.max_health = 50
        self.attack_cooldown = 0
        self.alive = True
        
    def update(self, player):
        if not self.alive:
            return
            
        # Move towards player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        # Attack player if close
        if distance < 40 and self.attack_cooldown <= 0:
            player.health -= 10
            self.attack_cooldown = 60
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        if not self.alive:
            return
            
        # Draw enemy body
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
        # Draw health bar
        bar_width = 50
        bar_height = 6
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y - 12, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.y - 12, bar_width * health_ratio, bar_height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Punching Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.spawn_timer = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
    def spawn_enemy(self):
        # Spawn enemy at random edge of screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.randint(0, SCREEN_WIDTH - 40)
            y = -60
        elif side == 1:  # Right
            x = SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT - 60)
        elif side == 2:  # Bottom
            x = random.randint(0, SCREEN_WIDTH - 40)
            y = SCREEN_HEIGHT
        else:  # Left
            x = -40
            y = random.randint(0, SCREEN_HEIGHT - 60)
            
        self.enemies.append(Enemy(x, y))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.punch()
    
    def update(self):
        self.player.update(self.enemies)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player)
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.score += 10
        
        # Spawn new enemies
        self.spawn_timer += 1
        if self.spawn_timer >= 120:  # Spawn every 2 seconds
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # Check game over
        if self.player.health <= 0:
            self.running = False
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw game objects
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        # Draw instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "WASD/Arrow Keys: Move",
            "SPACE: Punch",
            "Survive as long as possible!"
        ]
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH - 250, 10 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Game over screen
        game_over_text = self.font.render(f"Game over nerd! Final Score: {self.score}", True, BLACK)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.fill(WHITE)
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        
        # Wait for a few seconds before closing
        pygame.time.wait(3000)
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
