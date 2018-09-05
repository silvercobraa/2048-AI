#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Puzzle2048(object):
    """Clase que representa el estado del Puzzle 2048."""
    def __init__(self, state=[[0 for j in range(4)] for i in range(4)], initial_tiles=0):
        super(Puzzle2048, self).__init__()
        self.__state = state
        self.__score = 0
        for i in range(initial_tiles):
            self.__place_random_tile()

    # Private
    def __random_value():
        """Retorna un 2 con probabilidad 0.9 o un 4 con probabilidad 0.1"""
        r = random.randint(0, 9) % 10
        if r == 0:
            return 4
        else:
            return 2

    def __place_random_tile(self):
        """Coloca un __random_value en una celda disponible."""
        available_cells = []
        for i, row in enumerate(self.__state):
            for j, k in enumerate(row):
                if k == 0:
                    available_cells.append((i, j))
        r = random.choice(available_cells)
        self.__state[r[0]][r[1]] = Puzzle2048.__random_value()

    def __merge(self, i1, j1, i2, j2):
        """Mueve la celda[i2][j2] a la celda adjacente [i1][i2], si es posible, \
        combinando ambas si es necesario. Este método solo debiera ser llamado\
        por las funciones 'move'. Retorna true si hubo un merge, falso si solo
        se desplazó una celda o si no se pudo hacer nada."""
        v1 = self.__state[i1][j1]
        v2 = self.__state[i2][j2]
        # si la celda destino está vacía, simplemente movemos la otra celda
        if v1 == 0:
            self.__state[i1][j1] = v2
            self.__state[i2][j2] = 0
            return False
        # si ambas tienen el mismo valor, las combinamos
        elif v1 == v2:
            self.__state[i1][j1] = v1 + v2
            self.__state[i2][j2] = 0
            self.__score += v1 + v2
            return True
        # si no se pudo mover retornamos falso
        return False

    # Public
    def get_score(self):
        return self.__score

    def get_state(self):
        """Retorna una copia del estado actual."""
        return [row.copy() for row in self.__state]

    def __repr__(self):
        ret = ''
        for row in self.__state:
            for x in row:
                ret += str(x) + ' '
            ret += '\n'
        return ret

    def move_left(self):
        """Ejecuta un movimiento hacia la izquierda. Retorna Falso si no es posible realizarlo."""
        prev_state = self.get_state()
        merge = []
        for i, row in enumerate(self.__state):
            merge = [False, False, False]
            merge[0] = self.__merge(i, 0, i, 1)
            merge[1] = self.__merge(i, 1, i, 2)
            merge[2] = self.__merge(i, 2, i, 3)
            merge[0] = True if merge[0] or merge[1] else self.__merge(i, 0, i, 1)
            merge[1] = True if merge[1] or merge[2] else self.__merge(i, 1, i, 2)
            merge[0] = True if merge[0] or merge[1] else self.__merge(i, 0, i, 1)

        # print(self)
        if prev_state != self.__state:
            self.__place_random_tile()
            # print(self)
            return True

        return False

    def move_right(self):
        prev_state = self.get_state()
        merge = []
        for i, row in enumerate(self.__state):
            merge = [False, False, False]
            merge[0] = self.__merge(i, 3, i, 2)
            merge[1] = self.__merge(i, 2, i, 1)
            merge[2] = self.__merge(i, 1, i, 0)
            merge[0] = True if merge[0] or merge[1] else self.__merge(i, 3, i, 2)
            merge[1] = True if merge[1] or merge[2] else self.__merge(i, 2, i, 1)
            merge[0] = True if merge[0] or merge[1] else self.__merge(i, 3, i, 2)

        # print(self)
        if prev_state != self.__state:
            self.__place_random_tile()
            # print(self)
            return True

        return False

    def move_up(self):
        prev_state = self.get_state()
        merge = []
        for j in range(4):
            merge = [False, False, False]
            merge[0] = self.__merge(0, j, 1, j)
            merge[1] = self.__merge(1, j, 2, j)
            merge[2] = self.__merge(2, j, 3, j)
            merge[0] = True if merge[0] or merge[1] else self.__merge(0, j, 1, j)
            merge[1] = True if merge[1] or merge[2] else self.__merge(1, j, 2, j)
            merge[0] = True if merge[0] or merge[1] else self.__merge(0, j, 1, j)

        # print(self)
        if prev_state != self.__state:
            self.__place_random_tile()
            # print(self)
            return True

        return False

    def move_down(self):
        prev_state = self.get_state()
        merge = []
        for j in range(4):
            merge = [False, False, False]
            merge[0] = self.__merge(3, j, 2, j)
            merge[1] = self.__merge(2, j, 1, j)
            merge[2] = self.__merge(1, j, 0, j)
            merge[0] = True if merge[0] or merge[1] else self.__merge(3, j, 2, j)
            merge[1] = True if merge[1] or merge[2] else self.__merge(2, j, 1, j)
            merge[0] = True if merge[0] or merge[1] else self.__merge(3, j, 2, j)

        # print(self)
        if prev_state != self.__state:
            self.__place_random_tile()
            # print(self)
            return True

        return False

    def random_move(self):
        """Ejecuta al azar uno de los 4 movimientos posibles y lo ejecuta."""
        moves = [self.move_up, self.move_left, self.move_down, self.move_right]
        move = random.choice(moves)
        # print(move.__name__)
        return move()

    def available_moves(self):
        # creo las 4 ramas posibles con una copia del estado actual
        u = Puzzle2048(state=self.get_state())
        l = Puzzle2048(state=self.get_state())
        d = Puzzle2048(state=self.get_state())
        r = Puzzle2048(state=self.get_state())
        moves = []
        u.move_up()
        if self.__state != u.get_state():
            moves.append(self.move_up)
        l.move_left()
        if self.__state != l.get_state():
            moves.append(self.move_left)
        d.move_down()
        if self.__state != d.get_state():
            moves.append(self.move_down)
        r.move_right()
        if self.__state != r.get_state():
            moves.append(self.move_right)
        return moves

def simulate(puzzle):
    simulation_puzzle = Puzzle2048(state=puzzle.get_state())
    it = 0
    moves = simulation_puzzle.available_moves()
    while moves != []:
        # if it > 10000:
            # return simulation_puzzle.random_move()
        # print(moves)
        move = random.choice(moves)
        move()
        it += 1
        moves = simulation_puzzle.available_moves()
    return simulation_puzzle.get_score()

def pure_mcts(puzzle, iterations):
    u = Puzzle2048(state=puzzle.get_state())
    l = Puzzle2048(state=puzzle.get_state())
    d = Puzzle2048(state=puzzle.get_state())
    r = Puzzle2048(state=puzzle.get_state())
    u.move_up()
    l.move_left()
    d.move_down()
    r.move_right()
    puzzles = [u, l, d, r]
    # print(puzzles)
    scores = [0, 0, 0, 0]
    for i in range(iterations):
        for j, puzz in enumerate(puzzles):
            scores[j] += simulate(puzz)
            # print(scores[j])

    max_score = max(scores)
    # print(scores, max_score)
    # aunque improbable, puede haber mas de una simulacion con el mismo puntaje
    # en ese caso, decidimos al azar entre ellas
    moves = [i for i, score in enumerate(scores) if score == max_score]
    move = random.choice(moves)
    if move == 0:
        puzzle.move_up()
        return 'UP'
    elif move == 1:
        puzzle.move_left()
        return 'LEFT'
    elif move == 2:
        puzzle.move_down()
        return 'DOWN'
    elif move == 3:
        puzzle.move_right()
        return 'RIGHT'



def main():
    p = Puzzle2048(initial_tiles=2)
    it = 1
    while p.available_moves():
        print('pure_mcts:', pure_mcts(p, it))
        print(p)
        it += 1

if __name__ == '__main__':
    main()
