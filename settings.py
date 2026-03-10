from raylib import *
from pyray import *
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
WINDOW_WIDTH, WINDOW_HEIGHT = 1000,800

# WINDOW_WIDTH = get_monitor_width(0)
# WINDOW_HEIGHT = get_monitor_height(0)
#print("HERE",WINDOW_HEIGHT,WINDOW_WIDTH)
GRAVITY           = 2000

PLAYER_BASE_SIZE  =  20.0
PLAYER_SPEED      =  50
PLAYER_MAX_SHOOTS =  1
PLAYER_COLOR      =  RED
PLAYER_SPEED_MAX  =  15

MAX_BIG_BALLS     =  2
BALLS_SPEED       =  .80
BALL_COLOR        =  RED
BIG_BALL_SIZE     =  50
MED_BALL_SIZE     =  35
SMALL_BALL_SIZE   =  20
BIG_BALL_PTS      =  200
MED_BALL_PTS      =  100
SMALL_BALL_PTS    =  50

SHOOT_SPEED       =  700
SHOOT_THICKNESS   =  3
SHOOT_COLOR       =  DARKGRAY

POINTS_FRAMES     =  100

TRANSPARENT_GRAY  = Color(50,50,50,50)

BULLET_SPEED      =  1000

# class Settings():
#     def __init__(self):
#         WINDOW_WIDTH = get_screen_width()
#         WINDOW_HEIGHT = get_screen_height()