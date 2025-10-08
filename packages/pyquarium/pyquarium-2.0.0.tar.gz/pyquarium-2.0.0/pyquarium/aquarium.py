"""Constant for the valid fish art styles, and classes for all the
possible aqarium members.
"""

import curses
import random

# All entries in the dict for an individual fish type must have the same
# string length.
FISH_TYPE = [
    {'right': ['><>'],          'left': ['<><']},
    {'right': ['>||>'],         'left': ['<||<']},
    {'right': ['>))>'],         'left': ['<[[<']},
    {'right': ['>||o', '>||.'], 'left': ['o||<', '.||<']},
    {'right': ['>))o', '>)).'], 'left': ['o[[<', '.[[<']},
    {'right': ['>-==>'],        'left': ['<==-<']},
    {'right': [r'>\\>'],        'left': ['<//<']},
    {'right': ['><)))*>'],      'left': ['<*(((><']},
    {'right': ['}-[[[*>'],      'left': ['<*]]]-{']},
    {'right': [']-<)))b>'],     'left': ['<d(((>-[']},
    {'right': ['><XXX*>'],      'left': ['<*XXX><']},
    {'right': ['_.-._.-^=>', '.-._.-.^=>',
               '-._.-._^=>', '._.-._.^=>'],
      'left': ['<=^-._.-._', '<=^.-._.-.',
               '<=^_.-._.-', '<=^._.-._.']},
    {'right': ['}>=b>'],        'left': ['<d=<{']},
    {'right': [')+++}Xb>'],     'left': ['<dX{+++(']},
]


class Fish:
    """Fish class for all the fish in the aquarium."""

    def __init__(self, y: int, x: int):
        """Initialize a fish at cordinates y, x.

        Keyword arguments:
        y -- y coordinate.
        x -- x coodrinate.
        """
        type = random.choice(FISH_TYPE)
        color_pattern = random.choice(('random', 'head-tail', 'single'))
        self.length = len(type['right'][0])
        colors = []
        if color_pattern == 'random':
            for i in range(self.length):
                colors.append(random.choice(range(3, 8)))
        if color_pattern == 'single' or color_pattern == 'head-tail':
            colors = [random.choice(range(3, 8))] * self.length
        if color_pattern == 'head-tail':
            headTailColor = random.choice(range(3, 8))
            colors[0] = headTailColor
            colors[-1] = headTailColor
        self.right = type['right']
        self.left = type['left']
        self.color = colors
        self.h_speed = random.randint(1, 6)
        self.v_speed = random.randint(5, 15)
        self.h_bearing_count = random.randint(10, 60)
        self.v_bearing_count = random.randint(2, 20)
        self.bearing_right = random.choice((True, False))
        self.descending = random.choice((True, False))
        self.x = x
        self.y = y
        self.counter = 1

    def swim(self, bottom_edge: int, right_edge: int):
        """Calculate the random swimming motion of the fish by adjusting
        its x and y.

        Keyword arguments:
        bottom_edge -- Bottom edge boundary for the fish to swim within.
        right_edge -- Right edge boundary for the fish to swim within.
        """
        if self.counter % self.h_speed == 0:
            if self.bearing_right:
                if self.x != right_edge - self.length:
                    self.x += 1
                else:
                    self.bearing_right = False
                    self.color.reverse()
            else:
                if self.x != 0:
                    self.x -= 1
                else:
                    self.bearing_right = True
                    self.color.reverse()
        self.h_bearing_count -= 1
        if self.h_bearing_count == 0:
            self.h_bearing_count = random.randint(10, 60)
            self.bearing_right = not self.bearing_right
        if self.counter % self.v_speed == 0:
            if self.descending:
                if self.y != bottom_edge:
                    self.y += 1
                else:
                    self.descending = False
            else:
                if self.y != 0:
                    self.y -= 1
                else:
                    self.descending = True
        self.v_bearing_count -= 1
        if self.v_bearing_count == 0:
            self.v_bearing_count = random.randint(2, 20)
            self.descending = not self.descending
        self.counter += 1

    def draw(self, stdscr):
        """Draw the fish on the terminal window.

        Keyword arguments:
        stdscr -- Curses window in which to draw.
        """
        if self.bearing_right:
            fish_text = self.right[self.counter % len(self.right)]
        else:
            fish_text = self.left[self.counter % len(self.left)]
        x_position = self.x
        for i, fish_part in enumerate(fish_text):
            stdscr.addstr(self.y, self.x, fish_part,
                          curses.color_pair(self.color[i]))
            self.x += 1
        self.x = x_position


class Bubbler:
    """Class for all the bubble nucleation points in the aquarium."""

    def __init__(self, y: int, x: int):
        """Initialize a bubbler at coordinates y, x.

        Keyword arguments:
        y -- y coordinate.
        x -- x coodrinate.
        """
        self.y = y + 1
        self.x = x
        self.bubbles = []

    def burble(self, right_edge):
        """Calculate the random bubbling from the bubbler.

        Keyword arguments:
        right_edge -- Right boundary for the bubbles to float within.
        """
        if random.randint(1, 5) == 1:
            self.bubbles.append(self.Bubble(self.y, self.x))
        for i in range(len(self.bubbles) - 1, -1, -1):
            if self.bubbles[i].y == 0:
                del self.bubbles[i]
        for bubble in self.bubbles:
            bubble.float(right_edge)

    class Bubble:
        """Class for the individual bubbles emanating from a Bubbler."""

        def __init__(self, y: int, x: int):
            """Initialize a bubble at coordinates y, x.

            Keyword arguments:
            y -- y coordinate.
            x -- x coordinate.
            """
            self.y = y
            self.x = x
            self.origin = y

        def float(self, right_edge):
            """Calculate the random floating motion of the bubble.

            Keyword arguments:
            right_edge -- Right boundary for the bubbles.
            """
            diceRoll = random.randint(1, 6)
            if self.y != self.origin:  # Bubble up from a fixed point.
                if (diceRoll == 1) and (self.x > 0):
                    self.x -= 1
                elif (diceRoll == 2) and (self.x < right_edge):
                    self.x += 1
            self.y -= 1

        def draw(self, stdscr):
            """Draw the bubble on the terminal window.

            Keyword arguments:
            stdscr -- Curses window in which to draw.
            """
            stdscr.addstr(self.y, self.x, random.choice(('o', 'O')),
                          curses.color_pair(1))


class Kelp:
    """Class for all the kelp strands in the aquarium."""

    def __init__(self, y: int, x: int):
        """Initialize a kelp strand of height y at x coordinate x.

        Keyword arguments:
        y -- y coordinate.
        x -- x coordinate.
        """
        self.y = y
        self.x = x
        self.segments = [random.choice(['(', ')']) for i in range(self.y)]

    def sway(self):
        """Calculate the random swaying motion of the kelp strand."""
        for i, segment in enumerate(self.segments):
            if random.randint(1, 20) == 1:
                if segment == '(':
                    self.segments[i] = ')'
                elif segment == ')':
                    self.segments[i] = '('

    def draw(self, stdscr, bottom_edge: int):
        """Draw the kelp strand on the terminal window.

        Keyword arguments:
        stdscr -- Curses window in which to draw.
        bottom_edge -- Bottom edge at which to position the kelp base.
        """
        for i, segment in enumerate(self.segments):
            if segment == '(':
                stdscr.addstr(bottom_edge - i, self.x, segment,
                              curses.color_pair(3))
            elif segment == ')':
               stdscr.addstr(bottom_edge - i, self.x + 1, segment,
                             curses.color_pair(3))
