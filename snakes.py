#!/usr/bin/env python

# A multiplayer version of snake.py

import curses
from random import randrange
from argparse import ArgumentParser


class Snake:
    # Note: the last segment of a snake's body is invisible and invulnerable to collisions
    # (it's required for rendering)

    def __init__(self, body, headchar, speed):
        self.body = body
        self.speed = speed
        self.headchar = headchar
        self.grow = False
    
    # Update the snake and redraw it
    def update(self, game):
        # Get the other snake
        other = game.bsnake if self is game.asnake else game.asnake

        head = self.body[0]
        last = head.copy()
        
        # Update head position
        head[0] += self.speed[0]
        head[1] += self.speed[1]
        
        # Check bounds
        if not (0 <= head[0] < game.wwidth) or not (0 <= head[1] < game.wheight):
            if not game.toroidal:
                game.over(f"Snake {self.headchar} went out of bounds >> {other.headchar} WINS!")
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
                    try:
                        game.screen.addch(last[1], last[0], ' ') # delch() does not work
                    except:
                        pass # sometimes it throws an exception for no reason

        # Check auto-collision
        if self.body[0] in self.body[1:-1]:
            game.over(f"Snake {self.headchar} bumped on itself >> {other.headchar} WINS!")
            return

        # Draw the snake
        game.screen.addch(head[1], head[0], self.headchar) # head
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

    def collides_with(self, other):
        return self.body[0] in other.body[1:-1]
    
    def contains(self, point):
        return point in self.body[:-1]


class Game:

    def __init__(self, stdscr, args):
        self.screen = stdscr
        self.wheight, self.wwidth = stdscr.getmaxyx()

        abody = [ [i, 0] for i in (2, 1, 0) ]
        bbody = [ [self.wwidth - i, self.wheight - 1] for i in (3, 2, 1) ]

        self.asnake = Snake(abody, 'A', [1, 0])
        self.bsnake = Snake(bbody, 'B', [-1, 0])

        self.quit = False
        self.paused = False
        self.toroidal = args.toroidal
        self.makepie()

    def over(self, reason):
        self.quit = True
        self.reason = reason

    def makepie(self):
        again = True
        while again:
            self.pie = [randrange(self.wwidth), randrange(self.wheight)]
            again = self.asnake.contains(self.pie) or self.bsnake.contains(self.pie)

    def run(self):
        # Game loop
        while not self.quit:
            
            # Handle input
            c = self.screen.getch()

            a = self.asnake
            b = self.bsnake

            # Snake A control
            if c == curses.KEY_RIGHT and a.speed != [-1, 0]:
                a.speed = [1, 0]
            elif c == curses.KEY_LEFT and a.speed != [1, 0]:
                a.speed = [-1, 0]
            elif c == curses.KEY_UP and a.speed != [0, 1]:
                a.speed = [0, -1]
            elif c == curses.KEY_DOWN and a.speed != [0, -1]:
                a.speed = [0, 1]

            # Snake B control
            elif c == ord('d') and b.speed != [-1, 0]:
                b.speed = [1, 0]
            elif c == ord('a') and b.speed != [1, 0]:
                b.speed = [-1, 0]
            elif c == ord('w') and b.speed != [0, 1]:
                b.speed = [0, -1]
            elif c == ord('s') and b.speed != [0, -1]:
                b.speed = [0, 1]

            # Other controls
            elif c == ord('q'):
                return "Players quit game >> PARITY"
            elif c == ord('p'):
                prompt = "GAME PAUSED. PRESS p TO RESUME"
                l = len(prompt)
                if self.paused:
                    self.screen.addstr(self.wheight - 1, (self.wwidth - l) // 2, " " * l)
                    self.paused = False
                else:
                    self.screen.addstr(self.wheight - 1, (self.wwidth - l) // 2, prompt)
                    self.screen.refresh()
                    self.paused = True
            
            # Frame update
            if not self.paused:
                a.update(self)
                b.update(self)

                # Check collisions
                prompt = "Snake {loser} bumped on {winner} >> {winner} WINS!"
                if a.collides_with(b):
                    self.over(prompt.format(loser=a.headchar, winner=b.headchar))
                elif b.collides_with(a):
                    self.over(prompt.format(loser=b.headchar, winner=a.headchar))
                
                # TODO: Check if player wins
            
                # Check if snakes ate pie
                if a.body[0] == self.pie:
                    a.grow = True
                    self.makepie()
                elif b.body[0] == self.pie:
                    b.grow = True
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
        description="A multiplayer curses implementation of the game Snake. Press " +
            "P to pause and Q/ESC to quit. To move snake A use the arrow keys " +
            "and WASD for snake B.")
    parser.add_argument("--toroidal", "-t", action="store_true", help=
                        "Activate toroidal space")
    args = parser.parse_args()

    try:
        result = curses.wrapper(main, args)
        print("\nGAME OVER: " + result + "\n")
    except KeyboardInterrupt:
        print("\nPROGRAM INTERRUPTED\n")
