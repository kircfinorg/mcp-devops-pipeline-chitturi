import pygame
import random
import math
#initionalizing pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
ZOMBIE_GREEN = (100, 150, 80)
SKIN_TONE = (255, 220, 177)
BROWN = (139, 69, 19)
PURPLE = (148, 0, 211)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
ASPHALT = (70, 70, 70)
BRICK_RED = (150, 50, 50)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.base_speed = 5
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.punch_cooldown = 0
        self.base_punch_cooldown = 20
        self.punch_range = 80  # Increased punch radius
        self.is_punching = False
        self.punch_timer = 0
        self.punch_extension = 0  # How far the fist extends
        self.hit_enemies = set()  # Track which enemies were hit in this punch
        self.punch_angle = 0  # Angle toward mouse when punch started
        
        # Leveling system
        self.level = 1
        self.kills = 0
        self.kills_for_next_level = 10
        self.base_damage = 25
        self.damage_multiplier = 1.0
        
        # Weapons and coins
        self.coins = 0
        self.has_sword = False
        self.has_gun = False
        self.gun_ammo = 0
        self.gun_cooldown = 0
        
        # Powerup effects
        self.invincible = False
        self.invincible_timer = 0
        self.double_speed = False
        self.double_speed_timer = 0
        self.damage_boost = False
        self.damage_boost_timer = 0
        
        # Ground slam ability
        self.ground_slam_cooldown = 0
        self.is_slamming = False
        self.slam_timer = 0
        
    def update(self, enemies, obstacles):
        keys = pygame.key.get_pressed()
        
        # Update powerup timers
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.invincible = True
        else:
            self.invincible = False
            
        if self.double_speed_timer > 0:
            self.double_speed_timer -= 1
            self.double_speed = True
        else:
            self.double_speed = False
            # Reset speed and punch cooldown when powerup wears off
            self.speed = self.base_speed
            self.base_punch_cooldown = 20
        
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= 1
            self.damage_boost = True
        else:
            self.damage_boost = False
        
        # Ground slam cooldown
        if self.ground_slam_cooldown > 0:
            self.ground_slam_cooldown -= 1
        
        # Ground slam animation
        if self.slam_timer > 0:
            self.slam_timer -= 1
            self.is_slamming = True
        else:
            self.is_slamming = False
        
        # Gun cooldown
        if self.gun_cooldown > 0:
            self.gun_cooldown -= 1
        
        # Store old position for collision detection
        old_x, old_y = self.x, self.y
        
        # Movement
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += self.speed
        
        # Apply movement
        self.x += move_x
        self.y += move_y
            
        # Smooth collision with obstacles - slide along walls
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for obstacle in obstacles:
            if player_rect.colliderect(obstacle):
                # Reset to old position
                self.x, self.y = old_x, old_y
                
                # Try sliding horizontally
                self.x = old_x + move_x
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if player_rect.colliderect(obstacle):
                    self.x = old_x
                    
                # Try sliding vertically
                self.y = old_y + move_y
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if player_rect.colliderect(obstacle):
                    self.y = old_y
                break
            
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
            # Animate fist extension (bigger range now)
            self.punch_extension = (10 - self.punch_timer) * 6
            
            # Check for hits during the entire punch animation
            self.check_punch_hits(enemies)
        else:
            self.is_punching = False
            self.punch_extension = 0
            # Clear hit enemies when punch ends
            if self.punch_timer == 0 and not self.is_punching:
                self.hit_enemies.clear()
    
    def take_damage(self, damage):
        if not self.invincible:
            self.health -= damage
    
    def activate_powerup(self, powerup_type):
        if powerup_type == "speed":
            self.double_speed_timer = 300  # 5 seconds at 60 FPS
            self.base_punch_cooldown = 5  # Much faster punching
            self.speed = 8  # Faster movement too
        elif powerup_type == "invincible":
            self.invincible_timer = 180  # 3 seconds at 60 FPS
        elif powerup_type == "health":
            self.health = min(self.max_health, self.health + 50)  # Heal 50 HP
        elif powerup_type == "damage":
            self.damage_boost_timer = 600  # 10 seconds at 60 FPS
    
    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.kills_for_next_level = self.level * 10
        self.damage_multiplier += 0.2  # 20% damage increase per level
        self.max_health += 10
        self.health = min(self.max_health, self.health + 20)  # Heal 20 HP on level up
    
    def add_kill(self):
        """Track kills and level up when threshold reached"""
        self.kills += 1
        self.coins += 10  # Earn 10 coins per kill
        if self.kills >= self.kills_for_next_level:
            self.level_up()
    
    def shoot_gun(self, enemies):
        """Shoot gun at nearest enemy"""
        if not self.has_gun or self.gun_ammo <= 0 or self.gun_cooldown > 0:
            return False
        
        # Find nearest enemy
        nearest_enemy = None
        min_distance = float('inf')
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            enemy_center_x = enemy.x + enemy.width // 2
            enemy_center_y = enemy.y + enemy.height // 2
            distance = math.sqrt((player_center_x - enemy_center_x)**2 + 
                               (player_center_y - enemy_center_y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        if nearest_enemy and min_distance < 400:  # Gun range
            damage = 50 * self.damage_multiplier
            if self.damage_boost:
                damage *= 2
            nearest_enemy.take_damage(damage)
            self.gun_ammo -= 1
            self.gun_cooldown = 30  # Half second cooldown
            return True
        return False
    
    def ground_slam(self, enemies):
        """Perform ground slam attack - damages all nearby enemies"""
        if self.ground_slam_cooldown <= 0:
            self.ground_slam_cooldown = 300  # 5 second cooldown
            self.slam_timer = 20
            self.is_slamming = True
            
            # Damage all enemies within range
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            
            for enemy in enemies:
                if not enemy.alive:
                    continue
                    
                enemy_center_x = enemy.x + enemy.width // 2
                enemy_center_y = enemy.y + enemy.height // 2
                
                distance = math.sqrt((player_center_x - enemy_center_x)**2 + 
                                   (player_center_y - enemy_center_y)**2)
                
                # Ground slam has larger radius
                if distance < 150:
                    damage = 40 * self.damage_multiplier
                    if self.damage_boost:
                        damage *= 2
                    enemy.take_damage(damage)  # More damage than regular punch
    
    def punch(self):
        if self.punch_cooldown <= 0:
            self.punch_cooldown = self.base_punch_cooldown
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
            
            # Hit detection with fist size consideration (bigger radius)
            if distance < 50:  # Increased fist radius + tolerance
                damage = self.base_damage * self.damage_multiplier
                if self.has_sword:
                    damage *= 1.5  # Sword increases melee damage by 50%
                if self.damage_boost:
                    damage *= 2  # Double damage with powerup
                enemy.take_damage(damage)
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
        # Draw human player
        center_x = self.x + self.width // 2
        
        # Invincibility effect - glowing outline
        if self.invincible:
            pygame.draw.rect(screen, GOLD, (self.x - 3, self.y - 3, self.width + 6, self.height + 6), 3)
        
        # Double speed effect - cyan outline
        if self.double_speed:
            pygame.draw.rect(screen, CYAN, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 2)
        
        # Damage boost effect - orange outline
        if self.damage_boost:
            pygame.draw.rect(screen, ORANGE, (self.x - 4, self.y - 4, self.width + 8, self.height + 8), 3)
        
        # Legs
        pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 50, 15, 30))  # Left leg
        pygame.draw.rect(screen, BLUE, (self.x + 30, self.y + 50, 15, 30))  # Right leg
        
        # Body (torso)
        pygame.draw.rect(screen, RED, (self.x + 10, self.y + 25, 30, 30))
        
        # Head
        pygame.draw.circle(screen, SKIN_TONE, (center_x, self.y + 15), 15)
        
        # Eyes
        pygame.draw.circle(screen, BLACK, (center_x - 5, self.y + 12), 3)
        pygame.draw.circle(screen, BLACK, (center_x + 5, self.y + 12), 3)
        
        # Mouth
        pygame.draw.arc(screen, BLACK, (center_x - 6, self.y + 15, 12, 8), 3.14, 6.28, 2)
        
        # Arms (when not punching)
        if not self.is_punching:
            pygame.draw.rect(screen, SKIN_TONE, (self.x, self.y + 30, 10, 20))  # Left arm
            pygame.draw.rect(screen, SKIN_TONE, (self.x + 40, self.y + 30, 10, 20))  # Right arm
            
            # Draw sword if equipped
            if self.has_sword:
                pygame.draw.rect(screen, GRAY, (self.x + 45, self.y + 25, 4, 30))  # Blade
                pygame.draw.rect(screen, BROWN, (self.x + 43, self.y + 50, 8, 10))  # Handle
            
            # Draw gun if equipped
            if self.has_gun:
                pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + 35, 15, 8))  # Gun body
                pygame.draw.rect(screen, DARK_GRAY, (self.x - 10, self.y + 37, 5, 4))  # Barrel
        
        # Draw punch effect - human fist
        if self.is_punching:
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            
            # Calculate fist position based on angle
            fist_x = player_center_x + math.cos(self.punch_angle) * self.punch_extension
            fist_y = player_center_y + math.sin(self.punch_angle) * self.punch_extension
            
            # Skin tone color
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
        
        # Draw ground slam effect
        if self.is_slamming:
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            
            # Expanding shockwave circles
            slam_progress = (20 - self.slam_timer) / 20
            radius = int(150 * slam_progress)
            alpha = int(255 * (1 - slam_progress))
            
            # Draw multiple shockwave rings
            for i in range(3):
                ring_radius = radius - i * 20
                if ring_radius > 0:
                    pygame.draw.circle(screen, YELLOW, 
                                     (player_center_x, player_center_y), 
                                     ring_radius, 4)
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 5, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.y - 15, bar_width * health_ratio, bar_height))

class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type  # "car", "building", "dumpster"
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        if self.type == "car":
            # Draw abandoned car
            pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
            # Windows
            pygame.draw.rect(screen, CYAN, (self.x + 10, self.y + 10, 30, 20))
            pygame.draw.rect(screen, CYAN, (self.x + self.width - 40, self.y + 10, 30, 20))
            # Wheels
            pygame.draw.circle(screen, BLACK, (self.x + 20, self.y + self.height), 10)
            pygame.draw.circle(screen, BLACK, (self.x + self.width - 20, self.y + self.height), 10)
            
        elif self.type == "building":
            # Draw building wall
            pygame.draw.rect(screen, BRICK_RED, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            # Windows
            for i in range(0, self.width, 30):
                for j in range(0, self.height, 40):
                    if i + 15 < self.width and j + 20 < self.height:
                        pygame.draw.rect(screen, YELLOW, (self.x + i + 5, self.y + j + 5, 15, 20))
                        
        elif self.type == "dumpster":
            # Draw dumpster
            pygame.draw.rect(screen, DARK_GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
            # Lid
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 5, self.width, 8))

class Enemy:
    def __init__(self, x, y, wave=1):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.base_speed = 2
        self.speed = self.base_speed + (wave - 1) * 0.15  # Slower progression
        self.base_health = 50
        self.health = self.base_health + (wave - 1) * 5  # Slower health increase
        self.max_health = self.health
        self.attack_cooldown = 0
        self.alive = True
        self.wave = wave
        self.stuck_timer = 0
        self.last_x = x
        self.last_y = y
        
    def update(self, player, obstacles):
        if not self.alive:
            return
            
        # Store old position
        old_x, old_y = self.x, self.y
        
        # Check if stuck
        if abs(self.x - self.last_x) < 1 and abs(self.y - self.last_y) < 1:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
        
        self.last_x = self.x
        self.last_y = self.y
            
        # Calculate direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            # Try moving directly toward player
            self.x += move_x
            self.y += move_y
            
            # Check collision with obstacles
            enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
            for obstacle in obstacles:
                if enemy_rect.colliderect(obstacle):
                    # Reset position
                    self.x, self.y = old_x, old_y
                    
                    # Better pathfinding - try to go around obstacle
                    # Calculate obstacle center
                    obs_center_x = obstacle.x + obstacle.width / 2
                    obs_center_y = obstacle.y + obstacle.height / 2
                    
                    # Determine which side of obstacle to go around
                    to_obs_x = obs_center_x - self.x
                    to_obs_y = obs_center_y - self.y
                    
                    # Try perpendicular directions to go around
                    # If obstacle is more to the left/right, try going up/down
                    if abs(to_obs_x) > abs(to_obs_y):
                        # Try going up or down
                        if dy > 0:
                            self.y = old_y + self.speed
                        else:
                            self.y = old_y - self.speed
                        
                        # Also try slight horizontal movement
                        if dx > 0:
                            self.x = old_x + self.speed * 0.3
                        else:
                            self.x = old_x - self.speed * 0.3
                    else:
                        # Try going left or right
                        if dx > 0:
                            self.x = old_x + self.speed
                        else:
                            self.x = old_x - self.speed
                        
                        # Also try slight vertical movement
                        if dy > 0:
                            self.y = old_y + self.speed * 0.3
                        else:
                            self.y = old_y - self.speed * 0.3
                    
                    # Check if new position still collides
                    enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    if enemy_rect.colliderect(obstacle):
                        # Still colliding, try sliding along obstacle
                        self.x = old_x
                        self.y = old_y
                        
                        # Try only horizontal
                        self.x = old_x + move_x
                        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                        if enemy_rect.colliderect(obstacle):
                            self.x = old_x
                            # Try only vertical
                            self.y = old_y + move_y
                            enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                            if enemy_rect.colliderect(obstacle):
                                self.y = old_y
                    
                    # If stuck for too long, try random direction to escape
                    if self.stuck_timer > 60:
                        angle = random.uniform(0, 2 * math.pi)
                        self.x = old_x + math.cos(angle) * self.speed * 3
                        self.y = old_y + math.sin(angle) * self.speed * 3
                        self.stuck_timer = 0
                    break
        
        # Attack player if close
        if distance < 40 and self.attack_cooldown <= 0:
            damage = 10 + (self.wave - 1) * 1  # Slower damage increase
            player.take_damage(damage)
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
        
        center_x = self.x + self.width // 2
        
        # Draw zombie
        # Legs (torn pants)
        pygame.draw.rect(screen, GRAY, (self.x + 5, self.y + 40, 12, 20))  # Left leg
        pygame.draw.rect(screen, GRAY, (self.x + 23, self.y + 40, 12, 20))  # Right leg
        
        # Body (torn shirt)
        pygame.draw.rect(screen, DARK_GREEN, (self.x + 8, self.y + 20, 24, 22))
        
        # Head (zombie green)
        pygame.draw.circle(screen, ZOMBIE_GREEN, (center_x, self.y + 12), 12)
        
        # Eyes (dead/white)
        pygame.draw.circle(screen, WHITE, (center_x - 4, self.y + 10), 3)
        pygame.draw.circle(screen, WHITE, (center_x + 4, self.y + 10), 3)
        pygame.draw.circle(screen, BLACK, (center_x - 4, self.y + 10), 1)
        pygame.draw.circle(screen, BLACK, (center_x + 4, self.y + 10), 1)
        
        # Mouth (open/groaning)
        pygame.draw.ellipse(screen, BLACK, (center_x - 4, self.y + 14, 8, 6))
        
        # Arms (reaching out)
        pygame.draw.rect(screen, ZOMBIE_GREEN, (self.x - 2, self.y + 22, 8, 15))  # Left arm
        pygame.draw.rect(screen, ZOMBIE_GREEN, (self.x + 34, self.y + 22, 8, 15))  # Right arm
        
        # Draw health bar
        bar_width = 50
        bar_height = 6
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y - 12, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.y - 12, bar_width * health_ratio, bar_height))

class Boss(Enemy):
    def __init__(self, x, y, wave):
        super().__init__(x, y, wave)
        self.width = 80
        self.height = 120
        self.speed = 1.5
        self.health = 200 + wave * 50  # Much more health
        self.max_health = self.health
        self.is_boss = True
        
    def update(self, player, obstacles):
        # Boss uses same pathfinding as regular enemies
        super().update(player, obstacles)
        
    def draw(self, screen):
        if not self.alive:
            return
        
        center_x = self.x + self.width // 2
        
        # Draw boss zombie (bigger and scarier)
        # Legs (torn pants)
        pygame.draw.rect(screen, GRAY, (self.x + 10, self.y + 80, 24, 40))  # Left leg
        pygame.draw.rect(screen, GRAY, (self.x + 46, self.y + 80, 24, 40))  # Right leg
        
        # Body (torn shirt)
        pygame.draw.rect(screen, DARK_RED, (self.x + 16, self.y + 40, 48, 44))
        
        # Head (zombie green - bigger)
        pygame.draw.circle(screen, ZOMBIE_GREEN, (center_x, self.y + 24), 24)
        
        # Eyes (dead/white - bigger)
        pygame.draw.circle(screen, WHITE, (center_x - 8, self.y + 20), 6)
        pygame.draw.circle(screen, WHITE, (center_x + 8, self.y + 20), 6)
        pygame.draw.circle(screen, RED, (center_x - 8, self.y + 20), 3)
        pygame.draw.circle(screen, RED, (center_x + 8, self.y + 20), 3)
        
        # Mouth (open/groaning - bigger)
        pygame.draw.ellipse(screen, BLACK, (center_x - 8, self.y + 28, 16, 12))
        
        # Arms (reaching out - bigger)
        pygame.draw.rect(screen, ZOMBIE_GREEN, (self.x - 4, self.y + 44, 16, 30))  # Left arm
        pygame.draw.rect(screen, ZOMBIE_GREEN, (self.x + 68, self.y + 44, 16, 30))  # Right arm
        
        # Boss crown/indicator
        pygame.draw.polygon(screen, GOLD, [
            (center_x - 15, self.y),
            (center_x - 10, self.y - 10),
            (center_x - 5, self.y),
            (center_x, self.y - 15),
            (center_x + 5, self.y),
            (center_x + 10, self.y - 10),
            (center_x + 15, self.y)
        ])
        
        # Draw health bar (bigger)
        bar_width = 80
        bar_height = 8
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y - 20, bar_width, bar_height))
        pygame.draw.rect(screen, RED, (self.x - 5, self.y - 20, bar_width * health_ratio, bar_height))
        
        # Boss label
        font = pygame.font.Font(None, 20)
        boss_text = font.render("BOSS", True, GOLD)
        screen.blit(boss_text, (self.x + 25, self.y - 35))

class Powerup:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = powerup_type  # "speed", "invincible", or "health"
        self.collected = False
        
    def check_collision(self, player):
        """Check if player collects this powerup"""
        if self.collected:
            return False
            
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        powerup_center_x = self.x + self.width // 2
        powerup_center_y = self.y + self.height // 2
        
        distance = math.sqrt((player_center_x - powerup_center_x)**2 + 
                           (player_center_y - powerup_center_y)**2)
        
        if distance < 40:
            self.collected = True
            return True
        return False
    
    def draw(self, screen):
        if self.collected:
            return
            
        if self.type == "speed":
            # Draw speed powerup (lightning bolt)
            pygame.draw.rect(screen, CYAN, (self.x, self.y, self.width, self.height))
            pygame.draw.polygon(screen, YELLOW, [
                (self.x + 15, self.y + 5),
                (self.x + 10, self.y + 15),
                (self.x + 18, self.y + 15),
                (self.x + 12, self.y + 25)
            ])
            # Label
            font = pygame.font.Font(None, 16)
            text = font.render("2X", True, BLACK)
            screen.blit(text, (self.x + 8, self.y + 2))
            
        elif self.type == "invincible":
            # Draw invincibility powerup (shield)
            pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, GOLD, (self.x + 15, self.y + 15), 12, 3)
            # Label
            font = pygame.font.Font(None, 16)
            text = font.render("INV", True, WHITE)
            screen.blit(text, (self.x + 5, self.y + 10))
            
        elif self.type == "health":
            # Draw health powerup (heart)
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            # Draw heart shape
            pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 12), 6)
            pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 12), 6)
            pygame.draw.polygon(screen, WHITE, [
                (self.x + 5, self.y + 14),
                (self.x + 15, self.y + 24),
                (self.x + 25, self.y + 14)
            ])
            # Label
            font = pygame.font.Font(None, 16)
            text = font.render("+50", True, WHITE)
            screen.blit(text, (self.x + 5, self.y + 2))
            
        elif self.type == "damage":
            # Draw damage powerup (fist with fire)
            pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))
            # Draw fist
            pygame.draw.circle(screen, RED, (self.x + 15, self.y + 15), 10)
            pygame.draw.rect(screen, RED, (self.x + 10, self.y + 15, 10, 8))
            # Label
            font = pygame.font.Font(None, 16)
            text = font.render("DMG", True, WHITE)
            screen.blit(text, (self.x + 4, self.y + 2))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Puncher - Abandoned City")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game states: "menu", "playing", "shop"
        self.state = "menu"
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.powerups = []
        self.obstacles = self.create_obstacles()
        self.spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
        # Wave system
        self.current_wave = 1
        self.enemies_per_wave = 5
        self.enemies_spawned_this_wave = 0
        self.wave_complete = False
        self.wave_timer = 0
        self.is_boss_wave = False
        self.boss = None
        
        # Menu buttons
        self.play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 60)
        self.shop_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30, 200, 60)
        self.back_button = pygame.Rect(50, 50, 150, 50)
        
    def create_obstacles(self):
        """Create obstacles for the abandoned city"""
        obstacles = []
        
        # Randomize building positions
        building_configs = [
            (random.randint(50, 200), random.randint(50, 200), 150, 200, "building"),
            (random.randint(800, 1000), random.randint(100, 250), 200, 180, "building"),
            (random.randint(350, 500), random.randint(450, 600), 180, 150, "building"),
        ]
        
        for config in building_configs:
            obstacles.append(Obstacle(*config))
        
        # Cars
        obstacles.append(Obstacle(random.randint(250, 400), random.randint(250, 400), 80, 50, "car"))
        obstacles.append(Obstacle(random.randint(650, 800), random.randint(350, 500), 80, 50, "car"))
        obstacles.append(Obstacle(random.randint(450, 600), random.randint(100, 200), 80, 50, "car"))
        
        # Dumpsters
        obstacles.append(Obstacle(random.randint(150, 250), random.randint(550, 650), 60, 50, "dumpster"))
        obstacles.append(Obstacle(random.randint(750, 900), random.randint(550, 700), 60, 50, "dumpster"))
        
        return [obs.get_rect() for obs in obstacles], obstacles
    
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
            
        self.enemies.append(Enemy(x, y, self.current_wave))
        self.enemies_spawned_this_wave += 1
    
    def spawn_boss(self):
        """Spawn a boss enemy"""
        # Spawn boss at top center
        x = SCREEN_WIDTH // 2 - 40
        y = -120
        self.boss = Boss(x, y, self.current_wave)
        self.enemies.append(self.boss)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == "menu":
                        if self.play_button.collidepoint(mouse_pos):
                            self.start_game()
                        elif self.shop_button.collidepoint(mouse_pos):
                            self.state = "shop"
                    
                    elif self.state == "shop":
                        if self.back_button.collidepoint(mouse_pos):
                            self.state = "menu"
                        # Check shop item clicks
                        self.handle_shop_click(mouse_pos)
                    
                    elif self.state == "playing":
                        self.player.punch()
            
            elif event.type == pygame.KEYDOWN and self.state == "playing":
                if event.key == pygame.K_SPACE:
                    self.player.punch()
                elif event.key == pygame.K_r:
                    self.player.ground_slam(self.enemies)
                elif event.key == pygame.K_g:
                    self.player.shoot_gun(self.enemies)
    
    def start_game(self):
        """Start a new game"""
        self.state = "playing"
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT // 2
        self.player.health = self.player.max_health
        self.enemies = []
        self.powerups = []
        self.obstacles = self.create_obstacles()
        self.current_wave = 1
        self.enemies_per_wave = 5
        self.enemies_spawned_this_wave = 0
        self.wave_complete = False
        self.is_boss_wave = False
        self.boss = None
        self.spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.score = 0
    
    def handle_shop_click(self, mouse_pos):
        """Handle clicks in the shop"""
        # Sword button
        sword_button = pygame.Rect(SCREEN_WIDTH // 2 - 250, 300, 200, 100)
        if sword_button.collidepoint(mouse_pos) and not self.player.has_sword:
            if self.player.coins >= 200:
                self.player.coins -= 200
                self.player.has_sword = True
        
        # Gun button
        gun_button = pygame.Rect(SCREEN_WIDTH // 2 + 50, 300, 200, 100)
        if gun_button.collidepoint(mouse_pos) and not self.player.has_gun:
            if self.player.coins >= 400:
                self.player.coins -= 400
                self.player.has_gun = True
                self.player.gun_ammo = 50  # Start with 50 bullets
        
        # Ammo refill button (if player has gun)
        if self.player.has_gun:
            ammo_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 80)
            if ammo_button.collidepoint(mouse_pos):
                if self.player.coins >= 50:
                    self.player.coins -= 50
                    self.player.gun_ammo += 30
    
    def spawn_powerup(self):
        """Spawn a random powerup at a random location (not on obstacles)"""
        max_attempts = 10
        for _ in range(max_attempts):
            x = random.randint(50, SCREEN_WIDTH - 80)
            y = random.randint(50, SCREEN_HEIGHT - 80)
            powerup_rect = pygame.Rect(x, y, 30, 30)
            
            # Check if powerup overlaps with obstacles
            collision = False
            for obstacle in self.obstacles[0]:
                if powerup_rect.colliderect(obstacle):
                    collision = True
                    break
            
            if not collision:
                powerup_type = random.choice(["speed", "invincible", "health", "damage"])
                self.powerups.append(Powerup(x, y, powerup_type))
                break
    
    def update(self):
        if self.state != "playing":
            return
        
        self.player.update(self.enemies, self.obstacles[0])
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player, self.obstacles[0])
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.player.add_kill()  # Track kills for leveling
                # More points for bosses
                if hasattr(enemy, 'is_boss') and enemy.is_boss:
                    self.score += 100 * self.current_wave
                else:
                    self.score += 10 * self.current_wave
        
        # Check powerup collection
        for powerup in self.powerups[:]:
            if powerup.check_collision(self.player):
                self.player.activate_powerup(powerup.type)
                self.powerups.remove(powerup)
        
        # Wave system
        if self.current_wave % 10 == 0 and not self.is_boss_wave:
            # Boss wave every 10 waves
            self.is_boss_wave = True
            if self.boss is None or not self.boss.alive:
                self.spawn_boss()
                self.enemies_spawned_this_wave = 1
        elif not self.is_boss_wave:
            # Regular wave
            if self.enemies_spawned_this_wave < self.enemies_per_wave:
                # Spawn enemies for current wave
                self.spawn_timer += 1
                spawn_rate = max(80, 150 - self.current_wave * 5)  # Slower progression
                if self.spawn_timer >= spawn_rate:
                    self.spawn_enemy()
                    self.spawn_timer = 0
        
        # Check if wave is complete
        if len(self.enemies) == 0 and self.enemies_spawned_this_wave > 0:
            # Wave complete
            if not self.wave_complete:
                self.wave_complete = True
                self.wave_timer = 180  # 3 second break between waves
            
            self.wave_timer -= 1
            if self.wave_timer <= 0:
                # Start next wave
                self.current_wave += 1
                self.enemies_per_wave += 1  # Slower enemy increase
                self.enemies_spawned_this_wave = 0
                self.wave_complete = False
                self.is_boss_wave = False
                self.boss = None
                
                # Regenerate obstacles every 3 waves
                if self.current_wave % 3 == 0:
                    self.obstacles = self.create_obstacles()
        
        # Spawn powerups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= 600:  # Spawn every 10 seconds
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # Check game over
        if self.player.health <= 0:
            self.state = "menu"  # Return to menu instead of closing
    
    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "shop":
            self.draw_shop()
        elif self.state == "playing":
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu"""
        self.screen.fill(DARK_GRAY)
        
        # Title
        title_font = pygame.font.Font(None, 100)
        title_text = title_font.render("ZOMBIE PUNCHER", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 40)
        subtitle_text = subtitle_font.render("Abandoned City", True, GOLD)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Play button
        mouse_pos = pygame.mouse.get_pos()
        play_color = GREEN if self.play_button.collidepoint(mouse_pos) else DARK_GREEN
        pygame.draw.rect(self.screen, play_color, self.play_button)
        pygame.draw.rect(self.screen, WHITE, self.play_button, 3)
        play_text = self.font.render("PLAY", True, WHITE)
        play_rect = play_text.get_rect(center=self.play_button.center)
        self.screen.blit(play_text, play_rect)
        
        # Shop button
        shop_color = BLUE if self.shop_button.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(self.screen, shop_color, self.shop_button)
        pygame.draw.rect(self.screen, WHITE, self.shop_button, 3)
        shop_text = self.font.render("SHOP", True, WHITE)
        shop_rect = shop_text.get_rect(center=self.shop_button.center)
        self.screen.blit(shop_text, shop_rect)
        
        # Show coins
        coin_text = self.font.render(f"Coins: {self.player.coins}", True, GOLD)
        self.screen.blit(coin_text, (SCREEN_WIDTH // 2 - 80, 600))
    
    def draw_shop(self):
        """Draw the shop screen"""
        self.screen.fill(DARK_GRAY)
        
        # Title
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("SHOP", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Coins display
        coin_text = self.font.render(f"Coins: {self.player.coins}", True, GOLD)
        self.screen.blit(coin_text, (SCREEN_WIDTH // 2 - 80, 180))
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_color = RED if self.back_button.collidepoint(mouse_pos) else DARK_RED
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, WHITE, self.back_button, 3)
        back_text = pygame.font.Font(None, 30).render("BACK", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Sword item
        sword_button = pygame.Rect(SCREEN_WIDTH // 2 - 250, 300, 200, 100)
        if self.player.has_sword:
            pygame.draw.rect(self.screen, DARK_GREEN, sword_button)
            status_text = "OWNED"
        else:
            sword_color = GRAY if sword_button.collidepoint(mouse_pos) else DARK_GRAY
            pygame.draw.rect(self.screen, sword_color, sword_button)
            status_text = "200 Coins"
        pygame.draw.rect(self.screen, WHITE, sword_button, 3)
        
        sword_title = pygame.font.Font(None, 32).render("SWORD", True, WHITE)
        self.screen.blit(sword_title, (sword_button.x + 50, sword_button.y + 20))
        sword_desc = pygame.font.Font(None, 20).render("+50% Melee DMG", True, YELLOW)
        self.screen.blit(sword_desc, (sword_button.x + 30, sword_button.y + 50))
        sword_price = pygame.font.Font(None, 24).render(status_text, True, GOLD if not self.player.has_sword else GREEN)
        self.screen.blit(sword_price, (sword_button.x + 40, sword_button.y + 75))
        
        # Gun item
        gun_button = pygame.Rect(SCREEN_WIDTH // 2 + 50, 300, 200, 100)
        if self.player.has_gun:
            pygame.draw.rect(self.screen, DARK_GREEN, gun_button)
            status_text = "OWNED"
        else:
            gun_color = GRAY if gun_button.collidepoint(mouse_pos) else DARK_GRAY
            pygame.draw.rect(self.screen, gun_color, gun_button)
            status_text = "400 Coins"
        pygame.draw.rect(self.screen, WHITE, gun_button, 3)
        
        gun_title = pygame.font.Font(None, 32).render("GUN", True, WHITE)
        self.screen.blit(gun_title, (gun_button.x + 65, gun_button.y + 20))
        gun_desc = pygame.font.Font(None, 20).render("50 DMG Range", True, YELLOW)
        self.screen.blit(gun_desc, (gun_button.x + 35, gun_button.y + 50))
        gun_price = pygame.font.Font(None, 24).render(status_text, True, GOLD if not self.player.has_gun else GREEN)
        self.screen.blit(gun_price, (gun_button.x + 45, gun_button.y + 75))
        
        # Ammo refill (if player has gun)
        if self.player.has_gun:
            ammo_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 80)
            ammo_color = ORANGE if ammo_button.collidepoint(mouse_pos) else DARK_GRAY
            pygame.draw.rect(self.screen, ammo_color, ammo_button)
            pygame.draw.rect(self.screen, WHITE, ammo_button, 3)
            
            ammo_title = pygame.font.Font(None, 32).render("AMMO REFILL", True, WHITE)
            self.screen.blit(ammo_title, (ammo_button.x + 15, ammo_button.y + 15))
            ammo_desc = pygame.font.Font(None, 24).render("+30 Bullets", True, YELLOW)
            self.screen.blit(ammo_desc, (ammo_button.x + 45, ammo_button.y + 45))
            ammo_price = pygame.font.Font(None, 24).render("50 Coins", True, GOLD)
            self.screen.blit(ammo_price, (ammo_button.x + 55, ammo_button.y + 65))
    
    def draw_game(self):
        """Draw the game screen"""
        # Draw abandoned city background (asphalt)
        self.screen.fill(ASPHALT)
        
        # Draw road lines
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.rect(self.screen, YELLOW, (i, SCREEN_HEIGHT // 2 - 2, 50, 4))
        
        # Draw obstacles
        for obstacle in self.obstacles[1]:
            obstacle.draw(self.screen)
        
        # Draw game objects
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        self.player.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (10, 50))
        
        if self.is_boss_wave:
            wave_text = self.font.render(f"Wave: {self.current_wave} - BOSS!", True, GOLD)
        else:
            wave_text = self.font.render(f"Wave: {self.current_wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 90))
        
        # Draw level and kills
        level_text = self.font.render(f"Level: {self.player.level}", True, GOLD)
        self.screen.blit(level_text, (10, 130))
        
        kills_text = self.font.render(f"Kills: {self.player.kills}/{self.player.kills_for_next_level}", True, WHITE)
        self.screen.blit(kills_text, (10, 170))
        
        # Draw coins
        coin_text = self.font.render(f"Coins: {self.player.coins}", True, GOLD)
        self.screen.blit(coin_text, (SCREEN_WIDTH - 200, 10))
        
        # Draw ammo if player has gun
        if self.player.has_gun:
            ammo_text = self.font.render(f"Ammo: {self.player.gun_ammo}", True, YELLOW)
            self.screen.blit(ammo_text, (SCREEN_WIDTH - 200, 50))
        
        # Draw wave complete message
        if self.wave_complete:
            big_font = pygame.font.Font(None, 72)
            if self.is_boss_wave:
                wave_msg = big_font.render(f"BOSS DEFEATED!", True, GOLD)
            else:
                wave_msg = big_font.render(f"WAVE {self.current_wave} COMPLETE!", True, GOLD)
            text_rect = wave_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(wave_msg, text_rect)
        
        # Draw active powerup indicators
        small_font = pygame.font.Font(None, 24)
        ui_y = 210
        
        if self.player.invincible:
            inv_text = small_font.render(f"INVINCIBLE: {self.player.invincible_timer // 60}s", True, GOLD)
            self.screen.blit(inv_text, (10, ui_y))
            ui_y += 25
        
        if self.player.double_speed:
            speed_text = small_font.render(f"DOUBLE SPEED: {self.player.double_speed_timer // 60}s", True, CYAN)
            self.screen.blit(speed_text, (10, ui_y))
            ui_y += 25
        
        if self.player.damage_boost:
            damage_text = small_font.render(f"DAMAGE BOOST: {self.player.damage_boost_timer // 60}s", True, ORANGE)
            self.screen.blit(damage_text, (10, ui_y))
            ui_y += 25
        
        # Ground slam cooldown
        if self.player.ground_slam_cooldown > 0:
            slam_text = small_font.render(f"Ground Slam: {self.player.ground_slam_cooldown // 60}s", True, RED)
            self.screen.blit(slam_text, (10, ui_y))
        else:
            slam_text = small_font.render("Ground Slam: READY (R)", True, GREEN)
            self.screen.blit(slam_text, (10, ui_y))
        
        # Draw instructions
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            "WASD: Move",
            "Click/SPACE: Punch",
            "R: Ground Slam"
        ]
        if self.player.has_gun:
            instructions.append("G: Shoot Gun")
        
        y_offset = 100 if self.player.has_gun else 120
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, y_offset + i * 22))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
