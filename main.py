from pygame.locals import *
import pygame as pm
import asyncio
import random
import os

pm.init()
screen_info = pm.display.Info()
screenwidth,screenheight = (screen_info.current_w,screen_info.current_h)
SCREEN = pm.display.set_mode((screenwidth,screenheight))
CLOCK = pm.time.Clock()
background_image = pm.transform.scale(pm.image.load('Assets/lava_floor.png').convert_alpha(),(screenwidth,screenheight))
intro_image = pm.transform.scale(pm.image.load('Assets/bumpy_land.png').convert_alpha(),(screenwidth,screenheight))
class Rock:
    def __init__(self,image,safe,pos,size):
        self.image = image
        self.safe = safe
        self.pos = pos
        self.size = size
        self.broken = None
        self.sprite = pm.transform.scale(pm.image.load(f'{self.image}').convert_alpha(),(size))
    def show(self):
        SCREEN.blit(self.sprite,(self.pos))
    def selected(self,mouse_pos,player = None,clicked = False):
        if mouse_pos[0] > self.pos[0] and mouse_pos[0] < self.pos[0] + self.size[0] and mouse_pos[1] > self.pos[1] and mouse_pos[1] < self.pos[1] + self.size[1] and clicked:
            if player:
                player.pos = [self.pos[0] + self.size[0]/2 - player.size[0]/2,self.pos[1] + self.size[1]/2 - player.size[1]/2]
            if not self.safe:
                self.broken = True
            else:
                self.broken = False
class Player:
    def __init__(self,image,pos = [0,0],size = None):
        self._pos = pos
        self.pos = pos
        self.prev_pos = pos
        self.image = image
        self.sprite = pm.image.load(f'{self.image}').convert_alpha()
        self.life_count = None
        if not size:
            self.size = self.sprite.get_size()
        else:
            self.size = size
        self.sprite = pm.transform.scale(self.sprite,self.size)
        pass
    def life_display(life_count,life_image,life_initial_pos= [0,0],life_size = None,gap = [0,0]):
        self.life_count = life_count
        self.life_image = life_image
        self.life_initial_pos = life_initial_pos
        self.life_size = life_size
        self.life_objects = []
        for i in range(self.life_count):
            position = [i * (self.life_initial_pos[0] + gap[0]),i * (self.life_initial_pos[1] + gap[1])]
            image = pm.image.load(self.life_image).convert_alpha()
            if not self.life_size:
                self.life_size = image.get_size()
            image = pm.transform.scale(image,(self.life_size))
            life_object = {'image' : image,'position' : position}
            self.life_objects.append(life_object)
    def show(self):
        SCREEN.blit(self.sprite,self.pos)
        if self.life_count:
            for i in self.life_objects:
                SCREEN.blit(i['image'],i['position'])
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        if self._pos != value:
            self.prev_pos = self._pos
            self._pos = value
def rocks(folder,rock_matrix,starting_pos,size,bias = [0,0]):
    images = os.listdir(folder)
    vertical_rocks, horizontal_rocks = rock_matrix
    rock_list = []
    for i in range(vertical_rocks):
        safe_index = random.randint(0,horizontal_rocks - 1)
        rock_list.append([])
        for j in range(horizontal_rocks):
            image = random.choice(images)
            if j != safe_index:
                safe = False
            else:
                safe = True
            rock_pos = [starting_pos[0] + (size[0] + bias[0]) * j, starting_pos[1] + (size[1] + bias[1]) * i]
            rock = Rock(f'{folder}/{image}',safe,rock_pos,size)
            rock.bias = bias
            rock_list[i].append(rock)
    return rock_list
def animate(object,rate,folder,loops = 1):
    try:
        if object.animation_loop != loops:
            object.rate += 1
        else:
            object.frame_count = -1
    except AttributeError:
        object.animation_loop = 0
        object.rate = 0
        object.image_list = os.listdir(folder)
        object.frames = list(map(lambda x : pm.transform.scale(pm.image.load(f'{folder}/{x}').convert_alpha(),object.size),object.image_list))
        object.frame_count = 0
    if object.rate == rate:
        object.rate = 0
        if object.frame_count == len(object.frames) - 1:
            object.frame_count = 0
            object.animation_loop += 1
        else:
            object.frame_count += 1
    SCREEN.blit(object.frames[object.frame_count],object.pos)
async def main():
    rock_rows = 7
    intro_pos = (0,0)
    pos = (0,intro_pos[1] + intro_image.get_height() - 125)
    rock_size = [screenheight/rock_rows,screenheight/(rock_rows + 2)]
    start_rock = Rock('Assets/rocks/l1.png',True,[screenwidth/2 - rock_size[0]/2,intro_image.get_height() - 150 + screenheight - rock_size[1]],rock_size)
    end_rock = Rock('Assets/rocks/l4.png',True,[screenwidth/2 - rock_size[0]/2,intro_pos[1] + intro_image.get_height() - 25],rock_size)
    all_rocks = rocks('Assets/rocks',[rock_rows - 2,3],[screenwidth/2 - rock_size[0] - rock_size[0]/2,end_rock.pos[1] + end_rock.size[1]],rock_size)
    start_rock.pos[1] = all_rocks[-1][-1].pos[1] + all_rocks[-1][-1].size[1] + all_rocks[-1][-1].bias[1]
    player = Player('Assets/player.png',(0,0))
    player.pos = [start_rock.pos[0] + start_rock.size[0]/2 - player.size[0]/2,start_rock.pos[1] + start_rock.size[1]/2 - player.size[1]/2]
    player.life_display(3,'Assets/Heart.png')
    scroll = 0
    clicked = False
    current_rock_row = 4
    show_player = True
    while True:
        intro_pos = (intro_pos[0],intro_pos[1] + scroll)
        pos = (pos[0],pos[1] + scroll)
        SCREEN.fill((0,0,0))
        SCREEN.blit(background_image,(pos))
        SCREEN.blit(intro_image,(intro_pos))
        end_rock.pos[1] += scroll
        player.pos[1] += scroll
        mouse_pos = pm.mouse.get_pos()
        if current_rock_row == -1:
            end_rock.selected(mouse_pos,player = player,clicked=clicked)
            print('Yrue')
        for index,rows in enumerate(all_rocks):
            for rock in rows:
                rock.pos[1] += scroll
                if all_rocks[current_rock_row] == rows:
                    rock.selected(mouse_pos,player = player,clicked  = clicked)
                if rock.broken == True:
                    if rock.frame_count != -1:
                        show_player = False
                        animate(rock,5,'Assets/rock_break')
                    else:
                        all_rocks[index].remove(rock)
                else:
                    if rock.broken == False and current_rock_row > -1 and all_rocks[current_rock_row] == rows:
                        current_rock_row -= 1
                        print(current_rock_row)
                    rock.frame_count = 0
                    rock.show()
        clicked = False    
        start_rock.pos[1] += scroll
        start_rock.show()
        end_rock.show()
        
        scroll = 0
        for event in pm.event.get():
            if event.type == QUIT:
                pm.quit()
            if event.type == MOUSEWHEEL:
                clicked = False
                if event.y == 1:
                    if intro_pos[1] >= 0 :
                        scroll = -intro_pos[1]
                    else:
                        scroll = 50
                else:
                    if pos[1] <= 0:
                        scroll = -pos[1]
                    else:
                        scroll = -50
            elif event.type == MOUSEBUTTONDOWN:
                clicked = True
        if show_player:
            player.frame_count = 0
            player.show()
        else:
            animate(player,30,'Assets/burning')
            clicked = False
            if player.frame_count == -1:
                player.animation_loop = 0
                show_player = True
                player.pos = player.prev_pos
        CLOCK.tick(60)
        pm.display.update()
        await asyncio.sleep(0)
asyncio.run(main())