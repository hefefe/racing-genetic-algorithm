import pygame
import time
import math
from utils import resize, rotate_center

TRACK_BORDER = resize(pygame.image.load("img/trasa_obrys.png"), 0.55, 0.55)
TRACK = resize(pygame.image.load("img/trasa.png"), 0.55, 0.55)
CAR = resize(pygame.image.load("img/autkoMINI.png"), 0.75, 0.75)
FINISH = pygame.image.load("img/meta.png")

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI")

FPS = 60


class Car:
    IMG = CAR
    START_POS = (300, 100)

    def __init__(self, max_vel, rotation_vel):

        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.3

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
        self.vel = max(self.vel - self.acceleration, -1 * self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle - 90)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        if self.vel>0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
            self.move()
        else:
            self.vel = min(self.vel + self.acceleration / 2, 0)
            self.move()


def draw(window, Car):
    window.blit(TRACK, (0, 0))
    window.blit(TRACK_BORDER, (0, 0))
    window.blit(FINISH, (0, 0))
    Car.draw(window)
    pygame.display.update()


run = True
clock = pygame.time.Clock()
carr = Car(12, 7)

while run:
    clock.tick(FPS)
    draw(WINDOW, carr)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        carr.rotate(left=True)
    if keys[pygame.K_d]:
        carr.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        carr.move_forward()
    if keys[pygame.K_s]:
        moved = True
        carr.move_backwards()
    if not moved:
        carr.reduce_speed()
pygame.quit()
