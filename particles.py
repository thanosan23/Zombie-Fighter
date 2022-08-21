import random
import math

import pygame

class Particle:
    def __init__(self, x, y, velocity, timer):
        self.x_pos = x
        self.y_pos = y
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
        self.particles.append(Particle(self.entity.pos.x_pos + (self.entity.pos.width//2),
                                       self.entity.pos.y_pos + (self.entity.pos.height//2),
                                       self.velocity,
                                       random.randint(3, 5)))

    def update(self, screen):
        if self.counter < self.timer:
            self.add_particle()
            self.counter += 1
        for particle in self.particles[:]:
            angle = self.angle - random.randint(0, 250)/100
            particle.x_pos += math.cos(angle) * particle.velocity[0]
            particle.y_pos -= math.sin(angle) * particle.velocity[1]
            particle.timer -= 0.1

            rect = pygame.Rect(int(particle.x_pos), int(particle.y_pos),
                               int(particle.timer), int(particle.timer))
            pygame.draw.rect(screen, (255, 0, 0), rect)

            if particle.timer <= 0:
                self.particles.remove(particle)

        return self.counter < self.timer
