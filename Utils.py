import pygame


def resize(img, xfactor, yfactor):

    size = round(img.get_width()*xfactor), round(img.get_height()*yfactor)
    return pygame.transform.scale(img, size)


def rotate_center(win, img, top_left, angle):

    rotated_image = pygame.transform.rotate(img, angle)
    new_rect = rotated_image.get_rect(center=img.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)
    return new_rect