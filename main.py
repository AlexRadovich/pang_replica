from raylib import *
from settings import *
from pyray import *
from pang import *

current_game = Game()

if __name__ == '__main__':  

  init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pang")
  set_target_fps(120)

  current_game.startup()

  while not window_should_close():

    current_game.update()
      
    begin_drawing()
    clear_background(WHITE)

    current_game.draw()

    end_drawing()

close_window()
  
current_game.shutdown()