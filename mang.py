import pygame, sys, os, time, random, json
from screen_fade import ScreenFade
from pygame.locals import *

# Mäng "Taevast sajab lihapalle"
# Autor: Ingemar Tamm (2022)
# Käivitamiseks on vaja Python3 ja PyGame.

pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Taevast sajab lihapalle')
display = pygame.Surface((200, 150))
clock = pygame.time.Clock()

if not os.path.isfile('save.txt'):
    save_file = open('save.txt', 'w')
    save_file.write(json.dumps({'pos': [100, 50], 'level': 1, 'health': 3, 'finished': False})) 
    save_file.close()

save_file = open('save.txt', 'r')
info = json.loads(save_file.read())
save_file.close()

def load_img(path, colorkey=None, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if colorkey: img.set_colorkey(colorkey)
    if scale: img = pygame.transform.scale(img, (scale))
    return img

def load_sound(name):
    return pygame.mixer.Sound('data/sfx/' + name)

def load_dir(path):
    image_dir = {}
    for file in os.listdir(path):
        try:
            image_dir[file.split('.')[0]] = load_img(path + "/" + file, (0, 0, 0)).convert_alpha()
        except pygame.error:
            continue
    return image_dir

class Meatball:

    def __init__(self, pos, speed):
        self.img = load_img('data/images/meatball.png')
        self.pos = list(pos)
        self.velocity = [0, 0]
        self.speed = speed
    
    @property
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], 16, 16)
    
    def update(self, target):
        if self.rect.colliderect(target.rect) and not target.protection:
            return [True, 'target']

        self.velocity[1] += self.speed / 100
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        if self.pos[1] >= 121:
            return [True, 'ground']
        else:
            return [False, 'none']

    def render(self, surf):
        surf.blit(self.img, self.pos)
class Player:

    def __init__(self, info):
        self.action = 'idle'
        self.action_ = self.action
        self.frame = 0
        self.velocity = [0, 0]
        self.health = info['health']
        self.animations = load_dir('data/images/animations/player_' + self.action)
        self.img = self.animations['player_' + self.action + str(int(self.frame))]
        self.rect = self.img.get_rect()
        self.rect.x = info['pos'][0]
        self.rect.y = info['pos'][1]
        self.anim_speed = 0.15
        self.grounded = True
        self.flip = False
        self.mask = pygame.mask.from_surface(self.img)
        self.protection = False

    @property
    def isdead(self):
        return self.health <= 0

    def animate(self):
        if self.action != self.action_:
            self.animations = load_dir('data/images/animations/player_' + self.action)
            self.action_ = self.action
        if self.flip:
            self.img = pygame.transform.flip(self.animations['player_' + self.action + str(int(self.frame))], True, False)
        else:
            self.img = self.animations['player_' + self.action + str(int(self.frame))]
        self.mask = pygame.mask.from_surface(self.img)
        if self.frame >= len(self.animations) - 1: 
            self.frame = 0
        else: 
            self.frame += self.anim_speed

    def update(self, actions):
        self.animate()
        if self.rect.y >= 120 - self.img.get_height(): 
            self.velocity[1] = 0
            self.grounded = True
        else: 
            self.velocity[1] += 0.1
            self.grounded = False

        if self.rect.x >= display.get_width() - self.img.get_width():
            self.rect.x = display.get_width() - self.img.get_width()
        if self.rect.x <= 0: 
            self.rect.x = 0
        if actions['jump']: 
            self.velocity[1] = -2
            jump_s.play()

        if actions['left']: 
            self.velocity[0] = -1
            self.flip = True
        elif actions['right']: 
            self.velocity[0] = 1
            self.flip = False
        else: self.velocity[0] = 0

        if self.velocity[0] != 0: 
            self.action = 'run'
            self.anim_speed = 0.15
        else: 
            self.action = 'idle'
            self.anim_speed = 0.05

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def render(self, surf):
        outline = [(p[0] + self.rect.x, p[1] + self.rect.y) for p in self.mask.outline()]
        if self.protection:
            pygame.draw.lines(surf, (255, 255, 255), False, outline, 3)
        surf.blit(self.img, (self.rect.x, self.rect.y))
class Level:

    def __init__(self, player):
        self.background_music = load_sound('background_music.mp3')
        self.hearth_img = load_img('data/images/health.png')
        self.player = player
        self.protection = 3
        self.index = 0

    def update(self, dt):
        for meatball in meatballs:
            collision_info = meatball.update(self.player)
            if collision_info[0]:
                if collision_info[1] == 'target' and not self.protection:
                    meatballs.remove(meatball)
                    self.player.protection = True
                    self.protection = 5
                    self.player.health -= 1
                elif self.protection or collision_info[1] == 'ground':
                    meatballs.remove(meatball)

        if self.protection == 0:
            self.player.protection = False
        self.player.update(actions)

        #mängija elud
        for i in range(player.health):
            display.blit(self.hearth_img, (i * 16, 0))

        self.protection = max(0, self.protection - dt)
    
    def render(self, surf):
        for meatball in meatballs:
            meatball.render(surf)
        surf.blit(ground_img, (0, 120))
        self.player.render(surf)


reward_frame = 0
reward_anim = load_dir('data/images/animations/reward')
#animatsiooniga seotud muutujad
#pildid
ground_img = load_img('data/images/ground.png')
autor_img = load_img('data/images/autor.png')

#heli
jump_s = load_sound('jump.wav')

#booleanid
actions = {'right': False, 'left': False, 'jump': False}

finished = info['finished']
started = False
start_intro = False
#muud muutujad

level_duration = 45 
#esimene parameeter näitab mitu palli taevast alla sajab - suvaline arv defineertud vahemikust
#teine parameeter näitab mitu elu saab mängija selle leveli lõppedes juurde
#kolmas parameeter näitab lihapallide langemise kiirust levelis
level_info = {1: [[1, 3], 1, 2], 2: [[2, 5], 2, 2], 3: [[3, 7], 3, 3], 4: [[5, 9], 4, 3], 5: [[7, 10], 0, 4]}

meatballs = []
#ajaga seotud muutujad
start = time.time()
a2 = time.time()
dt = 0

#muud graafikaga seotud muutujad
start_fade = ScreenFade(1, (0, 0, 0), 4)
death_fade = ScreenFade(2, (235, 65, 54), 4)
font = pygame.font.Font('freesansbold.ttf', 15)

restart_button = pygame.Rect(0, 0, font.size('Uuesti alustamiseks')[0], font.size('Uuesti alustamiseks')[1])
restart_button1 = pygame.Rect(48, (display.get_height() // 2) + 16, font.size('vajuta tühikut')[0], font.size('vajuta tühikut')[1])
restart_button.topleft = (25, display.get_height() // 2 - 7)

player = Player(info)
level = Level(player)
level.index = info['level']
screen_shake = 0
level.background_music.play(-1)

while True:

    if not finished and started and not player.isdead:
        display.fill((249, 212, 178))
        
        #timer ja aeg
        timer = time.time()
        a1 = time.time()
        a = int(a1 - a2)
        seconds_left = int(level_duration - (timer - start))
        display.blit(font.render('level: ' + str(level.index), False, (172, 50, 50)), (0, 18))
        display.blit(font.render(str(seconds_left), False, (172, 50, 50)), (0, 34))
        
        level.update(dt)

        #lihapallid
        if a >= 3:
            for i in range(random.randint(level_info[level.index][0][0], level_info[level.index][0][1])):
                meatballs.append(Meatball(
                    [random.randint(0, display.get_width() - 16), -random.randint(16, 64)],
                    level_info[level.index][2]
                ))
            a2 = time.time()
            a1 = time.time()
        
        #kontrollitakse kas level on lõppenud või mitte
        if seconds_left <= 0 and level.index <= 5:
            player.health += level_info[level.index][1]
            level.index += 1
            start = time.time()
        #kontrollitakse kas mängija võitis või mitte
        if level.index > 5 and seconds_left <= 0: 
            finished = True

        level.render(display)
        if start_intro:
            if start_fade.fade(display):
                start_intro =  False
                death_fade.fade_counter = 0

    elif not started:
        display.fill((10, 10, 10))
        display.blit(font.render('Vajuta mängimiseks', False, (255, 255, 255)), (32, display.get_height() // 2))
        display.blit(font.render('suvalist nuppu!', False, (255, 255, 255)), (48, (display.get_height() // 2) + 16))
        display.blit(autor_img, ((display.get_width() // 2) - autor_img.get_width() // 2, display.get_height() - 30))
        if start_intro:
            started = True

    elif player.isdead:
        display.fill((249, 212, 178))
        display.blit(ground_img, (0, 120))
        death_fade.fade(display)
        pygame.draw.rect(display, (1, 1, 1), restart_button)
        pygame.draw.rect(display, (1, 1, 1), restart_button1)
        display.blit(font.render('Uuesti alustamiseks', False, (255, 255, 255)), (25, (display.get_height() // 2 - 6)))
        display.blit(font.render('vajuta tühikut', False, (255, 255, 255)), (48, (display.get_height() // 2) + 16))

    elif finished:
        display.fill((249, 212, 178))
        if not reward_frame + 0.1 >= len(reward_anim):
            reward_frame += 0.1
        if int(reward_frame) <= 10:
            screen_shake = 30
        reward_img = reward_anim['reward' + str(int(reward_frame))]
        display.blit(ground_img, (0, 120))
        display.blit(reward_img, ((display.get_width() // 2) - reward_img.get_width() // 2, (display.get_height() // 2) - reward_img.get_height() // 2 - 20))
        display.blit(font.render('Uuesti mängimiseks', False, (255, 255, 255)), (25, (display.get_height() // 2 + 11)))
        display.blit(font.render('vajuta tühikut', False, (255, 255, 255)), (48, (display.get_height() // 2) + 23))
    else:
        display.fill((0, 0, 10))
    

    actions['jump'] = False
    for event in pygame.event.get():
        if event.type == QUIT:
            save_file = open('save.txt', 'w')
            save_file.write(json.dumps({'pos': [player.rect.x, player.rect.y - 20], 'level':level.index, 'health': player.health, 'finished': finished}))
            save_file.close()
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if started == False:
                start_intro = True
            if event.key in [K_d, K_RIGHT]:
                actions['right'] = True
            if event.key in [K_a, K_LEFT]:
                actions['left'] = True
            if event.key in [K_w, K_SPACE, K_UP] and player.grounded:
                actions['jump'] = True
                if player.isdead:
                    player.health = 3
                    start = time.time()
                    death_fade.fade_counter = 0
                if finished:
                    level.index = 1
                    start = time.time()
                    player.health = 3
                    finished = False
        if event.type == KEYUP:
            if event.key in [K_d, K_RIGHT]:
                actions['right'] = False
            if event.key in [K_a, K_LEFT]:
                actions['left'] = False

    #ekraani väristamine
    if screen_shake > 0:
        screen_shake -= 1

    render_offset = [0, 0]
    if screen_shake:
        render_offset[0] = random.randint(0, 16) - 8
        render_offset[1] = random.randint(0, 16) - 8

    pygame.display.update()
    screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), render_offset)
    dt = clock.tick(60) / 1000
