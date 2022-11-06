import pygame
import time
import math
from utils import resize, rotate_center

TRACK_BORDER = resize(pygame.image.load("img/trasa_obrys.png"), 0.55, 0.55)
TRACK = resize(pygame.image.load("img/trasa.png"), 0.55, 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

CAR = resize(pygame.image.load("img/autkoMINI.png"), 0.65, 0.65)

FINISH = resize(pygame.image.load("img/meta.png"), 0.55, 0.56)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (490, 572)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI")

FPS = 60


class Car:
    START_POS = (410, 605)

    def __init__(self):

        self.img = CAR
        self.max_vel = 12
        self.vel = 0
        self.rotation_vel = 7
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.3
        self.points = -1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, window):
        rotate_center(window, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backwards(self):
        self.vel = max(self.vel - self.acceleration, -1 * self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle - 90)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
            self.move()
        else:
            self.vel = min(self.vel + self.acceleration / 2, 0)
            self.move()

    def collision(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        overlap = mask.overlap(car_mask, offset)
        return overlap

    def add_point(self, amount):
        self.points += amount


def draw(window, car):
    window.blit(TRACK, (0, 0))
    window.blit(TRACK_BORDER, (0, 0))
    window.blit(FINISH, FINISH_POS)
    car.draw(window)
    pygame.display.update()


def movement():
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        carr.rotate(left=True)
    if keys[pygame.K_d]:
        carr.rotate(right=True)
    if keys[pygame.K_w] and not keys[pygame.K_s]:
        moved = True
        carr.move_forward()
    if keys[pygame.K_s]:
        moved = True
        carr.move_backwards()
    if not moved:
        carr.reduce_speed()


run = True
clock = pygame.time.Clock()
carr = Car()

i = 0
while run:
    clock.tick(FPS)
    draw(WINDOW, carr)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    movement()

    if carr.collision(TRACK_BORDER_MASK) is not None:
        print("kolizja")

    poi = carr.collision(FINISH_MASK, *FINISH_POS)
    if poi is not None:
        if i == 0 and poi[0] < 5:
            carr.add_point(1)
            print(carr.points)
            i += 1
        elif i == 0 and poi[0] > 60:
            carr.add_point(-1)
            print(carr.points)
            i += 1
    if poi is None:
        i = 0
pygame.quit()
