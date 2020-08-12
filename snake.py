#!/usr/bin/env python3

from random import randrange
from argparse import ArgumentParser
import curses

class Snake:
    
    def __init__(self, headpos_x, headpos_y):
        self.body = []
        self.body.append([headpos_x, headpos_y])
        self.body.append([headpos_x - 1, headpos_y])
        self.body.append([headpos_x - 2, headpos_y])
        self.speed = [1, 0]
        self.grow = False
    
    # Update the snake and redraw it
    def update(self, game, toroidal):
        head = self.body[0]
        last = head.copy()
        
        # Update head position
        head[0] += self.speed[0]
        head[1] += self.speed[1]
        
        # Check bounds
        if not (0 <= head[0] < game.wwidth) or not (0 <= head[1] < game.wheight):
            if not toroidal:
                game.over("Snake went out of bounds")
                return
            head[0] %= game.wwidth
            head[1] %= game.wheight
        
        if self.grow:
            self.body.insert(1, last)
            self.grow = False
        else:
            # Update the rest of the snake
            for i, part in enumerate(self.body):
                if i > 0:
                    temp = part.copy()
                    self.body[i] = last
                    last = temp
                    
                    # Delete the character
                    game.screen.addch(last[1], last[0], ' ') # delch() does not work
                    
        # Check auto-collision
        for i, part in enumerate(self.body):
            if i > 0 and i < len(self.body) - 1:
                if self.body[0] == part:
                    game.over("Auto-collision")
                    return

        # Draw the snake
        game.screen.addch(head[1], head[0], '@') # head
        for i, part in enumerate(self.body): # rest of the body
            if i > 0 and i < len(self.body) - 1:
                prev = self.body[i-1]

                # Straight segments
                if i == len(self.body) - 1 or self.body[i+1][0] == prev[0] or self.body[i+1][1] == prev[1]:
                    if prev[0] == part[0]:
                        c = curses.ACS_VLINE
                    else:
                        c = curses.ACS_HLINE
                
                # Corners
                else:
                    nxt = self.body[i+1]

                    ul = [[part[0], part[1]+1], [part[0]+1, part[1]]]
                    ll = [[part[0], part[1]-1], [part[0]+1, part[1]]]
                    lr = [[part[0], part[1]-1], [part[0]-1, part[1]]]
                    ur = [[part[0], part[1]+1], [part[0]-1, part[1]]]

                    if prev in ul and nxt in ul:
                        c = curses.ACS_ULCORNER
                    elif prev in ll and nxt in ll:
                        c = curses.ACS_LLCORNER
                    elif prev in lr and nxt in lr:
                        c = curses.ACS_LRCORNER
                    elif prev in ur and nxt in ur:
                        c = curses.ACS_URCORNER
                
                game.screen.addch(part[1], part[0], c)        

class Game:

    def __init__(self, stdscr, args):
        self.screen = stdscr
        self.wheight, self.wwidth = stdscr.getmaxyx()
        self.snake = Snake(self.wwidth // 2, self.wheight // 2)
        self.quit = False
        self.paused = False
        self.makepie()
        self.toroidal = args.toroidal
    
    def over(self, reason):
        self.quit = True
        self.reason = reason
    
    def makepie(self):
        again = True
        while again:
            self.pie = [randrange(self.wwidth), randrange(self.wheight)]
            again = False
            for part in self.snake.body:
                if self.pie == part:
                    again = True
    
    def run(self):
        # Game loop
        while not self.quit:
            
            # Handle input
            c = self.screen.getch()
            if (c == curses.KEY_RIGHT or c == ord('d')) and self.snake.speed != [-1, 0]:
                self.snake.speed = [1, 0]
            elif (c == curses.KEY_LEFT or c == ord('a')) and self.snake.speed != [1, 0]:
                self.snake.speed = [-1, 0]
            elif (c == curses.KEY_UP or c == ord('w')) and self.snake.speed != [0, 1]:
                self.snake.speed = [0, -1]
            elif (c == curses.KEY_DOWN or c == ord('s')) and self.snake.speed != [0, -1]:
                self.snake.speed = [0, 1]
            elif c == ord('q'):
                return "Player quit game"
            elif c == ord('p'):
                prompt = "GAME PAUSED. PRESS p TO RESUME"
                if self.paused:
                    self.screen.addstr(self.wheight - 1, (self.wwidth - len(prompt)) // 2, " " * len(prompt))
                    self.paused = False
                else:
                    self.screen.addstr(self.wheight - 1, (self.wwidth - len(prompt)) // 2, prompt)
                    self.screen.refresh()
                    self.paused = True
            
            if not self.paused:
                self.snake.update(self, self.toroidal)
                
                # Check if player wins
                if len(self.snake.body) == self.wwidth * self.wheight:
                    return "CONGRATULATIONS! Player wins!"
            
                # Check if snake ate pie
                if self.snake.body[0] == self.pie:
                    self.snake.grow = True
                    self.makepie()
            
                # Draw pie
                self.screen.addch(self.pie[1], self.pie[0], curses.ACS_PI)
                
                self.screen.refresh()
                
            curses.napms(100)
        
        return self.reason


def main(stdscr, args):
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    g = Game(stdscr, args)
    return g.run()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="A small curses implementation of the game Snake. Press " +
            "P to pause and Q/ESC to quit. To move the snake use the arrow keys " +
            "or WASD.")
    parser.add_argument("--toroidal", "-t", action="store_true", help=
                        "Activate toroidal space")
    args = parser.parse_args()

    try:
        result = curses.wrapper(main, args)
        print("\nGAME OVER: " + result + "\n")
    except KeyboardInterrupt:
        print("\nPROGRAM INTERRUPTED\n")
