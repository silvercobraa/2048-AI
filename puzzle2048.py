#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Esta clase implementa todas las mecánicas del juego.
# Por razones de eficiencia, todos los métodos son estáticos, para evitar el overhead
# extra de crear instancias cada vez. Éstos métodos pueden pensarse como que son
# simplemente funciones, pero bajo el scope de una clase.
# Todas las funciones son puras, es decir que no alteran el estado de los parámetros
# pasados, y siempre retornan el mismo output para un mismo input.
# El estado del puzzle se representa con 64 bits: 4 bits por cada una de las celdas
# del puzzle. Cada uno de estos 4 bits puede guardar un valor entre 0 y 15, el
# cual representa el exponente de la potencia de 2 del valor en su celda correspondiente.
# Por ejemplo, para representar un 32 se guardará un 5. Se ve entonces que esta
# implementación aguantará un máximo de 2^15 = 32768 por celda antes de hacer overflow.
# El orden de los grupos de 4 bits está en row major order, es decir los primeros
# 4 bits menos significatvos son la celda (0, 0), los 16 bits menos significativos
# corresponden a la fila 0, los 4 bits más significativos corresponden a la celda (3, 3).
# Por eficiencia, los movimientos se ejecutan consultando lookup tables. Si bien no
# podemos precomputar los 4 movimientos de cada uno de los 2^64 estados posibles, sí
# podemos hacerlo por fila.
# Se tienen 2 tablas, una para los movimientos left y otra para los movimientos right,
# esta última calculada simplemente revirtiendo el orden de los grupos de 4 bits de cada fila,
# consultando la tabla para left y finalmente revirtiendo el resultado.
# La accion left se calcula consultando la lookup table left para cada fila del puzzle.
# La accion right se calcula consultando la lookup table left para cada fila del puzzle.
# La accion up se calcula transponiendo la matriz del puzzle, consultando la lookup table
# left para cada fila y finalmente transponiendo el resultado.
# La accion down se calcula transponiendo la matriz del puzzle, consultando la lookup table
# right para cada fila y finalmente transponiendo el resultado.
import random

class Puzzle2048(object):
    """Clase que representa el estado del Puzzle 2048."""
    # maximo hay 2^16 posibilidades por cada fila
    __move_right_lookup = [0 for i in range(1 << 16)]
    __move_left_lookup = [0 for i in range(1 << 16)]
    __score_lookup = [0 for i in range(1 << 16)]
    __h1 = [0, 4, 8, 12, 13, 9, 5, 1, 2, 6, 10, 14, 15, 11, 7, 3]
    __h2 = [0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11, 15, 14, 13, 12]
    __h3 = [12, 11, 10, 9, 13, 12, 11, 10, 14, 13, 12, 11, 15, 14, 13, 12]

    # moves = [up, Puzzle2048.left, Puzzle2048.down, Puzzle2048.right]

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
        return 2 if r == 0 else 1

    def __reverse(word):
        """Revierte el orden de los BYTES de word. Util para calcular las lookup tables para los movimientos left a partir de los right."""
        b0 = (word >> 0) & 0xF
        b1 = (word >> 4) & 0xF
        b2 = (word >> 8) & 0xF
        b3 = (word >> 12) & 0xF
        ret = (b0 << 12) | (b1 << 8) | (b2 << 4) | (b3 << 0)
        return ret

    def __transpose(state):
        a1 = state & 0xF0F00F0FF0F00F0F
        a2 = state & 0x0000F0F00000F0F0
        a3 = state & 0x0F0F00000F0F0000
        a = a1 | (a2 << 12) | (a3 >> 12)
        b1 = a & 0xFF00FF0000FF00FF
        b2 = a & 0x00FF00FF00000000
        b3 = a & 0x00000000FF00FF00
        return b1 | (b2 >> 24) | (b3 << 24)
        new_state = 0
        for i in range(4):
            for j in range(4):
                new_state |= ((state >> 16*i + 4*j) & 0xF) << (16*j + 4*i)
        return new_state

    def __merge(row, source, destiny):
        """Combina 2 celdas consecutivas. Retorna una tripleta con un booleano, el nuevo valor source y el nuevo valor destiny. \
        El booleano indica si es que se combinaron los valores source y destiny, es decir eran iguales. \
        Esto es util para no hacer más de 1 merge donde no corresponda."""
        if destiny == 0:
            return False, 0, source
        elif source == destiny:
            # por cada merge en la fila se suma la potencia de 2 producida al puntaje
            Puzzle2048.__score_lookup[row] += 1 << (destiny + 1)
            return True, 0, destiny + 1
        return False, source, destiny

    def precompute_tables():
        """Esto es dificil de explicar..."""
        for row in range(1 << 16):
            b0 = (row >> 0) & 0xF
            b1 = (row >> 4) & 0xF
            b2 = (row >> 8) & 0xF
            b3 = (row >> 12) & 0xF
            merge0 = False
            merge1 = False
            merge2 = False
            merge0, b1, b0 = Puzzle2048.__merge(row, b1, b0)
            merge1, b2, b1 = Puzzle2048.__merge(row, b2, b1)
            merge2, b3, b2 = Puzzle2048.__merge(row, b3, b2)
            merge0, b1, b0 = (True, b1, b0) if merge0 or merge1 else Puzzle2048.__merge(row, b1, b0)
            merge1, b2, b1 = (True, b2, b1) if merge1 or merge2 else Puzzle2048.__merge(row, b2, b1)
            merge0, b1, b0 = (True, b1, b0) if merge0 or merge1 else Puzzle2048.__merge(row, b1, b0)
            new_row = ((b3 & 0xF) << 12) | ((b2 & 0xF) << 8) | ((b1 & 0xF) << 4) | ((b0 & 0xF) << 0)
            Puzzle2048.__move_left_lookup[row] = new_row
            Puzzle2048.__move_right_lookup[Puzzle2048.__reverse(row)] = Puzzle2048.__reverse(new_row)

    def place_random_tile(state):
        """Coloca un __random_value en una celda disponible."""
        available_cells = []
        for i in range(4):
            for j in range(4):
                cell = (state >> (16*i + 4*j)) & 0xF
                if cell == 0:
                    available_cells.append((i, j))
        r = random.choice(available_cells)
        offset = 16*r[0] + 4*r[1]
        state ^= ((state >> offset) & 0xF) << offset
        state |= Puzzle2048.__random_value() << offset
        return state

    # Public
    def get_score(state):
        if not Puzzle2048.can_move(state):
            return -99999999
        ret1 = 0
        ret2 = 0
        ret3 = 0
        ret0 = 0
        for i in range(16):
            val = (state >> (4*i)) & 0xF
            if val == 0:
                ret0 += 10000
            else:
                # ret1 += (1 << val)*(1 << h1[i])
                # ret2 += (1 << val)*(1 << h2[i])
                #ret1 += (1 << val) * (1 << Puzzle2048.__h1[i])
                #ret2 += (1 << val) * (1 << Puzzle2048.__h2[i])
                ret3 += (1 << val) * (1 << Puzzle2048.__h3[i])
        #return max(ret1, ret2) + ret0
        return ret3 + ret0

    def get_matrix(state):
        """Retorna la matriz que representa el estado."""
        m = [[0 for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                offset = 16*i + 4*j
                exponent = (state >> offset) & 0xF
                if exponent != 0:
                    m[i][j] = 2**exponent
        return m

    def print(state):
        for i in range(4):
            for j in range(4):
                cell = (state >> (16*i + 4*j)) & 0xF
                if cell == 0:
                    print('%5d' % 0, end='')
                else:
                    print('%5d' % (1 << cell), end='')
            print('')
        print('')

    def left(state):
        new_state = 0
        # por cada fila consulto la lookup table. Cada fila son 16 bits consecutivos.
        # desplazo 16 bits por la cantidad de filas, y aplico una mascara para descartar los bits que no importan
        # consulto la tabla con la fila obtenida
        # agrego el resultado en la su fila correspondiente en el nuevo estado
        score = 0
        for i in range(4):
            row = (state >> (16*i)) & 0xFFFF
            r = Puzzle2048.__move_left_lookup[row]
            score += Puzzle2048.__score_lookup[row]
            new_state |= r << (16*i)
        return new_state, score

    def right(state):
        # lo mismo que left, pero con la otra tabla
        new_state = 0
        score = 0
        for i in range(4):
            row = (state >> (16*i)) & 0xFFFF
            r = Puzzle2048.__move_right_lookup[row]
            score += Puzzle2048.__score_lookup[row]
            new_state |= r << (16*i)
        return new_state, score

    def up(state):
        # igual que left, pero hay que transponer antes y después
        tr = Puzzle2048.__transpose(state)
        new_state = 0
        score = 0
        for i in range(4):
            row = (tr >> (16*i)) & 0xFFFF
            r = Puzzle2048.__move_left_lookup[row]
            score += Puzzle2048.__score_lookup[row]
            new_state |= r << (16*i)
        return Puzzle2048.__transpose(new_state), score

    def down(state):
        # igual que right, pero hay que transponer antes y después
        tr = Puzzle2048.__transpose(state)
        new_state = 0
        score = 0
        for i in range(4):
            row = (tr >> (16*i)) & 0xFFFF
            r = Puzzle2048.__move_right_lookup[row]
            score += Puzzle2048.__score_lookup[row]
            new_state |= r << (16*i)
        return Puzzle2048.__transpose(new_state), score

    moves = [up, left, down, right]

    def can_move(state):
        return any((state != move(state)[0] for move in Puzzle2048.moves))

    def random_move(state):
        move = random.choice(Puzzle2048.moves)
        state, score = move(state)
        try:
            state = Puzzle2048.place_random_tile(state)
        except IndexError as ie:
            pass
        return state, score



def main():
    Puzzle2048.precompute_tables()
    state = 0
    state = Puzzle2048.place_random_tile(state)
    state = Puzzle2048.place_random_tile(state)
    Puzzle2048.print(state)
    print(Puzzle2048.get_matrix(state))
    total_score = 0
    while True:
        move = input()
        if move == 'w':
            state, score = Puzzle2048.up(state)
            total_score += score
        elif move == 'a':
            state, score = Puzzle2048.left(state)
            total_score += score
        elif move == 's':
            state, score = Puzzle2048.down(state)
            total_score += score
        elif move == 'd':
            state, score = Puzzle2048.right(state)
            total_score += score
        Puzzle2048.print(state)
        state = Puzzle2048.place_random_tile(state)
        Puzzle2048.print(state)
        print('total_score:', total_score)

if __name__ == '__main__':
    pass
    main()
