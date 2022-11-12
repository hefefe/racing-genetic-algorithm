import pygame
import time
import numpy
import math
import random

from Utils import resize, rotate_center

TRACK_BORDER = resize(pygame.image.load("img/trasa_obrys.png"), 0.55, 0.55)
TRACK = resize(pygame.image.load("img/trasa.png"), 0.55, 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

CAR = resize(pygame.image.load("img/autkoMINI.png"), 0.65, 0.65)

FINISH = resize(pygame.image.load("img/meta.png"), 0.45, 0.49)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (490, 580)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI")

FPS = 100


class Car(pygame.sprite.Sprite):
    START_POS = (410, 605)

    def __init__(self):
        super().__init__()
        self.radars = None
        self.new_rect = None
        self.rotated_image = None
        self.img = CAR
        self.max_vel = 12
        self.vel = 0
        self.rotation_vel = 4
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.3
        self.points = -1
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
        self.multiplier = 1
        self.base_number = 7
        self.hidden_number = 6
        self.out_number = 3

        self.brain()
        self.random_weights()
        self.car_alive = True

    def rotate(self):
        # if left:
            self.angle += self.rotation_vel*self.out_sums[1]*self.multiplier
        # elif right:
            self.angle -= self.rotation_vel*self.out_sums[2]*self.multiplier

    def draw(self, window):
        self.new_rect, self.rotated_image = rotate_center(window, self.img, (self.x, self.y), self.angle)
        self.more_radars()
        self.feedforward()
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration*self.out_sums[0], self.max_vel)*self.multiplier
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
        self.points += amount

    def movement(self):
        # moved = False
        # if self.out_sums[1]==1:
            self.rotate()
        # if self.out_sums[2]==1:
            self.rotate()
        # if self.out_sums[0]==1:
        #     moved = True
            self.move_forward()
        # else:
        #     self.reduce_speed()
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
        # if wrong, change to unimodal sigmoidal function
        return (150-length)

    def more_radars(self):
        self.radars = [self.radar(-90), self.radar(-60), self.radar(-30), self.radar(0), self.radar(30), self.radar(60),
                       self.radar(90)]
    def brain(self):
        self.base_weights = numpy.zeros((self.base_number,self.base_number+1))
        self.hidden_weights = numpy.zeros((self.hidden_number,self.base_number+1))
        self.out_weights = numpy.zeros((self.out_number, self.hidden_number+1))
        self.base_sums = numpy.zeros(7)
        self.hidden_sums = numpy.zeros(6)
        self.out_sums= numpy.zeros(4)

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
            self.base_sums[i] += self.base_weights[i][0]
            for j in range(self.base_number):
                self.base_sums[i] += self.radars[j]*self.base_weights[i][j+1]
            self.base_sums[i] = 1/(1+math.exp(-self.base_sums[i]))

        for i in range(self.hidden_number):
            self.hidden_sums[i] += self.hidden_weights[i][0]
            for j in range(self.hidden_number):
                self.hidden_sums[i] += self.base_sums[j]*self.hidden_weights[i][j+1]
            self.hidden_sums[i] = 1/(1+math.exp(-self.hidden_sums[i]))

        for i in range(self.out_number):
            self.out_sums[i] += self.out_weights[i][0]
            for j in range(self.out_number):
                self.out_sums[i] += self.hidden_sums[j]*self.out_weights[i][j+1]
            self.out_sums[i] = 1/(1+math.exp(-self.out_sums[i]))
            # if self.out_sums[i]>0:
            #     self.out_sums[i] = 1
            # else:
            #     self.out_sums[i] = 0


def draw(window):
    window.blit(TRACK, (0, 0))
    window.blit(TRACK_BORDER, (0, 0))
    window.blit(FINISH, FINISH_POS)


run = True
clock = pygame.time.Clock()
cars = []
for i in range(30):
    car = Car()
    cars.append(car)
i = True
while run:
    clock.tick(FPS)
    draw(WINDOW)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    for car in cars:
        car.movement()
        car.draw(WINDOW)
        if car.collision(TRACK_BORDER_MASK) is not None:
            car.stop()
    pygame.display.update()

    # poi = carr.collision(FINISH_MASK, *FINISH_POS)
    # if poi is not None:
    #     if i is True and poi[0] < 5:
    #         carr.add_point(1)
    #         print(carr.points)
    #         i = False
    #     elif i is True and poi[0] > 60:
    #         carr.add_point(-1)
    #         print(carr.points)
    #         i = False
    # if poi is None:
    #     i = True
pygame.quit()
