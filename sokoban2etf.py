#!/usr/bin/python
#
# Copyright (c) 2011, Jeroen Ketema, University of Twente
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  * Neither the name of the University of Twente nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from sys import argv, stderr

SORT_COUNT = 5
BLOCK, FREE, MAN, GOAL, WALL = range(SORT_COUNT)
STATE_TYPE  = "state_type"

ACTION_COUNT = 5
LEFT, UP, RIGHT, DOWN, FINISH = range(ACTION_COUNT)
ACTION_TYPE = "action_type"

class Cell(object):
    def __init__(self, cell_type):
        if   cell_type == '$': self.cell_type = BLOCK
        elif cell_type == ' ': self.cell_type = FREE
        elif cell_type == '@': self.cell_type = MAN
        elif cell_type == '.': self.cell_type = GOAL
        elif cell_type == '#': self.cell_type = WALL
        else:
            stderr.write("Invalid symbol '" + cell_type + "' encountered\n")
            exit(1)

        self.in_use = self.cell_type == GOAL or self.cell_type == MAN

    def __str__(self):
        if   self.cell_type == BLOCK: return "$"
        elif self.cell_type == FREE : return " "
        elif self.cell_type == MAN  : return "@"
        elif self.cell_type == GOAL : return "."
        elif self.cell_type == WALL : return "#"

    def get_type(self):
        return self.cell_type

    def get_primitive_type(self):
        return (FREE if self.cell_type == GOAL else self.cell_type)

    def get_used(self):
        return self.in_use

    def set_in_use(self):
        self.in_use = True

    def is_goal(self):
        return self.cell_type == GOAL

class Screen(object):
    def __init__(self):
        self.screen = [[]]

    def __str__(self):
        screen = self.screen
        string = ""

        for  i in range(len(screen)):
            for j in range(len(screen[i])):
                char = str(screen[i][j])

                if screen[i][j].get_used() and char == ' ':
                    if self.is_corner(i, j):
                        char = 'c'
                    elif self.is_alcove(i, j):
                        char = 'a'

                string += char

            string += "\n"

        return string

    def append_column(self, row, cell):
        for i in range(len(self.screen), row + 1):
            self.screen.append([])

        self.screen[row].append(cell)

    def find_direct_use(self):
        screen  = self.screen
        changed = False

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_used() or screen[i][j].get_type() == WALL:
                    continue

                if j - 1 >= 0 \
                        and screen[i][j - 1].get_used():
                    screen[i][j].set_in_use()
                    changed = True
                elif j + 1 < len(screen[i]) \
                        and screen[i][j + 1].get_used():
                    screen[i][j].set_in_use()
                    changed = True
                elif i - 1 >= 0 and j < len(screen[i - 1]) \
                        and screen[i - 1][j].get_used():
                    screen[i][j].set_in_use()
                    changed = True
                elif i + 1 < len(screen) and j < len(screen[i + 1]) \
                        and screen[i + 1][j].get_used():
                    screen[i][j].set_in_use()
                    changed = True

        return changed

    def mark_used(self):
        changed = True

        while changed:
            changed = self.find_direct_use()

    def get_state(self):
        screen = self.screen
        string = "begin state\n"

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_used():
                    string += "field_" + str(i) + "_" + str(j)
                    string += ":" + STATE_TYPE + " "

        string  = string[:len(string) - 1] + "\n"
        string += "end state"
        return string

    def get_edge(self):
        return "begin edge\n" \
            + "action:" + ACTION_TYPE + "\n" \
            + "end edge"

    def get_init(self):
        screen = self.screen

        string = "begin init\n"

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_used():
                    string += str(screen[i][j].get_primitive_type()) + " "

        string  = string[:len(string) - 1] + "\n"
        string += "end init"
        return string

    def get_move(self, i_man, j_man, i_free, j_free, direction):
        string = ""

        for k in range(len(self.screen)):
            for l in range(len(self.screen[k])):
                if not self.screen[k][l].get_used():
                    continue

                if k == i_man and l == j_man:
                    string += str(MAN) + "/" + str(FREE) + " "
                elif k == i_free and l == j_free:
                    string += str(FREE) + "/" + str(MAN) + " "
                else:
                    string += "* "

        string += str(direction)
        return string

    def get_moves(self, i, j):
        screen = self.screen
        string = ""

        if j - 1 >= 0 \
                and screen[i][j - 1].get_used():
            string += "begin trans\n" \
                + self.get_move(i, j, i, j - 1, LEFT) + "\n" \
                + "end trans\n"

        if i - 1 >= 0 and j < len(screen[i - 1]) \
                and screen[i - 1][j].get_used():
            string += "begin trans\n" \
                + self.get_move(i, j, i - 1, j, UP) + "\n" \
                + "end trans\n"

        if j + 1 < len(screen[i]) \
                and screen[i][j + 1].get_used():
            string += "begin trans\n" \
                + self.get_move(i, j, i, j + 1, RIGHT) + "\n" \
                + "end trans\n"

        if i + 1 < len(screen) and j < len(screen[i + 1]) \
                and screen[i + 1][j].get_used():
            string += "begin trans\n" \
                + self.get_move(i, j, i + 1, j, DOWN) + "\n" \
                + "end trans\n"

        return string

    def get_push(self, i_man, j_man, i_block, j_block, i_free, j_free, \
                     direction):
        string = ""

        for k in range(len(self.screen)):
            for l in range(len(self.screen[k])):
                if not self.screen[k][l].get_used():
                    continue

                if k == i_man and l == j_man:
                    string += str(MAN) + "/" + str(FREE) + " "
                elif k == i_block and l == j_block:
                    string += str(BLOCK) + "/" + str(MAN) + " "
                elif k == i_free and l == j_free:
                    string += str(FREE) + "/" + str(BLOCK) + " "
                else:
                    string += "* "

        string += str(direction)
        return string

    def is_corner(self, i, j):
        screen = self.screen

        if screen[i][j].get_type() == GOAL:
            return False

        if i - 1 >= 0 and j < len(screen[i - 1]) \
                and screen[i - 1][j].get_type() == WALL:
            if j - 1 >= 0 and screen[i][j - 1].get_type() == WALL:
                return True
            elif j + 1 < len(screen[i]) and screen[i][j + 1].get_type() == WALL:
                return True
        elif i + 1 < len(screen) and j < len(screen[i + 1]) \
                and screen[i + 1][j].get_type() == WALL:
            if j - 1 >= 0 and screen[i][j - 1].get_type() == WALL:
                return True
            elif j + 1 < len(screen[i]) and screen[i][j + 1].get_type() == WALL:
                return True

        return False

    def is_horizontal_half_alcove(self, i, i_wall, j, inc):
        screen = self.screen

        if screen[i][j].get_type() == GOAL:
            return False

        if j + inc >= 0 and j + inc < len(screen[i]):
            if screen[i][j + inc].get_type() == WALL:
                return True
            elif j + inc >= 0 and j + inc < len(screen[i_wall]) \
                    and screen[i_wall][j + inc].get_type() == WALL:
                return self.is_horizontal_half_alcove(i, i_wall, j + inc, inc)

        return False

    def is_vertical_half_alcove(self, i, j, j_wall, inc):
        screen = self.screen

        if screen[i][j].get_type() == GOAL:
            return False

        if i + inc >= 0 and i + inc < len(screen):
            if j < len(screen[i + inc]) \
                    and screen[i + inc][j].get_type() == WALL:
                return True
            elif j_wall < len(screen[i + inc]) \
                    and screen[i + inc][j_wall].get_type() == WALL:
                return self.is_vertical_half_alcove(i + inc, j, j_wall, inc)

        return False

    def is_alcove(self, i, j):
        screen = self.screen
        found = False

        if not found and j - 1 >= 0 \
                and screen[i][j - 1].get_type() == WALL:
            found = self.is_vertical_half_alcove(i, j, j - 1, -1) \
                and self.is_vertical_half_alcove(i, j, j - 1, 1)

        if not found and j + 1 < len(screen[i]) \
                and screen[i][j + 1].get_type() == WALL:
            found = self.is_vertical_half_alcove(i, j, j + 1, -1) \
                and self.is_vertical_half_alcove(i, j, j + 1, 1)

        if not found and i - 1 >= 0 and j < len(screen[i - 1]) \
                and screen[i - 1][j].get_type() == WALL:
            found = self.is_horizontal_half_alcove(i, i - 1, j, -1) \
                and self.is_horizontal_half_alcove(i, i - 1, j, 1)

        if not found and i + 1 < len(screen) and j < len(screen[i + 1]) \
                and screen[i + 1][j].get_type() == WALL:
            found = self.is_horizontal_half_alcove(i, i + 1, j, -1) \
                and self.is_horizontal_half_alcove(i, i + 1, j, 1)

        return found

    def is_useless_position(self, i, j):
        return self.is_corner(i, j) \
            or self.is_alcove(i, j)

    def get_pushes(self, i, j, optimized):
        screen = self.screen
        string = ""

        if j - 2 >= 0 and j - 1 >= 0 \
                and screen[i][j - 2].get_used() and screen[i][j - 1].get_used():
            if not optimized or not self.is_useless_position(i, j - 2):
                string += "begin trans\n" \
                    + self.get_push(i, j, i, j - 1, i, j - 2, LEFT) + "\n" \
                    + "end trans\n"

        if i - 1 >= 0 and i - 2 >= 0 \
                and j < len(screen[i - 1]) and j < len(screen[i - 2]) \
                and screen[i - 1][j].get_used() and screen[i - 2][j].get_used():
            if not optimized or not self.is_useless_position(i - 2, j):
                string += "begin trans\n" \
                    + self.get_push(i, j, i - 1, j, i - 2, j, UP) + "\n" \
                    + "end trans\n"

        if j + 1 < len(screen[i]) and j + 2 < len(screen[i]) \
                and screen[i][j + 1].get_used() and screen[i][j + 2].get_used():
            if not optimized or not self.is_useless_position(i, j + 2):
                string += "begin trans\n" \
                    + self.get_push(i, j, i, j + 1, i, j + 2, RIGHT) + "\n" \
                    + "end trans\n"

        if i + 1 < len(screen) and i + 2 < len(screen) \
                and j < len(screen[i + 1]) and j < len(screen[i + 2]) \
                and screen[i + 1][j].get_used() and screen[i + 2][j].get_used():
            if not optimized or not self.is_useless_position(i + 2, j):
                string += "begin trans\n" \
                    + self.get_push(i, j, i + 1, j, i + 2, j, DOWN) + "\n" \
                    + "end trans\n"

        return string

    def get_finished(self):
        screen = self.screen
        string = "begin trans\n"

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_used():
                    if screen[i][j].is_goal():
                        string += str(BLOCK) + "/" + str(BLOCK) + " "
                    else:
                        string += "* "

        string += str(FINISH) + "\n"
        string += "end trans"
        return string

    def get_trans(self, optimized):
        string = ""

        for i in range(len(self.screen)):
            for j in range(len(self.screen[i])):
                if self.screen[i][j].get_used():
                    string += self.get_moves(i, j)
                    string += self.get_pushes(i, j, optimized)

        string += self.get_finished()
        return string

    def get_sorts(self):
        string = "begin sort " + STATE_TYPE + "\n"
        for i in range(SORT_COUNT):
            if   i == BLOCK: string += "\"block\"\n"
            elif i == FREE : string += "\"free\"\n"
            elif i == MAN  : string += "\"man\"\n"
            # GOAL and MAN are not needed in the etf
            # elif i == GOAL : string += "\"goal\"\n"
            # elif i == WALL : string += "\"wall\"\n"
        string += "end sort\n"

        string += "begin sort " + ACTION_TYPE + "\n"
        for i in range(ACTION_COUNT):
            if   i == LEFT  : string += "\"l\"\n"
            elif i == UP    : string += "\"u\"\n"
            elif i == RIGHT : string += "\"r\"\n"
            elif i == DOWN  : string += "\"d\"\n"
            elif i == FINISH: string += "\"finish\"\n"
        string += "end sort"
        return string

def parse_screen(file_name):
    f = open(file_name, 'rb')
    d = f.read()
    f.close()

    row = 0

    screen = Screen()

    for c in d:
        if c == '\n':
            row += 1
        elif c == '\r':
            continue
        else:
            cell = Cell(c)
            screen.append_column(row, cell)

    return screen

def usage():
    stderr.write("Usage: " + argv[0] + " [--optimize] <sokoban screen>\n")
    exit(1)

def main():
    if len(argv) == 2:
        file_name = argv[1]
        optimized = False
    elif len(argv) == 3 and argv[1] == "--optimize":
        file_name = argv[2]
        optimized = True
    elif len(argv) == 3 and argv[2] == "--optimize":
        file_name = argv[1]
        optimized = True
    else:
        usage()

    screen = parse_screen(file_name)
    screen.mark_used()

    stderr.write(str(screen))

    print screen.get_state()
    print screen.get_edge()
    print screen.get_init()
    print screen.get_trans(optimized)
    print screen.get_sorts()

main()
