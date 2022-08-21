import math
import random
import sys
import pygame

from collision import AABB
from utils import bound_radian
from particles import ParticleSystem

# constants
WIDTH = 1280
HEIGHT = 512
FPS = 60

# basic pygame setup
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
CLOCK = pygame.time.Clock()

class Entity:
    entities = []
    def __init__(self):
        Entity.entities.append(self)

class Pos:
    def __init__(self, x_pos, y_pos, width, height):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height

    def __str__(self):
        return f"{self.x_pos}, {self.y_pos}"

class Health:
    def __init__(self, entity, damage=1):
        self.entity = entity
        self.damage = damage
        self.health = 100

    def lose_health(self):
        self.health -= self.damage
        self.health = max(self.health, 0)

    def draw(self):
        outer_rect = pygame.Rect(10, 10, 100, 5)
        health_rect = pygame.Rect(10, 10, self.health, 5)

        pygame.draw.rect(SCREEN, (255, 255, 255), outer_rect)
        pygame.draw.rect(SCREEN, (255, 0, 0), health_rect)

class Projectile:
    def __init__(self, x, y, angle):
        self.pos = Pos(x, y, 5, 5)
        self.angle = angle

        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)

        # checks if projectile hits a zombie
        self.hit = False

    def update(self, enemies):
        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)
        self.pos.x_pos += math.cos(self.angle) * 5
        self.pos.y_pos += math.sin(self.angle) * 5

        for enemy in enemies:
            if AABB.check(self.collider, enemy.collider):
                enemy.health -= 25
                self.hit = True
                enemy.hit = True
                enemy.particle_system = ParticleSystem(enemy,
                                                       self.angle,
                                                       [2, random.randint(0, 20)/10-1], 15)

    def draw(self):
        rect = pygame.Rect(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)
        pygame.draw.rect(SCREEN, (255, 255, 0), rect)

class Zombie(Entity):
    def __init__(self, x, y, entity):
        super().__init__()
        self.pos = Pos(x, y, 15, 15)

        # collider
        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)

        self.hit = False
        self.particle_system = None

        # entity that we are moving towards
        self.entity = entity

        # health
        self.health = 100

    def update(self):
        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)
        angle = math.atan2(self.entity.pos.y_pos - self.pos.y_pos,
                           self.entity.pos.x_pos - self.pos.x_pos)
        # move towards angle
        colliding = False

        for entity in Entity.entities:
            if isinstance(entity, Player) and AABB.check(self.collider, entity.collider):
                colliding = True
                entity.health.lose_health()
                break
        if not colliding:
            self.pos.x_pos += math.cos(angle)
            self.pos.y_pos += math.sin(angle)

    def draw(self):
        if self.hit:
            self.hit = self.particle_system.update(SCREEN)

        rect = pygame.Rect(self.pos.x_pos, self.pos.y_pos, 15, 15)
        pygame.draw.rect(SCREEN, (0, 255, 0), rect)

class Player(Entity):
    def __init__(self, x, y, w=15, h=15):
        super().__init__()
        self.pos = Pos(x, y, w, h)

        # collision
        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)

        # rotation
        self.angle = 0 # in radians
        self.delta_x = math.cos(self.angle) * 5
        self.delta_y = math.sin(self.angle) * 5

        # projectiles
        self.projectiles = []
        self.projectile_cooldown = 0
        self.cool_down_rate = 1/2 # half a second cooldown

        self.health = Health(self)

    def draw(self):
        # draw projectiles before player
        for projectile in self.projectiles:
            projectile.draw()
        # draw player
        rect = pygame.Rect(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)
        pygame.draw.rect(SCREEN, (255, 255, 255), rect)
        # draw laser
        pygame.draw.line(SCREEN, (255, 0, 0), (self.pos.x_pos + (self.pos.width//2),
                                               self.pos.y_pos + (self.pos.height//2)),
                         (self.pos.x_pos + (self.pos.width//2) + self.delta_x * 3,
                          self.pos.y_pos + (self.pos.height//2) + self.delta_y * 3), 2)
        self.health.draw()

    def update(self, keys, enemies):
        self.collider = AABB(self.pos.x_pos, self.pos.y_pos, self.pos.width, self.pos.height)
        colliding = False
        # movement
        if keys[pygame.K_LEFT]:
            self.angle = bound_radian(self.angle + -0.04)
            self.delta_x = math.cos(self.angle) * 5
            self.delta_y = math.sin(self.angle) * 5
        if keys[pygame.K_RIGHT]:
            self.angle = bound_radian(self.angle +  0.04)
            self.delta_x = math.cos(self.angle) * 5
            self.delta_y = math.sin(self.angle) * 5
        if keys[pygame.K_UP]:
            updated_x = self.pos.x_pos + self.delta_x
            updated_y = self.pos.y_pos + self.delta_y
            updated_aabb = AABB(updated_x, updated_y, self.pos.width, self.pos.height)
            # check for collisions
            for enemy in enemies:
                if AABB.check(updated_aabb, enemy.collider):
                    colliding = True
                    break

            if not colliding:
                if updated_x >= 0 and updated_x + self.pos.width <= WIDTH:
                    self.pos.x_pos = updated_x
                if updated_y >= 0 and updated_y + self.pos.height <= HEIGHT:
                    self.pos.y_pos = updated_y

        if keys[pygame.K_DOWN]:
            updated_x = self.pos.x_pos - self.delta_x
            updated_y = self.pos.y_pos - self.delta_y
            updated_aabb = AABB(updated_x, updated_y, self.pos.width, self.pos.height)
            # check of collisions
            for enemy in enemies:
                if AABB.check(updated_aabb, enemy.collider):
                    colliding = True
                    break
            if not colliding:
                if updated_x >= 0 and updated_x + self.pos.width <= WIDTH:
                    self.pos.x_pos = updated_x
                if updated_y >= 0 and updated_y + self.pos.height <= HEIGHT:
                    self.pos.y_pos = updated_y

        if keys[pygame.K_SPACE]:
            if self.projectile_cooldown == 0:
                self.shoot_projectile()
                self.projectile_cooldown = FPS * self.cool_down_rate

        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1

        for projectile in self.projectiles[:]:
            # remove projectile if projectile is outside of the SCREEN
            if (projectile.pos.x_pos + 5 < 0
                    or projectile.pos.x_pos + 5 > WIDTH - 5
                    or projectile.pos.y_pos + 5 < 0 or
                    projectile.pos.y_pos + 5 > HEIGHT - 5) or projectile.hit:
                self.projectiles.remove(projectile)
            projectile.update(enemies)

    def shoot_projectile(self):
        projectile = Projectile(self.pos.x_pos + (self.pos.width//2),
                                self.pos.y_pos + (self.pos.height//2), self.angle)
        self.projectiles.append(projectile)

PLAYER = Player(WIDTH//2, HEIGHT//2)

def timed_instantiate(entity, args, interval, collection):
    """
    Instantiates entity with given args every interval frames
    """
    if not hasattr(timed_instantiate, "counter"):
        timed_instantiate.counter = 0
    if timed_instantiate.counter % interval == 0:
        collection.append(entity(*args))
    timed_instantiate.counter += 1
    return collection

ZOMBIES = []
# game loop
while True:
    SCREEN.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    # updating
    KEYS = pygame.key.get_pressed()
    PLAYER.update(KEYS, ZOMBIES)

    ZOMBIES = timed_instantiate(Zombie, (random.choice([-15, WIDTH + 15]),
                                         random.randint(0, HEIGHT), PLAYER), 90, ZOMBIES)

    for zombie in ZOMBIES:
        zombie.update()

    # remove dead zombies
    for zombie in ZOMBIES[:]:
        if zombie.health <= 0:
            ZOMBIES.remove(zombie)

    # drawing
    PLAYER.draw()
    for zombie in ZOMBIES:
        zombie.draw()

    pygame.display.update()
    CLOCK.tick(FPS)
