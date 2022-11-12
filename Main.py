import pygame
import time
import math

from Utils import resize, rotate_center

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

FPS = 100


class Car(pygame.sprite.Sprite):
    START_POS = (410, 605)

    def __init__(self):

        super().__init__()
        self.img = CAR
        self.max_vel = 12
        self.vel = 0
        self.rotation_vel = 7
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.3
        self.points = -1
        self.rect = self.img.get_rect(topleft=(self.x,self.y))

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, window):
        self.new_rect = rotate_center(window, self.img, (self.x, self.y), self.angle)
        self.more_radars()

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backwards(self):
        self.vel = max(self.vel - self.acceleration, -1 * self.max_vel / 2)
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
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        overlap = mask.overlap(car_mask, offset)
        return overlap

    def add_point(self, amount):
        self.points += amount

    def movement(self):
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_a]:
            self.rotate(left=True)
        if keys[pygame.K_d]:
            self.rotate(right=True)
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            moved = True
            self.move_forward()
        if keys[pygame.K_s]:
            moved = True
            self.move_backwards()
        if not moved:
            self.reduce_speed()

    def radar(self, radar_angle):
        length = 0
        x = int(self.new_rect.center[0])
        y = int(self.new_rect.center[1])

        try:
            while not WINDOW.get_at((x, y)) == pygame.Color(255, 0, 0, 255) and length < 150:
                length += 1
                x = int(self.new_rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(self.new_rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)
        except:
            print("")
        # Draw Radar
        pygame.draw.line(WINDOW, (255, 255, 255, 255), self.new_rect.center, (x, y), 1)
        pygame.draw.circle(WINDOW, (0, 255, 0, 0), (x, y), 3)

        return self.angle + radar_angle, length

    def more_radars(self):
        self.radars = [self.radar(-90), self.radar(-60), self.radar(-30), self.radar(0), self.radar(30), self.radar(60), self.radar(90)]


def draw(window, car):

    window.blit(TRACK, (0, 0))
    window.blit(TRACK_BORDER, (0, 0))
    window.blit(FINISH, FINISH_POS)
    car.draw(window)
    pygame.display.update()


run = True
clock = pygame.time.Clock()
carr = Car()
i = True
while run:
    clock.tick(FPS)
    draw(WINDOW, carr)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    carr.movement()

    if carr.collision(TRACK_BORDER_MASK) is not None:
        print("kolizja")

    poi = carr.collision(FINISH_MASK, *FINISH_POS)
    if poi is not None:
        if i is True and poi[0] < 5:
            carr.add_point(1)
            print(carr.points)
            i = False
        elif i is True and poi[0] > 60:
            carr.add_point(-1)
            print(carr.points)
            i = False
    if poi is None:
        i = True
pygame.quit()
