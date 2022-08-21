import pygame
import math
import random

from collision import AABB
from utils import bound_radian
from particles import ParticleSystem

# constants
WIDTH = 1280
HEIGHT = 512
FPS = 60

# basic pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

class Entity:
    entities = []
    def __init__(self):
        Entity.entities.append(self)

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

        pygame.draw.rect(screen, (255, 255, 255), outer_rect)
        pygame.draw.rect(screen, (255, 0, 0), health_rect)

class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.w = 5
        self.h = 5
        self.angle = angle

        self.collider = AABB(self.x, self.y, self.w, self.h)

        # checks if projectile hits a zombie
        self.hit = False

    def update(self, enemies):
        self.collider = AABB(self.x, self.y, self.w, self.h)
        self.x += math.cos(self.angle) * 5
        self.y += math.sin(self.angle) * 5

        for enemy in enemies:
            if AABB.check(self.collider, enemy.collider):
                enemy.health -= 25
                self.hit = True
                enemy.hit = True
                enemy.particle_system = ParticleSystem(enemy, self.angle, [2, random.randint(0, 20)/10-1], 15)

    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, (255, 255, 0), rect)

class Zombie(Entity):
    def __init__(self, x, y, entity):
        super().__init__()
        self.x = x
        self.y = y
        self.w = 15
        self.h = 15

        # collider
        self.collider = AABB(self.x, self.y, self.w, self.h)

        self.hit = False
        self.particle_system = None

        # entity that we are moving towards
        self.entity = entity

        # health
        self.health = 100

    def update(self):
        self.collider = AABB(self.x, self.y, self.w, self.h)
        angle = math.atan2(self.entity.y - self.y, self.entity.x - self.x)
        # move towards angle
        colliding = False

        for entity in Entity.entities:
            if isinstance(entity, Player) and AABB.check(self.collider, entity.collider):
                colliding = True
                entity.health.lose_health()
                break

        if not colliding:
            self.x += math.cos(angle)
            self.y += math.sin(angle)

    def draw(self):
        if self.hit:
            self.hit = self.particle_system.update(screen)

        rect = pygame.Rect(self.x, self.y, 15, 15)
        pygame.draw.rect(screen, (0, 255, 0), rect)

class Player(Entity):
    def __init__(self, x, y, w=15, h=15):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.colour = (255, 255, 255)

        # collision
        self.collider = AABB(self.x, self.y, self.w, self.h)

        # rotation
        self.angle = 0 # in radians
        self.dx = math.cos(self.angle) * 5
        self.dy = math.sin(self.angle) * 5

        # projectiles
        self.projectiles = []
        self.projectile_cooldown = 0
        self.cool_down_rate = 1/2 # half a second cooldown

        self.health = Health(self)

    def draw(self):
        # draw projectiles before player
        for p in self.projectiles:
            p.draw()
        # draw player
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, self.colour, rect)
        # draw laser
        pygame.draw.line(screen, (255, 0, 0), (self.x + (self.w//2), self.y + (self.h//2)), (self.x + (self.w//2) + self.dx * 3, self.y + (self.h//2) + self.dy * 3), 2)
        self.health.draw()

    def update(self, keys, enemies):
        self.collider = AABB(self.x, self.y, self.w, self.h)
        colliding = False
        # movement
        if keys[pygame.K_LEFT]:
            self.angle = bound_radian(self.angle + -0.04)
            self.dx = math.cos(self.angle) * 5
            self.dy = math.sin(self.angle) * 5
        if keys[pygame.K_RIGHT]:
            self.angle = bound_radian(self.angle +  0.04)
            self.dx = math.cos(self.angle) * 5
            self.dy = math.sin(self.angle) * 5
        if keys[pygame.K_UP]:
            updated_x = self.x + self.dx
            updated_y = self.y + self.dy
            updated_aabb = AABB(updated_x, updated_y, self.w, self.h)
            # check for collisions
            for enemy in enemies:
                if AABB.check(updated_aabb, enemy.collider):
                    colliding = True
                    break


            if not colliding:
                if updated_x >= 0 and updated_x + self.w <= WIDTH:
                    self.x = updated_x
                if updated_y >= 0 and updated_y + self.h <= HEIGHT:
                    self.y = updated_y

        if keys[pygame.K_DOWN]:
            updated_x = self.x - self.dx
            updated_y = self.y - self.dy
            updated_aabb = AABB(updated_x, updated_y, self.w, self.h)
            # check of collisions
            for enemy in enemies:
                if AABB.check(updated_aabb, enemy.collider):
                    colliding = True
                    break
            if not colliding:
                if updated_x >= 0 and updated_x + self.w <= WIDTH:
                    self.x = updated_x
                if updated_y >= 0 and updated_y + self.h <= HEIGHT:
                    self.y = updated_y

        if keys[pygame.K_SPACE]:
            if self.projectile_cooldown == 0:
                self.shoot_projectile()
                self.projectile_cooldown = FPS * self.cool_down_rate

        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1

        for p in self.projectiles[:]:
            # remove projectile if projectile is outside of the screen
            if (p.x + 5 < 0 or p.x + 5 > WIDTH - 5 or p.y + 5 < 0 or p.y + 5 > HEIGHT - 5) or p.hit:
                self.projectiles.remove(p)
            p.update(enemies)

    def shoot_projectile(self):
        projectile = Projectile(self.x + (self.w//2), self.y + (self.h//2), self.angle)
        self.projectiles.append(projectile)

player = Player(WIDTH//2, HEIGHT//2)

def timed_instantiate(entity, args, interval, collection=[]):
    """
    Instantiates entity with given args every interval frames
    """
    if not hasattr(timed_instantiate, "counter"):
        timed_instantiate.counter = 0
    if timed_instantiate.counter % interval == 0:
        collection.append(entity(*args))
    timed_instantiate.counter += 1
    return collection

zombies = []
# game loop
while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    # updating
    keys = pygame.key.get_pressed()
    player.update(keys, zombies)

    zombies = timed_instantiate(Zombie, (random.choice([-15, WIDTH + 15]), random.randint(0, HEIGHT), player), 90, zombies)

    for zombie in zombies:
        zombie.update()

    # remove dead zombies
    for zombie in zombies[:]:
        if zombie.health <= 0:
            zombies.remove(zombie)

    # drawing
    player.draw()
    for zombie in zombies:
        zombie.draw()

    pygame.display.update()
    clock.tick(FPS)
