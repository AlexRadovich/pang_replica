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
        draw_circle(int(self.position.x),int(self.position.y),5, RED)
        if self.parent.debug_mode_on:
            draw_circle_v(self.hitbox_center, 9, TRANSPARENT_GREEN)

    def shoot(self):
        if self.active_shots < PLAYER_MAX_SHOOTS:
            self.shots.append(Shoot(self.position,self))
            self.active_shots += 1

    def getpos(self):
        return self.position
    
    def shutdown(self):
        unload_texture(self.sprite)


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
            self.time_held += 1
            if self.time_held % 5 == 0:
                self.bullets.append(Bullet(self, Vector2(self.position.x,self.position.y)))
            
        if not is_key_down(KEY_SPACE):
            self.firing = False

    def draw(self):
        draw_text(f"{len(self.bullets)}" , 20, 200, 20 , GREEN)
        if self.firing:
            if self.time_held % 30 < 10:
                draw_texture_ex(self.flash1,self.spritepos,0,.1,RED)
            elif self.time_held % 30 < 20:
                draw_texture_ex(self.flash2,self.spritepos,0,.1,RED)
            else:
                draw_texture_ex(self.flash3,self.spritepos,0,.1,RED)

            #draw_circle(int(self.position.x), int(self.position.y), 20, BLACK)

    def startup(self):
        self.flash1 = load_texture("assets/F1.png")
        self.flash2 = load_texture("assets/F2.png")
        self.flash3 = load_texture("assets/F3.png")

    def shutdown(self):
        unload_texture(self.flash1)
        unload_texture(self.flash2)
        unload_texture(self.flash3)
        
        
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

        pass

    def update(self):
        dt = get_frame_time()

        curvature = abs(math.cos(self.t))

        speed = self.base_speed * (0.5 + curvature)

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

        # for bullet in self.parent.player.gun.bullets:
        #     if bullet.active and check_collision_circles(self.hitbox_center,BOSS_HITBOX_SIZE , bullet.position, BULLET_SIZE):
        #         bullet.active = False
        #         self.hp -= 1


    def draw(self):
        if self.hit:
            draw_texture_ex(self.base,self.position,180,1.5,RED)
            self.hit = False
        else:
            draw_texture_ex(self.base,self.position,180,1.5,CLEAR)

        draw_text(str(self.hp) , WINDOW_WIDTH//2, 50 ,20, GREEN)
        #draw_circle(int(self.position.x),int(self.position.y),5,RED)
        if self.parent.debug_mode_on:
            draw_circle_v(self.hitbox_center, BOSS_HITBOX_SIZE, TRANSPARENT_GREEN)
        #draw_circle(int(self.x),int(self.y),30,PURPLE)
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
        if check_collision_circles(self.position,BOSS_BULLET_SIZE, self.parent.parent.parent.player.hitbox_center , 9):
            #DO HIT LOGIC
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
            self.speed /= 2
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




        

        # for line in self.parent.player.shots:
        #     if line.active and check_collision_circle_line(self.position,self.radius,line.start,line.top):
        #         line.active = False
        #         self.parent.player.active_shots -= 1

        #         if self.radius >= 19:
        #             self.split()
        #         self.active = False

        #         self.add_points(self.radius)

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

        self.get_screen_dimens()
        self.pointIDS = []
        self.paused = False
        self.gameover = False
        self.victory = False
        self.player = Player(self, Vector2(WINDOW_WIDTH//2,WINDOW_HEIGHT))
        # self.balls = [Ball(self, Vector2(random.randint(0,WINDOW_WIDTH),random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(300,-100))  , 
        #               Ball(self, Vector2(random.randint(0,WINDOW_WIDTH) , random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(-300,-100)) ]
        self.boss = Boss(self)
        

    def get_screen_dimens(self):
        self.WW = get_screen_width()
        self.WH = get_screen_height()
        return[WINDOW_WIDTH,WINDOW_HEIGHT]
    
    def startup(self):
        self.bg = load_texture("assets/bg.png")
        self.player.startup()
        self.boss.startup()


    def update(self):

        if (not self.gameover and not self.victory):

            if is_key_pressed(KEY_P): self.paused = not self.paused
            if is_key_pressed(KEY_T): self.debug_mode_on = not self.debug_mode_on

            if not self.paused:

                self.player.update()
                self.player.gun.update()
                self.boss.update()

                for bullet in self.player.gun.bullets:
                    bullet.update()

                
            

                # for shot in self.player.shots: 
                #     if shot.active: shot.update()


                actives = False
                # for ball in self.balls:
                #     if ball.active: 
                #         ball.update()
                #         actives = True


                #if not actives and not self.gameover:
                # if not self.gameover:
                #     self.victory = True

        if is_key_pressed(KEY_ENTER) and (self.gameover or self.victory):
            self.__init__()
            self.startup()


    def gamewin(self):
        self.victory = True

        
        
    def draw(self):
        draw_texture(self.bg,0,0, PURPLE) #background

        if self.debug_mode_on:
            draw_text(f"FPS: {get_fps()}" , 20,100,20, WHITE) #fps
            
            draw_text(f"window is: {WINDOW_WIDTH} x {WINDOW_HEIGHT}" , 20, 130, 20, WHITE)

        self.player.draw()
        self.player.gun.draw()
        self.boss.draw()
        for bullet in self.player.gun.bullets:
            bullet.draw()
        # for shot in self.player.shots: 
        #     if shot.active: shot.draw()

        # for ball in self.balls:
        #     if ball.active: ball.draw()

        for ID in self.pointIDS:
            if ID[2] > 0:
                draw_text(f"+{str(ID[3])}" , int(ID[0]) , int(ID[1]) , 20, Color(200, 122, 255, int(2.55 * ID[2])) )
                ID[2] -= 1

        draw_text(f"{self.player.points} POINTS" , 10, 10, 30 , PURPLE)

        if self.paused:
            draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, TRANSPARENT_GRAY)
            draw_text("Press [P] to unpause" , WINDOW_WIDTH//3 , WINDOW_HEIGHT//2, 30, BLACK)

        if self.gameover:
            draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, TRANSPARENT_GRAY)
            draw_text("GAME OVER PRESS [ENTER] TO PLAY AGAIN" , WINDOW_WIDTH//5, WINDOW_HEIGHT//2, 30, BLACK)

        if self.victory:
            draw_text("GAME WIN! PRESS [ENTER] TO PLAY AGAIN" , WINDOW_WIDTH//5, WINDOW_HEIGHT//2, 30, BLACK)

    def shutdown(self):
        unload_texture(self.bg)
        self.player.shutdown()
        self.player.gun.shutdown()
        self.boss.shutdown()