from raylib import *
from settings import *
from pyray import *
from collections import deque
from pathlib import Path
import random

class Player():
    def __init__(self, position, speed = PLAYER_SPEED):
        
        self.points = 0
        self.position = position
        #self.top = Vector2(position.x + 25, position.y- 50)
        self.top = Vector2(position.x - 25, position.y - 80)
        self.right = Vector2(position.x - 0, position.y - 95)
        self.gun_nozzle = Vector2(position.x + 24, position.y - 65)
        self.speed = speed
        self.shots = []
        self.movement = Vector2(0,0)
        self.active_shots = 0

        self.gun = Gun(self.gun_nozzle, self.right)

    def startup(self):
        self.sprite = load_texture("assets/ship.png")
        self.gun.startup()


    def update(self):
        move = self.movement.x

        if is_key_pressed(KEY_SPACE):
            self.shoot()
        if is_key_down(KeyboardKey.KEY_RIGHT) and move < PLAYER_SPEED_MAX:
            self.movement.x += .5
        elif is_key_down(KeyboardKey.KEY_LEFT) and move > -PLAYER_SPEED_MAX:
            self.movement.x -= .5
        elif move != 0:
            self.movement.x -= (move / abs(move))/3



        delta_x = self.position.x

        motion_this_frame = vector2_scale(self.movement, get_frame_time() * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)
        self.position.x = max(0, self.position.x)
        self.position.x = min(self.position.x, WINDOW_WIDTH - 50)

        delta_x = self.position.x - delta_x
        self.top.x += delta_x
        self.right.x += delta_x
        self.gun_nozzle.x += delta_x
        

    def draw(self):
        draw_texture_ex(self.sprite,self.top,0,2,WHITE)
        #draw_triangle(self.top,self.position,self.right,PLAYER_COLOR)

    def shoot(self):
        if self.active_shots < PLAYER_MAX_SHOOTS:
            self.shots.append(Shoot(self.position,self))
            self.active_shots += 1

    def getpos(self):
        return self.position
    
    def shutdown(self):
        unload_texture(self.sprite)


class Bullet():

    def __init__(self,position, horizontal_offset=0):
        self.position = position
        self.hoff = horizontal_offset

        #bullet_texture = load_texture()
        pass

    def update(self):
        dt = get_frame_time()
        self.position.y -= BULLET_SPEED * dt
        self.position.x +=  self.hoff * dt

    def draw(self):
        draw_circle(int(self.position.x), int(self.position.y), 10, RED)

class Gun():

    def __init__(self,position, spritepos):
        self.spritepos = spritepos
        self.dt = get_frame_time()
        self.bullets = deque()
        self.position = position
        self.time_held = 0
        
        pass
    def update(self):
        if is_key_down(KEY_TWO):
            self.firing = True
            self.time_held += 1
            if self.time_held % 5 == 0:
                self.bullets.append(Bullet(Vector2(self.position.x,self.position.y)))
            
            #replace with muzzle flash sprite
        if not is_key_down(KEY_TWO):
            self.firing = False

    def draw(self):
        if is_key_down(KEY_TWO) and self.firing:
            if self.time_held % 30 < 10:
                draw_texture_ex(self.flash1,self.spritepos,0,.2,RED)
            elif self.time_held % 30 < 20:
                draw_texture_ex(self.flash2,self.spritepos,0,.2,RED)
            else:
                draw_texture_ex(self.flash3,self.spritepos,0,.2,RED)

            #draw_circle(int(self.position.x), int(self.position.y), 20, BLACK)

    def startup(self):
        self.flash1 = load_texture("assets/F1.png")
        self.flash2 = load_texture("assets/F2.png")
        self.flash3 = load_texture("assets/F3.png")

    def shutdown(self):
        unload_texture(self.flash1)
        unload_texture(self.flash2)
        unload_texture(self.flash3)
        
        


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




        

        for line in self.parent.player.shots:
            if line.active and check_collision_circle_line(self.position,self.radius,line.start,line.top):
                line.active = False
                self.parent.player.active_shots -= 1

                if self.radius >= 19:
                    self.split()
                self.active = False

                self.add_points(self.radius)

        top = self.parent.player.top
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





    
class Score():
    pass
class Game():

    def __init__(self):

        self.get_screen_dimens()
        self.pointIDS = []
        self.paused = False
        self.gameover = False
        self.victory = False
        self.player = Player(Vector2(WINDOW_WIDTH//2,WINDOW_HEIGHT))
        self.balls = [Ball(self, Vector2(random.randint(0,WINDOW_WIDTH),random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(300,-100))  , 
                      Ball(self, Vector2(random.randint(0,WINDOW_WIDTH) , random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(-300,-100)) ]
        

    def get_screen_dimens(self):
        self.WW = get_screen_width()
        self.WH = get_screen_height()
        return[WINDOW_WIDTH,WINDOW_HEIGHT]
    
    def startup(self):
        self.bg = load_texture("assets/bg.png")
        self.player.startup()


    def update(self):

        if (not self.gameover and not self.victory):
            if IsKeyPressed(KEY_P):
                self.paused = not self.paused

            if not self.paused:

                self.player.update()
                self.player.gun.update()
                for bullet in self.player.gun.bullets:
                    bullet.update()
            

                for shot in self.player.shots: 
                    if shot.active: shot.update()


                actives = False
                for ball in self.balls:
                    if ball.active: 
                        ball.update()
                        actives = True
                if not actives and not self.gameover:
                    self.victory = True

        if is_key_pressed(KEY_ENTER) and (self.gameover or self.victory):
            self.__init__()
            self.startup()


    def gamewin(self):
        self.victory = True

        
        
    def draw(self):
        draw_texture(self.bg,0,0, PURPLE)
        draw_text(f"{WINDOW_WIDTH}, {WINDOW_HEIGHT}" , 100, 200, 30, WHITE)
        self.player.draw()
        self.player.gun.draw()
        for bullet in self.player.gun.bullets:
            bullet.draw()
        for shot in self.player.shots: 
            if shot.active: shot.draw()
        for ball in self.balls:
            if ball.active: ball.draw()
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