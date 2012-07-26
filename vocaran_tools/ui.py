#!/usr/bin/env python3

import curses
import os
import os.path

DATA_DIR = os.path.join(os.environ['HOME'], '.vocaran_tools')

class UI:

    def __init__(self):
        self.stack = []
        self.push_scene(self.main_menu)

    def push_scene(self, scene):
        self.stack.append(scene)

    def pop_scene(self):
        self.stack.pop()

    def main_menu(self, stdscr):
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Welcome to vocaloid_tools utility!")
            stdscr.addstr(2, 0, "What would you like to do?")
            stdscr.addstr(3, 3, "q - Quit")
            stdscr.refresh()

            c = stdscr.getch()
            if c == ord('q'):
                raise ExitException

    def main(self, stdscr):
        while len(self.stack) > 0:
            try:
                self.stack[-1](stdscr)
            except ExitException:
                break


class ExitException(Exception): pass

if __name__ == "__main__":
    x = UI()
    curses.wrapper(x.main)
