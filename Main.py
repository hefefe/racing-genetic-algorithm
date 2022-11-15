import pygame
import time
import numpy
import math
import random
import threading

from Utils import resize, rotate_center

TRACK_BORDER = resize(pygame.image.load("img/trasa_obrys.png"), 0.55, 0.55)
TRACK = resize(pygame.image.load("img/trasa.png"), 0.55, 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

CAR = resize(pygame.image.load("img/autkoMINI.png"), 0.65, 0.65)

FINISH = resize(pygame.image.load("img/meta.png"), 0.45, 0.49)
FINISH_POS = (490, 580)

CHECKPOINTS = resize(pygame.image.load("img/linie.png"), 0.55, 0.55)
CHECKPOINTS_MASK = pygame.mask.from_surface(CHECKPOINTS)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI")

FPS = 60


class Car(pygame.sprite.Sprite):
    START_POS = (570, 605)

    def __init__(self,base = numpy.zeros((7,8)),hidden = numpy.zeros((5,8)),out = numpy.zeros((3,6))):
        super().__init__()
        self.ticks = 0
        self.radars = None
        self.new_rect = None
        self.rotated_image = None
        self.img = CAR
        self.max_vel = 8
        self.vel = 0
        self.rotation_vel = 4
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.3
        self.points = 0
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
        self.multiplier = 1
        self.base_number = 7
        self.hidden_number = 5
        self.out_number = 3
        self.time_alive = 0
        self.i = True

        self.brain()
        if numpy.all((base == 0)):
            self.random_weights()
        else:
            self.set_weights(base, hidden, out)
        self.car_alive = True

    def draw(self, window):
        self.new_rect, self.rotated_image = rotate_center(window, self.img, (self.x, self.y), self.angle)
        self.more_radars()
        self.movement()
        self.feedforward()
        self.time_alive += 1/10 * self.out_outputs[0] * self.multiplier
        self.ticks += 1/10
        if self.ticks > 300 or car.collision(TRACK_BORDER_MASK) is not None:
            self.stop()
        if self.collision(CHECKPOINTS_MASK, 0,0) is not None:
            if self.i==True:
                self.add_point(1)
                self.i=False
        else:
            self.i=True

    def rotate(self):
        # if left:
            self.angle += self.rotation_vel * self.out_outputs[1] * self.multiplier
        # elif right:
            self.angle -= self.rotation_vel * self.out_outputs[2] * self.multiplier

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration * self.out_outputs[0], self.max_vel) * self.multiplier
        self.move()

    # def move_backwards(self):
    #     self.vel = max(self.vel - self.acceleration*self.out_sums[1], -1 * self.max_vel / 2)*self.multiplier
    #     self.move()

    def move(self):
        radians = math.radians(self.angle)
        horizontal = math.cos(radians) * self.vel
        vertical = math.sin(radians) * self.vel
        self.y -= vertical
        self.x += horizontal

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
            self.move()
        else:
            self.vel = min(self.vel + self.acceleration / 2, 0)
            self.move()

    def collision(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.rotated_image)
        offset = (int(self.new_rect.x - x), int(self.new_rect.y - y))
        overlap = mask.overlap(car_mask, offset)
        return overlap

    def add_point(self, amount):
        self.points += amount * self.multiplier

    def movement(self):
            self.rotate()
            self.move_forward()

    def stop(self):
        self.multiplier = 0
        self.car_alive = False

    def radar(self, radar_angle):
        length = 0
        x = int(self.new_rect.center[0])
        y = int(self.new_rect.center[1])

        try:
            while not WINDOW.get_at((x, y)) == pygame.Color(67, 42, 19, 255) and length < 150:
                length += 1
                x = int(self.new_rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(self.new_rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)
        except:
            print("")
        # pygame.draw.line(WINDOW, (255, 255, 255, 255), self.new_rect.center, (x, y), 1)
        if (150-length)/100 <= 0:
            return (150-length)/100
        else:
            return 1

    def more_radars(self):
        self.radars = [self.radar(-90), self.radar(-60), self.radar(-30), self.radar(0), self.radar(30), self.radar(60),
                       self.radar(90)]

    def fitness(self):
        fitness_score = self.points*10 + self.time_alive
        return fitness_score

    def set_weights(self, base, hidden, out):

        for i in range(self.base_number):
            for j in range(self.base_number+1):
                self.base_weights[i][j] = base[i][j]
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                self.hidden_weights[i][j] = hidden[i][j]
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                self.out_weights[i][j] = out[i][j]

    def get_weights(self):
        return self.base_weights, self.hidden_weights, self.out_weights

    def mutate(self, mutation_rate):
        for i in range(self.base_number):
            for j in range(self.base_number+1):
                if random.random() <= mutation_rate:
                    self.base_weights[i][j] = self.base_weights[i][j]+(2*random.random() -1)
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                if random.random() <= mutation_rate:
                    self.hidden_weights[i][j] = self.hidden_weights[i][j]+(2*random.random() -1)
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                if random.random() <= mutation_rate:
                    self.out_weights[i][j] = self.out_weights[i][j]+(2*random.random() -1)

    def get_alive(self):
        return self.car_alive

    def brain(self):
        self.base_weights = numpy.zeros((self.base_number,self.base_number+1))
        self.hidden_weights = numpy.zeros((self.hidden_number,self.base_number+1))
        self.out_weights = numpy.zeros((self.out_number, self.hidden_number+1))
        self.base_outputs = numpy.zeros(self.base_number)
        self.hidden_outputs = numpy.zeros(self.hidden_number)
        self.out_outputs= numpy.zeros(self.out_number)

    def random_weights(self):
        for i in range(self.base_number):
            for j in range(self.base_number+1):
                self.base_weights[i][j] = (2*random.random() -1)
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                self.hidden_weights[i][j] = (2*random.random() -1)
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                self.out_weights[i][j] = (2*random.random() -1)

    def feedforward(self):
        for i in range(self.base_number):
            self.base_outputs[i] += self.base_weights[i][0]
            for j in range(self.base_number):
                self.base_outputs[i] += self.radars[j] * self.base_weights[i][j + 1]
            self.base_outputs[i] = 1 / (1 + math.exp(-self.base_outputs[i]))
        for i in range(self.hidden_number):
            self.hidden_outputs[i] += self.hidden_weights[i][0]
            for j in range(self.hidden_number):
                self.hidden_outputs[i] += self.base_outputs[j] * self.hidden_weights[i][j + 1]
            self.hidden_outputs[i] = 1 / (1 + math.exp(-self.hidden_outputs[i]))
        for i in range(self.out_number):
            self.out_outputs[i] += self.out_weights[i][0]
            for j in range(self.out_number):
                self.out_outputs[i] += self.hidden_outputs[j] * self.out_weights[i][j + 1]
            self.out_outputs[i] = 1 / (1 + math.exp(-self.out_outputs[i]))
            # if self.out_sums[i]>0:
            #     self.out_sums[i] = 1
            # else:
            #     self.out_sums[i] = 0


def draw(window):
    window.blit(CHECKPOINTS,(0,0))
    window.blit(TRACK, (0, 0))
    window.blit(FINISH, FINISH_POS)
    window.blit(TRACK_BORDER, (0, 0))

run = True
clock = pygame.time.Clock()
cars = []
cars_amount = 10
deads = 0
best_fitness = 0
base = numpy.zeros((7, 8))
hidden = numpy.zeros((5, 8))
out = numpy.zeros((3, 6))
for i in range(cars_amount):
    cars.append(Car())

i = True
while run:
    clock.tick(FPS)
    draw(WINDOW)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    for car in cars:
        car.draw(WINDOW)
        car_alive = car.get_alive()
        if not car.get_alive():
            deads+=1
        if deads == cars_amount:
            for car in cars:
                fitness = car.fitness()
                if fitness >= best_fitness:
                    best_fitness = fitness
                    base, hidden, out = car.get_weights()
            cars.clear()
            for i in range(cars_amount):
                car = Car(base, hidden, out)
                car.mutate(0.2)
                cars.append(car)
    deads = 0
    best_fitness = 0
    pygame.display.update()
pygame.quit()
