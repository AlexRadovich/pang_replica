from raylib import *
from settings import *
from pyray import *
import random

class Player():
    def __init__(self, position, speed = PLAYER_SPEED):
        self.points = 0
        self.position = position
        self.top = Vector2(position.x + 25, position.y- 50)
        self.right = Vector2(position.x + 50, position.y)
        self.speed = speed
        self.shots = []
        self.active_shots = 0

    def update(self):
        motion = Vector2(0, 0)

        if is_key_pressed(KEY_SPACE):
            self.shoot()
        if is_key_down(KeyboardKey.KEY_RIGHT):
            motion.x += 1
        if is_key_down(KeyboardKey.KEY_LEFT):
            motion.x -= 1

        delta_x = self.position.x

        motion_this_frame = vector2_scale(motion, get_frame_time() * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)
        self.position.x = max(0, self.position.x)
        self.position.x = min(self.position.x, WINDOW_WIDTH - 50)

        delta_x = self.position.x - delta_x
        self.top.x += delta_x
        self.right.x += delta_x
        

    def draw(self):
        draw_triangle(self.top,self.position,self.right,PLAYER_COLOR)

    def shoot(self):
        if self.active_shots < PLAYER_MAX_SHOOTS:
            self.shots.append(Shoot(self.position,self))
            self.active_shots += 1

    def getpos(self):
        return self.position




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
        self.pointIDS = []
        self.paused = False
        self.gameover = False
        self.victory = False
        self.player = Player(Vector2(WINDOW_WIDTH//2,WINDOW_HEIGHT))
        self.balls = [Ball(self, Vector2(random.randint(0,WINDOW_WIDTH),random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(300,-100))  , 
                      Ball(self, Vector2(random.randint(0,WINDOW_WIDTH) , random.randint(0,WINDOW_HEIGHT//4)) , True, BIG_BALL_SIZE , Vector2(-300,-100)) ]
        

    def startup(self):
        pass


    def update(self):

        if (not self.gameover and not self.victory):
            if IsKeyPressed(KEY_P):
                self.paused = not self.paused

            if not self.paused:

                self.player.update()

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


    def gamewin(self):
        self.victory = True

        
        
    def draw(self):
        self.player.draw()
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
