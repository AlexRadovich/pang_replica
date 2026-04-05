#from raylib import *
from settings import *
from enums import * 
from pyray import *
from collections import deque
from pathlib import Path
import math
import random

class Player():
    def __init__(self, parent, position, speed = PLAYER_SPEED):
        
        self.points = 0
        self.parent = parent
        self.position = position
        #self.top = Vector2(position.x + 25, position.y- 50)
        self.top = Vector2(position.x - 25, position.y - 80)
        self.right = Vector2(position.x - 12, position.y - 85)
        self.gun_nozzle = Vector2(position.x + 0, position.y - 75)
        self.speed = speed
        #self.shots = []
        self.movement = Vector2(0,0)
        #self.active_shots = 0

        self.gun = Gun(self, self.gun_nozzle, self.right)
        self.hitbox_center = Vector2(position.x-1, position.y-55)

    def startup(self):
        self.sprite = load_texture("assets/ship.png")
        self.gun.startup()



    def update(self):
        move = self.movement.x

        # if is_key_pressed(KEY_SPACE):
        #     self.shoot()
        if is_key_down(KeyboardKey.KEY_RIGHT) and move < PLAYER_SPEED_MAX:
            self.movement.x += .5
        elif is_key_down(KeyboardKey.KEY_LEFT) and move > -PLAYER_SPEED_MAX:
            self.movement.x -= .5
        elif abs(move) <= 1:
            self.movement.x = 0
        elif move != 0:
            self.movement.x -= (move / abs(move))/3



        delta_x = self.position.x

        motion_this_frame = self.movement.x * get_frame_time() * self.speed
        self.position.x += int(motion_this_frame)
        self.position.x = max(0, self.position.x)
        self.position.x = min(self.position.x, WINDOW_WIDTH - 50)

        delta_x = self.position.x - delta_x
        self.top.x += delta_x
        self.right.x += delta_x
        self.gun_nozzle.x += delta_x
        self.hitbox_center.x += delta_x
        

    def draw(self):
        draw_texture_ex(self.sprite,self.top,0,1,WHITE)
        if self.parent.debug_mode_on:
            draw_circle(int(self.position.x),int(self.position.y),5, RED)

            draw_circle_v(self.hitbox_center, PLAYER_HBOX_RADIUS, TRANSPARENT_GREEN)

    def shoot(self):
        if self.active_shots < PLAYER_MAX_SHOOTS:
            self.shots.append(Shoot(self.position,self))
            self.active_shots += 1

    def getpos(self):
        return self.position
    
    def shutdown(self):
        unload_texture(self.sprite)

    def die(self):
        pass


class Bullet():

    def __init__(self, parent, position, active = True , horizontal_offset=0):

        self.active = active
        self.parent = parent
        self.position = position
        self.hoff = random.randint(-BULLET_OFFSET, BULLET_OFFSET)

        #bullet_texture = load_texture()
        pass

    def update(self):
        self.deads = 0
        dt = get_frame_time()
        self.position.y -= BULLET_SPEED * dt
        self.position.x +=  self.hoff * dt

        if self.position.y <= 0:
            self.parent.deads += 1
        if self.active and check_collision_circles(self.parent.parent.parent.boss.hitbox_center , BOSS_HITBOX_SIZE , self.position , BULLET_SIZE ):
            self.parent.parent.parent.boss.hp -= 1 
            self.active = False
            self.parent.parent.parent.boss.hit = True
        

    def draw(self):
        if self.active:
            draw_circle(int(self.position.x), int(self.position.y), BULLET_SIZE, RED)

class Gun():

    def __init__(self, parent, position, spritepos , dead_bullets = 0):
        self.parent = parent
        self.deads = dead_bullets
        self.spritepos = spritepos
        self.dt = get_frame_time()
        self.bullets = deque()
        self.position = position
        self.time_held = 0
        self.firing = False
        
    def update(self):

        for _ in range(self.deads):
            self.bullets.popleft()
        self.deads = 0

        if is_key_down(KEY_SPACE):
            self.firing = True
            self.time_held += get_frame_time()
            if self.time_held >= PLAYER_FIRE_RATE:
                self.time_held = 0
                self.bullets.append(Bullet(self, Vector2(self.position.x,self.position.y)))
                if not is_sound_playing(self.blast):play_sound(self.blast)

            
        if not is_key_down(KEY_SPACE):
            self.firing = False

    def draw(self):
        if self.parent.parent.debug_mode_on:
            draw_text(f"active player bullets: {len(self.bullets)}" , 20, 250, 14 , GREEN)
        if self.firing:
            if self.time_held % 2 < 0:
                draw_texture_ex(self.flash1,self.spritepos,0,.1,RED)
            elif self.time_held % 2 < 2:
                draw_texture_ex(self.flash2,self.spritepos,0,.1,RED)
            else:
                draw_texture_ex(self.flash3,self.spritepos,0,.1,RED)


    def startup(self):
        self.flash1 = load_texture("assets/F1.png")
        self.flash2 = load_texture("assets/F2.png")
        self.flash3 = load_texture("assets/F3.png")
        self.blast  = load_sound("assets/blaster.wav")
        set_sound_volume(self.blast,.4)


    def shutdown(self):
        unload_texture(self.flash1)
        unload_texture(self.flash2)
        unload_texture(self.flash3)
        unload_sound(self.blast)
        
        
class Boss():

    def __init__(self , parent):
        self.parent = parent
        self.position = Vector2(WINDOW_WIDTH//2+97, 300)
        self.hitbox_center = Vector2(self.position.x-97,self.position.y-100)
        self.cx = self.position.x-97
        self.cy = self.position.y-100
        self.hp = BOSS_HP
        self.speed = BOSS_SPEED
        self.ax = AMP_X
        self.ay = AMP_Y
        self.x = self.position.x-97
        self.y = self.position.y-100
        self.t = 0
        self.base_speed = BOSS_SPEED
        self.hit = False
        self.fired_this_cycle = False
        self.attacks = []

        self.frame = 0
        self.frames_passed = BOSS_DEATH_FRAME


        pass

   

    def update(self):

        

        dt = get_frame_time()
        if self.hp <= 0:
            self.frames_passed -= dt
        if self.frames_passed <= 0:
            self.frame += 1
            self.frames_passed = BOSS_DEATH_FRAME
        if self.frame >= 17:
            self.parent.victory = True

        curvature = abs(math.cos(self.t))

        speed = self.base_speed * (0.5 + curvature)

        if self.hp >0:

            self.t += speed * dt
            tempx = self.x
            tempy = self.y
            self.x = self.cx + self.ax * math.sin(self.t)
            self.y = self.cy + self.ay * math.sin(2 * self.t)
            tempx = self.x -tempx
            tempy = self.y -tempy

            self.position.x += tempx
            self.position.y += tempy
            self.hitbox_center.x += tempx
            self.hitbox_center.y += tempy


        for i in self.attacks:
            i.update()

        if self.fired_this_cycle == False and abs(math.sin(self.t)) < 0.02:
            self.attacks.append(Boss_attack1(self,Vector2(self.hitbox_center.x,self.hitbox_center.y+15), 150 , random.randint(-MAX_BOSS_HOFF,-MAX_BOSS_HOFF // 3) , BOSS_ATTACK_SPEED))
            self.attacks.append(Boss_attack1(self,Vector2(self.hitbox_center.x,self.hitbox_center.y+15), 150 , random.randint(-MAX_BOSS_HOFF //3 ,MAX_BOSS_HOFF //3 ) , BOSS_ATTACK_SPEED))
            self.attacks.append(Boss_attack1(self,Vector2(self.hitbox_center.x,self.hitbox_center.y+15), 150 , random.randint(MAX_BOSS_HOFF//3,MAX_BOSS_HOFF) , BOSS_ATTACK_SPEED))
            self.fired_this_cycle = True
            
        elif abs(math.sin(self.t)) >= 0.02:
            self.fired_this_cycle = False
        


    def draw(self):
        if self.hp <= 0:
            draw_texture_pro(self.demo, Rectangle(self.frame * 128, 0, 120, 120), Rectangle(self.position.x, self.position.y, 180, 180), Vector2(0,0), 180, WHITE)

        elif self.hit:
            draw_texture_ex(self.base,self.position,180,1.5,RED)
            self.hit = False
        else:
            draw_texture_ex(self.base,self.position,180,1.5,CLEAR)

            #draw_texture_pro(self.demo , Rectangle(self.frame * 120 , 120), Rectangle(self.position.x,self.position.y, 120, 120) , self.position , 0 , WHITE)


        draw_text(str(self.hp) , WINDOW_WIDTH//2, 50 ,20, GREEN)

        if self.parent.debug_mode_on:
            draw_circle_v(self.hitbox_center, BOSS_HITBOX_SIZE, TRANSPARENT_GREEN)

        
        draw_rectangle(int(WINDOW_WIDTH//4) , 10 , int((WINDOW_WIDTH//2) * (self.hp / BOSS_HP)) , 10 , RED)
        draw_rectangle(int(WINDOW_WIDTH//4) , 17 , int((WINDOW_WIDTH//2) * (self.hp / BOSS_HP)) , 3 , DARKRED)
        for i in self.attacks:
            i.draw()

    def startup(self):
        self.base = load_texture("assets/boss.png")
        self.demo = load_texture("assets/boss_demolition.png")
        self.flash = load_texture("assets/boss_flashing.png")

    def shutdown(self):
        unload_texture(self.base)
        unload_texture(self.demo)
        unload_texture(self.flash)

class Boss_bullet():

    def __init__(self, parent, origin,  theta, radius, position):
        self.parent = parent
        self.origin = origin
        self.theta = theta
        self.radius = radius
        self.position = position

    def update(self):
        self.theta += BOSS_ATTACK_ROTATION * get_frame_time()
        self.position = Vector2(int(self.origin.x + math.cos(self.theta) * self.radius) , int(self.origin.y + math.sin(self.theta) * self.radius))
        if check_collision_circles(self.position,BOSS_BULLET_SIZE, self.parent.parent.parent.player.hitbox_center , PLAYER_HBOX_RADIUS):
            if not self.parent.parent.parent.godmode:
                self.parent.parent.parent.gameover = True
            pass
    def draw(self):

        draw_circle_v(self.position, BOSS_BULLET_SIZE , YELLOW)



class Boss_bullet_type2():

    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass



class Boss_attack1():

    def __init__(self, parent, center, radius, hoff, speed):
        self.parent = parent
        self.position = center
        self.radius = radius
        self.hoff   = hoff
        self.speed  = speed
        self.bullets = []
        self.theta = ((math.pi * 2) / BOSS_ATTACK1_BULLETS)
        self.attack_rotation = 0
        self.tophalf = True
        for i in range(BOSS_ATTACK1_BULLETS):
            self.bullets.append(Boss_bullet(self, center , self.theta * i, self.radius , Vector2(int(self.position.x + math.cos(self.theta * i) * self.radius) , int(self.position.y + math.sin(self.theta * i) * self.radius))))

    def update(self):
        dt = get_frame_time()
        self.position.y -= self.speed * dt
        self.position.x +=  self.hoff * dt

        if self.tophalf and self.position.y >= WINDOW_HEIGHT //2:
            self.speed *= (3/5)
            self.hoff /=3
            self.tophalf = False

        for bullet in self.bullets:
            bullet.update()

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()
            
    

class Boss_attack2():
    
    def __init__(self, parent):
        self.parent = parent

class Shoot():

    def __init__(self, position, player):
        self.parent = player
        self.start = Vector2(position.x+25, WINDOW_HEIGHT)
        self.top   = Vector2(position.x+25, WINDOW_HEIGHT)
        self.active = True

    def update(self):
        self.top.y -= SHOOT_SPEED * get_frame_time()
        if self.top.y <= 0:
            self.active = False
            self.parent.active_shots -= 1


    def draw(self):
        DrawLineEx(self.start,self.top,SHOOT_THICKNESS,SHOOT_COLOR)

    
class Ball():

    def __init__(self, parent,  position, active,size, motion):
        self.active = active
        self.parent = parent
        self.position = position
        self.radius = size
        self.motion = motion
        self.speed = BALLS_SPEED

    def update(self):
        dt = get_frame_time()
        self.motion.y += GRAVITY * dt
        
        motion_this_frame = vector2_scale(self.motion, dt * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)

        if self.position.y + self.radius >= WINDOW_HEIGHT:
            self.position.y = WINDOW_HEIGHT - self.radius
            self.motion.y *= -.95

        if self.position.x + self.radius >= WINDOW_WIDTH:
            self.position.x = WINDOW_WIDTH - self.radius
            self.motion.x *= -1

        if self.position.x - self.radius <= 0:
            self.position.x = self.radius
            self.motion.x *= -1


        top = self.parent.player.gun_nozzle
        pos = self.parent.player.position
        right = self.parent.player.right
        
        if check_collision_circle_line(self.position,self.radius,top,pos) or check_collision_circle_line(self.position,self.radius,top,right):
            self.parent.gameover = True

    def add_points(self,size):

        pts = 0
        if size == 50:
            pts = BIG_BALL_PTS

        elif size == 31:
            pts = MED_BALL_PTS

        elif size == 12:
            pts = SMALL_BALL_PTS
        
        self.parent.player.points += pts
        self.parent.pointIDS.append([self.position.x , self.position.y , POINTS_FRAMES , pts])


    
    def split(self):
        self.parent.balls.append(Ball(self.parent,self.position, True, self.radius-19, Vector2(300,-500)))
        self.parent.balls.append(Ball(self.parent,self.position, True, self.radius-19, Vector2(-300,-500)))



    def draw(self):
        draw_circle_v(self.position,self.radius,BALL_COLOR)



class Game():

    def __init__(self):

        self.debug_mode_on = False
        self.screen = Screens.MENU
        self.get_screen_dimens()
        self.pointIDS = []
        self.paused = False
        self.gameover = False
        self.victory = False
        self.player = Player(self, Vector2(WINDOW_WIDTH//2,WINDOW_HEIGHT))
        self.boss = Boss(self)
        self.godmode = False

        self.menuselect = 0
        

    def get_screen_dimens(self):
        self.WW = get_screen_width()
        self.WH = get_screen_height()
        return[WINDOW_WIDTH,WINDOW_HEIGHT]
    
    def startup(self):
        init_audio_device()
        self.bg = load_texture("assets/bg.png")
        self.player.startup()
        self.boss.startup()
        self.menu_music = load_music_stream("assets/menu.wav")
        self.fight_music = load_music_stream("assets/battle.wav")
        self.titlefont = load_font_ex("assets/titlefont.ttf", 80, None, 95)
        self.selectfont = load_font_ex("assets/selectfont.otf", 50, None, 95)
        play_music_stream(self.fight_music)
        play_music_stream(self.menu_music)


    def update(self):

        if self.screen == Screens.MENU:
            update_music_stream(self.menu_music)

            if is_key_pressed(KEY_DOWN):
                self.menuselect += 1
            elif is_key_pressed(KEY_UP):
                self.menuselect -= 1

            if is_key_pressed(KEY_ENTER) and self.menuselect % 2 == 0:
                self.screen = Screens.GAME
            elif is_key_pressed(KEY_ENTER):
                self.screen = Screens.TUTORIAL


        elif self.screen == Screens.TUTORIAL:
            update_music_stream(self.menu_music)
            if is_key_pressed(KEY_ENTER):
                self.screen = Screens.GAME


        elif self.screen == Screens.GAME:


            if (not self.gameover and not self.victory):


                if is_key_pressed(KEY_P): self.paused = not self.paused
                if is_key_pressed(KEY_T): self.debug_mode_on = not self.debug_mode_on
                if self.debug_mode_on:
                    if is_key_pressed(KEY_G): self.godmode = not self.godmode
                    if is_key_pressed(KEY_BACKSLASH): self.boss.hp = 0
                    if is_key_pressed(KEY_L): 
                        self.__init__()
                        self.startup()


                if not self.paused:
                    update_music_stream(self.fight_music)

                    self.player.update()
                    self.player.gun.update()
                    self.boss.update()

                    for bullet in self.player.gun.bullets:
                        bullet.update()

            if is_key_pressed(KEY_ENTER) and (self.gameover or self.victory):
                self.__init__()
                self.startup()


    def gamewin(self):
        self.victory = True

        
        
    def draw(self):

        if self.screen == Screens.MENU:
            draw_texture(self.bg,0,0, WHITE) #background
            draw_texture_ex(self.player.sprite, Vector2(WINDOW_WIDTH//2-140, 2*WINDOW_HEIGHT//3), 00, 6, WHITE)
            draw_text_pro(self.titlefont, "SPACE" , Vector2(WINDOW_WIDTH//2 + 150, 110) , Vector2(WINDOW_WIDTH//3,30) ,  0  , 80 , 3, PURPLE)
            draw_text_pro(self.titlefont, "BOSSFIGHT" , Vector2(WINDOW_WIDTH//2 + 50, 180) , Vector2(WINDOW_WIDTH//3,30) ,  0  , 80 , 3, PURPLE)
            draw_rectangle_rounded(Rectangle(WINDOW_WIDTH//2-150, 350, 300, 70) , .3 , 4 , JUPITER_ORANGE)
            draw_rectangle_rounded(Rectangle(WINDOW_WIDTH//2-150, 440, 300, 70) , .3 , 4 , JUPITER_ORANGE)  
            draw_text_pro(self.selectfont, "PLAY" , Vector2(WINDOW_WIDTH//2-98 , 365) , Vector2(0,0), 0 , 45 , 8 , WHITE)
            draw_text_pro(self.selectfont, "TUTORIAL" , Vector2(WINDOW_WIDTH//2-136 , 459) , Vector2(0,0), 0 , 35 , 4 , WHITE)
            if self.menuselect%2 == 0:
                draw_rectangle_lines_ex(Rectangle(WINDOW_WIDTH//2-155, 345, 310, 80) , 3 , WHITE)
            else:
                draw_rectangle_lines_ex(Rectangle(WINDOW_WIDTH//2-155, 435, 310, 80) , 3 , WHITE)



        elif self.screen == Screens.TUTORIAL:
            draw_texture(self.bg,0,0, PURPLE) #background
            draw_texture_ex(self.player.sprite, Vector2(WINDOW_WIDTH//2-80, 2*WINDOW_HEIGHT//3 - 10), 00, 4, WHITE)
            draw_texture_ex(self.boss.base,Vector2(self.boss.position.x+70,self.boss.position.y+40),180,2.5,CLEAR)
            draw_text("THE ENEMY -->" , 150,100,30,RED)
            draw_text("DODGE ITS ATTACKS!" , 65,150,30,RED)
            draw_text("THE PLAYER (YOU).  ------->" , 80,WINDOW_HEIGHT - 200,25,RED)
            draw_text("PRESS [SPACE] TO SHOOT" , 80,WINDOW_HEIGHT - 150,25,RED)
            draw_text("USE ARROW KEYS [< and >] TO MOVE" , 80,WINDOW_HEIGHT - 100,25,RED)





        elif self.screen == Screens.GAME:
            draw_texture(self.bg,0,0, PURPLE) #background

            if self.debug_mode_on:
                draw_text(f"FPS: {get_fps()}" , 20,100,20, WHITE) #fps
                
                if self.godmode:
                    draw_text("Godmode [G]" , 20, 160, 20, GREEN)
                else:
                    draw_text("Godmode [G]" , 20, 160, 20, RED)
                draw_text("Instant Win [\]" , 20, 190, 20, RED)
                draw_text("Instant Restart [L]" , 20, 220, 20, RED)
                draw_text(f"window is: {WINDOW_WIDTH} x {WINDOW_HEIGHT}" , 20, 130, 20, WHITE)

            self.player.draw()
            self.player.gun.draw()
            self.boss.draw()
            for bullet in self.player.gun.bullets:
                bullet.draw()



            if self.paused:
                draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, TRANSPARENT_GRAY)
                draw_text("Press [P] to unpause" , WINDOW_WIDTH//3 , WINDOW_HEIGHT//2, 30, RED)

            if self.gameover:
                draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, TRANSPARENT_GRAY)
                draw_text("GAME OVER! PRESS [ENTER] TO PLAY AGAIN" , WINDOW_WIDTH//5, WINDOW_HEIGHT//2, 30, RED)

            if self.victory:
                draw_text("GAME WIN! PRESS [ENTER] TO PLAY AGAIN" , WINDOW_WIDTH//5, WINDOW_HEIGHT//2, 30, RED)

    def shutdown(self):
        unload_music_stream(self.menu_music)
        unload_music_stream(self.fight_music)
        unload_texture(self.bg)
        close_audio_device()
        self.player.shutdown()
        self.player.gun.shutdown()
        self.boss.shutdown()