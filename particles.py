import random
import pygame
import math

class Particle:
    def __init__(self, x, y, velocity, timer):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.timer = timer

class ParticleSystem:
    def __init__(self, entity, angle, velocity, timer):
        self.particles = []
        self.timer = timer
        self.counter = 0
        self.angle = angle
        self.entity = entity
        self.velocity = velocity

    def add_particle(self):
        self.particles.append(Particle(self.entity.x + (self.entity.w//2), self.entity.y + (self.entity.h//2), self.velocity, random.randint(3, 5)))

    def update(self, screen):
        if self.counter < self.timer:
            self.add_particle()
            self.counter += 1
        for particle in self.particles[:]:
            angle = self.angle - random.randint(0, 250)/100
            particle.x += math.cos(angle) * particle.velocity[0]
            particle.y -= math.sin(angle) * particle.velocity[1]
            particle.timer -= 0.1

            rect = pygame.Rect(int(particle.x), int(particle.y), int(particle.timer), int(particle.timer))
            pygame.draw.rect(screen, (255, 0, 0), rect)

            if particle.timer <= 0:
                self.particles.remove(particle)

        return self.counter < self.timer
