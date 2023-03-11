import pygame

# See kood pärineb siit: http://codingwithruss.com/pygame/shooter/music.html

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self, surf):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(surf, self.colour, (0 - self.fade_counter, 0, surf.get_width() // 2, surf.get_height()))
            pygame.draw.rect(surf, self.colour, (surf.get_width() // 2 + self.fade_counter, 0, surf.get_width(), surf.get_height()))
            pygame.draw.rect(surf, self.colour, (0, 0 - self.fade_counter, surf.get_width(), surf.get_height() // 2))
            pygame.draw.rect(surf, self.colour, (0, surf.get_height() // 2 +self.fade_counter, surf.get_width(), surf.get_height()))
        if self.direction == 2:
            pygame.draw.rect(surf, self.colour, (0, 0, surf.get_width(), 0 + self.fade_counter))
        if self.fade_counter >= surf.get_width():
            fade_complete = True

        return fade_complete