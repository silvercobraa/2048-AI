from puzzle2048 import Puzzle2048

class AI(object):
    EXPECTIMAX_DEPTH = 5
    INF = 99999999

    """docstring for AI."""
    def __init__(self, arg):
        super(AI, self).__init__()
        self.arg = arg

    def __chance(state, depth):
        if depth == 0:
            return Puzzle2048.get_score(state)
        expected_score = 0.0
        total_weight = 0
        for i in range(4):
            for j in range(4):
                offset = 16*i + 4*j
                cell = (state >> offset) & 0xF
                if cell == 0:
                    total_weight += 1 # 0.9 + 0.1
                    state2 = state
                    state4 = state
                    state2 ^= ((state >> offset) & 0xF) << offset
                    # state4 ^= ((state >> offset) & 0xF) << offset
                    state2 ^= 1 << offset
                    # state4 ^= 2 << offset
                    score2 = AI.__choice(state2, depth - 1)
                    # score4 = AI.__choice(state4, depth - 1)
                    expected_score += 1 * score2
                    expected_score += 0.9 * score2
                    # expected_score += 0.1 * score4
        return 0 if total_weight == 0 else expected_score / total_weight


    def __choice(state, depth):
        if depth <= 0:
            score = Puzzle2048.get_score(state)
            return score
        best_score = -AI.INF
        for move in Puzzle2048.moves:
            new_state, score = move(state)
            if new_state != state:
                score = AI.__chance(new_state, depth - 1)
                if score >= best_score:
                    best_score = score
        return best_score

    def expectimax(state, depth=EXPECTIMAX_DEPTH):
        best_state = 0
        best_score = -AI.INF
        moves = []
        game_score = 0
        for move in Puzzle2048.moves:
            new_state, sc = move(state)
            score = 0.0
            if new_state != state:
                moves.append(move)
                score = AI.__chance(new_state, depth)
                if score > best_score:
                    best_score = score
                    best_state = new_state
                    game_score = sc
        print(best_score)
        assert(best_state != 0)
        # print(move_name[best_move])
        return Puzzle2048.place_random_tile(best_state), game_score

    def __simulate(state):
        score = 0
        while Puzzle2048.can_move(state):
            new_state, sc = Puzzle2048.random_move(state)
            if new_state != state:
                state = Puzzle2048.place_random_tile(new_state)
                score += sc
        return state, score

    def __simulations(state, simulations):
        branch_score = 0
        for i in range(simulations):
            sim_state, sim_score = AI.__simulate(state)
            branch_score += sim_score
        return branch_score

    def pure_mcts(state, simulations):
        best_score = -AI.INF
        ans = (state, 0)
        for move in Puzzle2048.moves:
            new_state, sc = move(state)
            if new_state != state:
                new_state = Puzzle2048.place_random_tile(new_state)
                branch_score = AI.__simulations(new_state, simulations)
                if branch_score > best_score:
                    best_score = branch_score
                    ans = (new_state, sc)
        return ans



def main():
    Puzzle2048.precompute_tables()
    state = 0
    state = Puzzle2048.place_random_tile(state)
    state = Puzzle2048.place_random_tile(state)
    Puzzle2048.print(state)
    while Puzzle2048.can_move(state):
        state = AI.expectimax(state)
        Puzzle2048.print(state)


if __name__ == '__main__':
    main()
