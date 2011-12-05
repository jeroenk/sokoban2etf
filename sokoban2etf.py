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

BLOCK, FREE, GOAL, MAN, WALL = range(5)

class Cell(object):
    def __init__(self, cell_type):
        self.cell_type = cell_type
        self.in_use    = cell_type == GOAL

    def __str__(self):
        if   self.cell_type == BLOCK: return "$"
        elif self.cell_type == FREE : return " "
        elif self.cell_type == GOAL : return "."
        elif self.cell_type == MAN  : return "@"
        elif self.cell_type == WALL : return "#"

    def get_type(self):
        return self.cell_type

    def get_clean_type(self):
        return (FREE if self.cell_type == GOAL else self.cell_type)

    def get_use(self):
        return self.in_use

    def set_use(self, value):
        self.in_use = value

    def is_goal(self):
        return self.cell_type == GOAL

class Screen(object):
    def __init__(self):
        self.screen = [[]]

    def __str__(self):
        screen = ""

        for l in self.screen:
            for p in l:
                screen += str(p)

            screen += "\n"

        return screen

    def append_column(self, row, cell):
        for i in range(len(self.screen), row + 1):
            self.screen.append([])

        self.screen[row].append(cell)

    def used_iteration(self):
        screen  = self.screen
        changed = False

        for i in range(len(self.screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_use() or screen[i][j].get_type() == WALL:
                    continue

                if j - 1 >= 0 \
                        and screen[i][j - 1].get_use():
                    screen[i][j].set_use(True)
                    changed = True
                elif j + 1 < len(screen[i]) \
                        and screen[i][j + 1].get_use():
                    screen[i][j].set_use(True)
                    changed = True
                elif i - 1 >= 0 and j < len(screen[i - 1]) \
                        and screen[i - 1][j].get_use():
                    screen[i][j].set_use(True)
                    changed = True
                elif i + 1 < len(screen) and j < len(screen[i + 1]) \
                        and screen[i + 1][j].get_use():
                    screen[i][j].set_use(True)
                    changed = True

        return changed

    def mark_used(self):
        changed = True

        while changed:
            changed = self.used_iteration()

    def print_state(self):
        print "begin state"

        screen = self.screen
        string = ""

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_use():
                    string += "field_" + str(i) + "_" + str(j)
                    string += ":state_type "

        print string[:len(string) - 1]
        print "end state"

    def print_edge(self):
        print "begin edge"
        print "action:action_type"
        print "end edge"

    def print_init(self):
        print "begin init"

        screen = self.screen
        string = ""

        for i in range(len(screen)):
            for j in range(len(screen[i])):
                if screen[i][j].get_use():
                    string += str(screen[i][j].get_clean_type()) + " "

        print string[:len(string) - 1]
        print "end init"

    def print_move(self, i_man, j_man, i_free, j_free):
        string = ""

        for k in range(len(self.screen)):
            for l in range(len(self.screen[k])):
                if not self.screen[k][l].get_use():
                    continue

                if k == i_man and l == j_man:
                    string += str(MAN) + "/" + str(FREE) + " "
                elif k == i_free and l == j_free:
                    string += str(FREE) + "/" + str(MAN) + " "
                else:
                    string += "* "

        string += "0"
        print string

    def print_moves(self, i, j):
        screen = self.screen

        if j - 1 >= 0 \
                and screen[i][j - 1].get_use():
            print "begin trans"
            self.print_move(i, j, i, j - 1)
            print "end trans"

        if j + 1 < len(screen[i]) \
                and screen[i][j + 1].get_use():
            print "begin trans"
            self.print_move(i, j, i, j + 1)
            print "end trans"

        if i - 1 >= 0 and j < len(screen[i - 1]) \
                and screen[i - 1][j].get_use():
            print "begin trans"
            self.print_move(i, j, i - 1, j)
            print "end trans"

        if i + 1 < len(screen) and j < len(screen[i + 1]) \
                and screen[i + 1][j].get_use():
            print "begin trans"
            self.print_move(i, j, i + 1, j)
            print "end trans"

    def print_push(self, i_man, j_man, i_block, j_block, i_free, j_free):
        string = ""

        for k in range(len(self.screen)):
            for l in range(len(self.screen[k])):
                if not self.screen[k][l].get_use():
                    continue

                if k == i_man and l == j_man:
                    string += str(MAN) + "/" + str(FREE) + " "
                elif k == i_block and l == j_block:
                    string += str(BLOCK) + "/" + str(MAN) + " "
                elif k == i_free and l == j_free:
                    string += str(FREE) + "/" + str(BLOCK) + " "
                else:
                    string += "* "

        string += "0"
        print string

    def print_pushes(self, i, j):
        screen = self.screen

        if j - 2 >= 0 and j - 1 >= 0 \
                and screen[i][j - 2].get_use() and screen[i][j - 1].get_use():
            print "begin trans"
            self.print_push(i, j, i, j - 1, i, j - 2)
            print "end trans"

        if j + 1 < len(screen[i]) and j + 2 < len(screen[i]) \
                and screen[i][j + 1].get_use() and screen[i][j + 2].get_use():
            print "begin trans"
            self.print_push(i, j, i, j + 1, i, j + 2)
            print "end trans"

        if i - 1 >= 0 and i - 2 >= 0 \
                and j < len(screen[i - 1]) and j < len(screen[i - 2]) \
                and screen[i - 1][j].get_use() and screen[i - 2][j].get_use():
            print "begin trans"
            self.print_push(i, j, i - 1, j, i - 2, j)
            print "end trans"

        if i + 1 < len(screen) and i + 2 < len(screen) \
                and j < len(screen[i + 1]) and j < len(screen[i + 2]) \
                and screen[i + 1][j].get_use() and screen[i + 2][j].get_use():
            print "begin trans"
            self.print_push(i, j, i + 1, j, i + 2, j)
            print "end trans"

    def print_finished(self):
        print "begin trans"

        string = ""

        for i in range(len(self.screen)):
            for j in range(len(self.screen[i])):
                if self.screen[i][j].get_use():
                    if self.screen[i][j].is_goal():
                        string += str(BLOCK) + "/" + str(BLOCK) + " "
                    else:
                        string += "* "

        string += "1"
        print string
        print "end trans"

    def print_trans(self):
        for i in range(len(self.screen)):
            for j in range(len(self.screen[i])):
                if self.screen[i][j].get_use():
                    self.print_moves(i, j)
                    self.print_pushes(i, j)

        self.print_finished()

    def print_sorts(self):
        print "begin sort state_type"
        print "\"block\""
        print "\"free\""
        print "\"goal\""
        print "\"man\""
        print "\"wall\""
        print "end sort"

        print "begin sort action_type"
        print "\"step\""
        print "\"finished\""
        print "end sort"

def parse_screen(file_name):
    f = open(argv[1], 'rb')
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
            if   c == '$': cell = Cell(BLOCK)
            elif c == ' ': cell = Cell(FREE)
            elif c == '.': cell = Cell(GOAL)
            elif c == '@': cell = Cell(MAN)
            elif c == '#': cell = Cell(WALL)
            else:
                stderr.write("Invalid symbol '" + c + "' encountered\n")
                exit(1)
            screen.append_column(row, cell)

    return screen

def usage():
    stderr.write("Usage: " + argv[0] + " <sokoban screen>\n")
    exit(1)

def main():
    if len(argv) != 2:
        usage()

    screen = parse_screen(argv[1])
    screen.mark_used()

    screen.print_state()
    screen.print_edge()
    screen.print_init()
    screen.print_trans()
    screen.print_sorts()

main()
