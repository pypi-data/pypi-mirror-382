"""pyquarium, by Alexander Walters <https://github.com/awinstonw>,
adapted from Al Sweigart's, <https://alsweigart.com>, fishtank.py script
in *The Big Book of Small Python Projects*. The code has been refactored
to be more object oriented and I made some minor edits to the visual
presentation of the sandy bottom, the logic for determining where the
individual aquarium member objects spawn and in what z-order, and then
ported the whole thing over to use curses instead of bext. I also added
the ability to add/remove memebers from the aquarium on-the-fly.
Additionally, I added a CLI.
Book available: <https://nostarch.com/big-book-small-python-programming>
"""

import curses
import random
import sys
import time

import pyquarium.aquarium as aq

__version__ = 'v2.0.0'


def render_aquarium(fish_count: int, bubbler_count: int, kelp_count: int,
                    fps: int):
    """Print a moving aquarium to the terminal.

    Keyword arguments:
    fish -- the number of fish to show.
    bubblers -- the number of bubble generators to show.
    kelp -- the number of kelp strands.
    fps -- the speed of the simulation.
    """
    # Longest fish in the type dictionary to avoid spawning a fish
    # ouside the terminal boundary.
    max_length = 0
    for type in aq.FISH_TYPE:
        if len(type['right'][0]) > max_length:
            max_length = len(type['right'][0])

    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        height, width = stdscr.getmaxyx()
        height -= 1
        width -= 1
        bottom = height - 1  # Accounts for the sandy bottom.
        denominator = fps
        fish_list = [aq.Fish(random.randint(0, bottom),
                             random.randint(0, width - max_length))
                     for i in range(fish_count)]
        # Avoid putting the kelp and bubblers at the same column or on
        # the very edge.
        randoms = [*range(1, width - 1)]
        random.shuffle(randoms)
        kelp_list = []
        bubbler_list = []
        for x in randoms[:kelp_count]:
            kelp_list.append(aq.Kelp(random.randint(6, bottom), x))
            del randoms[0]
        for x in randoms[:bubbler_count]:
            bubbler_list.append(aq.Bubbler(bottom, x))
            del randoms[0]
        # Color 1 is the bubble color.
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # Color 3 is the kelp color.
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # Color 4 is the sandy bottom color.
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # Colors 3, 4 above and 5-8 below are all for the fish.
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            key = stdscr.getch()
            curses.flushinp()
            if key == ord('q'):
                # 2025-06-26: In python 3.13 curses.endwin() is throwing
                # an error and not exiting cleanly for some unknown
                # reason. Keeping the code the same here it now throws
                # the error up to the containing try/except block which
                # calls sys.exit() when handling a curses.error and then
                #  exits cleanly from there.
                curses.endwin()
                break
            elif key == ord('f'):
                fish_list.append(aq.Fish(random.randint(0, bottom),
                                 random.randint(0, width - max_length)))
            elif key == ord('d') and fish_list:
                del fish_list[0]
            elif key == ord('k') and randoms:
                kelp_list.append(aq.Kelp(random.randint(6, bottom),
                                         randoms[0]))
                del randoms[0]
            elif key == ord('j') and kelp_list:
                randoms.append(kelp_list[0].x)
                random.shuffle(randoms)
                del kelp_list[0]
            elif key == ord('b') and randoms:
                bubbler_list.append(aq.Bubbler(bottom, randoms[0]))
                del randoms[0]
            elif key == ord('v') and bubbler_list:
                randoms.append(bubbler_list[0].x)
                random.shuffle(randoms)
                del bubbler_list[0]
            elif key == ord('+'):
                denominator += 1
            elif key == ord('-') and denominator > 1:
                denominator -= 1
            # Draw the aquarium members with the kelp at the back, the fish
            # in the middle, and the bubbles up front.
            for kelp in kelp_list:
                kelp.sway()
                kelp.draw(stdscr, bottom)
            for fish in fish_list:
                fish.swim(bottom, width)
                fish.draw(stdscr)
            for bubbler in bubbler_list:
                bubbler.burble(width)
                for bubble in bubbler.bubbles:
                    bubble.draw(stdscr)
            # Draw '░' for the sandy bottom.
            stdscr.addstr(height, 0, chr(9617) * width, curses.color_pair(4))
            stdscr.refresh()
            time.sleep(1 / denominator)

    try:
        curses.wrapper(main)
    except KeyboardInterrupt, curses.error:
        sys.exit()
