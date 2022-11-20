import pygame
import numpy
import math
import random

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

cars_amount = 20
base_number = 7
hidden_number = 5
out_number = 3
weights_amount = base_number*(base_number+1)+hidden_number*(base_number+1)+out_number*(hidden_number+1)
cross_probability = 0.7
mutation_probability = 1/weights_amount * 2
gene_min_value = -10
gene_max_value = 10
time_to_death = 60


class Car(pygame.sprite.Sprite):
    START_POS = (490, 620)

    def __init__(self):
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
        self.base_number = base_number
        self.hidden_number = hidden_number
        self.out_number = out_number
        self.time_alive = 0
        self.multiple_intersections = True
        self.base_weights = numpy.zeros((self.base_number, self.base_number + 1))
        self.hidden_weights = numpy.zeros((self.hidden_number, self.base_number + 1))
        self.out_weights = numpy.zeros((self.out_number, self.hidden_number + 1))
        self.base_outputs = numpy.zeros(self.base_number)
        self.hidden_outputs = numpy.zeros(self.hidden_number)
        self.out_outputs = numpy.zeros(self.out_number)
        self.random_weights()
        self.car_alive = True

    def draw(self, window):
        self.new_rect, self.rotated_image = rotate_center(window, self.img, (self.x, self.y), self.angle)
        self.more_radars()
        self.movement()
        self.feedforward()
        if self.points >= 1:
            self.time_alive += self.vel * self.multiplier
        self.ticks += 1/10
        if self.ticks > time_to_death or car.collision(TRACK_BORDER_MASK) is not None:
            self.stop()
        if self.collision(CHECKPOINTS_MASK, 0, 0) is not None:
            if self.multiple_intersections:
                self.add_point(1)
                self.multiple_intersections = False
        else:
            self.multiple_intersections = True

    def rotate(self):
        self.angle += self.rotation_vel * self.out_outputs[1] * self.multiplier
        self.angle -= self.rotation_vel * self.out_outputs[2] * self.multiplier

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration * self.out_outputs[0], self.max_vel) * self.multiplier
        self.move()

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
            pass
        if (150-length)/100 < 1:
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
        weights = []
        for i in range(self.base_number):
            for j in range(self.base_number+1):
                weights.append(self.base_weights[i][j])
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                weights.append(self.hidden_weights[i][j])
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                weights.append(self.out_weights[i][j])
        return weights

    def mutate(self):
        for i in range(self.base_number):
            for j in range(self.base_number+1):
                if random.random() <= mutation_probability:
                    self.base_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                if random.random() <= mutation_probability:
                    self.hidden_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                if random.random() <= mutation_probability:
                    self.out_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)

    def get_alive(self):
        return self.car_alive

    def random_weights(self):
        for i in range(self.base_number):
            for j in range(self.base_number+1):
                self.base_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)
        for i in range(self.hidden_number):
            for j in range(self.base_number+1):
                self.hidden_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)
        for i in range(self.out_number):
            for j in range(self.hidden_number+1):
                self.out_weights[i][j] = random.randrange(gene_min_value, gene_max_value+1)

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


def draw(window):
    window.blit(CHECKPOINTS, (0, 0))
    window.blit(TRACK, (0, 0))
    window.blit(FINISH, FINISH_POS)
    window.blit(TRACK_BORDER, (0, 0))


def change_to_multiple_2d_arrays(array):
    base = numpy.zeros((base_number, base_number+1))
    hidden = numpy.zeros((hidden_number, base_number+1))
    out = numpy.zeros((out_number, hidden_number+1))
    incrementator = 0
    for i in range(base_number):
        for j in range(base_number + 1):
            base[i][j] = array[incrementator]
            incrementator += 1
    for i in range(hidden_number):
        for j in range(base_number + 1):
            hidden[i][j] = array[incrementator]
            incrementator += 1
    for i in range(out_number):
        for j in range(hidden_number + 1):
            out[i][j] = array[incrementator]
            incrementator += 1
    return base, hidden, out


run = True
clock = pygame.time.Clock()
cars = []
cars2 = []
cars3 = []
cars3_indexes = []
deads = 0
best_fitness = 0
best_weights = []
for i in range(cars_amount):
    cars.append(Car())

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
            deads += 1
    if deads == cars_amount:
        for car in cars:
            fitness = car.fitness()
            if best_fitness < fitness:
                best_fitness = car.fitness()
                best_weights = car.get_weights()
        rand1 = random.sample(range(0, cars_amount), cars_amount)
        rand2 = random.sample(range(0, cars_amount), cars_amount)
        for i in range(len(rand1)):
            if i % 2 == 0:
                car_fitness1 = cars[rand1[i]].fitness()
                car_fitness2 = cars[rand1[i+1]].fitness()
                car_fitness3 = cars[rand2[i]].fitness()
                car_fitness4 = cars[rand2[i+1]].fitness()
                if car_fitness1 >= car_fitness2:
                    cars2.append(cars[rand1[i]])
                else:
                    cars2.append(cars[rand1[i+1]])
                if car_fitness3 >= car_fitness4:
                    cars2.append(cars[rand2[i]])
                else:
                    cars2.append(cars[rand2[i+1]])
        for i in range(len(cars2)):
            if random.random() <= cross_probability:
                cars3.append(cars2[i])
                cars3_indexes.append(i)
        if len(cars3) >= 2:
            if len(cars3) % 2 == 1:
                cars3.pop()
                cars3_indexes.pop()
            rand3 = random.sample(range(0, len(cars3)), len(cars3))
            for i in range(len(cars3)):
                if i % 2 == 0:
                    rand_cross = random.randrange(0, weights_amount)
                    car_weights1 = cars3[rand3[i]].get_weights()
                    car_weights2 = cars3[rand3[i+1]].get_weights()
                    car_subweight1 = car_weights1[rand_cross:]
                    car_subweight2 = car_weights2[rand_cross:]
                    car_weights1[rand_cross:] = car_subweight2
                    car_weights2[rand_cross:] = car_subweight1
                    cars3[rand3[i]].set_weights(*change_to_multiple_2d_arrays(car_weights1))
                    cars3[rand3[i+1]].set_weights(*change_to_multiple_2d_arrays(car_weights2))
            for i in range(len(cars3)):
                cars2[cars3_indexes[i]] = cars3[i]
        for i in range(len(cars2)):
            cars2[i].mutate()
        for i in range(cars_amount):
            cars[i] = Car()
            cars[i].set_weights(*change_to_multiple_2d_arrays(cars2[i].get_weights()))
        rand = random.randrange(0, cars_amount)
        cars[rand].set_weights(*change_to_multiple_2d_arrays(best_weights))

    cars2 = []
    cars3 = []
    cars3_indexes = []
    deads = 0
    pygame.display.update()
pygame.quit()
