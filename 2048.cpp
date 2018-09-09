#include <iostream>
#include <vector>
#include <cassert>
#include <iomanip>
#include <string>
#include <unordered_map>

#define INF 99999999

using namespace std;

// Se almacenan solo los exponentes de los valores de cada celda,
// Se ocupa un entero de 64 bits para el estado, donde 16 bits consecutivos
// corresponden a una fila

typedef uint64_t (*Move)(uint64_t);

static int l_lookup[1 << 16];
static int r_lookup[1 << 16];
static int score_lookup[1 << 16];

class Game2048 {
private:

	// retorna un 1 (probabilidad 0.9) o un 2 (con probabilidad 0.1)
	static int random_value() {
		int random = rand() % 10;
		return random == 0 ? 2 : 1;
	}

	static int reverse(int word) {
		// printf("%04lx\n", word);
		int b0 = (word >> 0) & 0xF;
		int b1 = (word >> 4) & 0xF;
		int b2 = (word >> 8) & 0xF;
		int b3 = (word >> 12) & 0xF;
		int ret = (b0 << 12) | (b1 << 8) | (b2 << 4) | (b3 << 0);
		// printf("%04lx\n", ret);
		return ret;
	}

	static bool merge(int row, int& source, int& destiny) {
		if (destiny == 0) {
			destiny = source;
			source = 0;
			return false;
		}
		else if (source == destiny) {
			destiny += 1;
			source = 0;
			score_lookup[row] += (1 << destiny);
			return true;
		}
		return false;
	}

public:
	long score;
	static Move moves[4];
	// static Move moves[4] = {, &Game2048::left, &Game2048::down, &Game2048::right};

	static uint64_t place_random_tile(uint64_t state) {
		vector<pair<int, int>> empty_cells;
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				if (get(state, i, j) == 0) {
					empty_cells.push_back({i, j});
				}
			}
		}
		if (empty_cells.empty()) {
			return state;
		}
		int random = rand() % empty_cells.size();
		auto cell = empty_cells[random];
		return set(state, cell.first, cell.second, random_value());
	}

	Game2048 () {
		// this->state = 0L;
		// this->score = 0L;
		// this->state = place_random_tile(this->state);
		// this->state = place_random_tile(this->state);
	}
	static long get_score(uint64_t state) {
		long ret = 0;
		int i = 1;
		for (uint64_t st = state; st != 0; st >>= 4) {
			int exp = st & 0xF;
			// con esta funcion de evaluacion llego hasta 4096
			// ret += exp >= 3 ? (1 << exp) : 0;
			// ret += exp >= 4 ? exp*(1 << exp) : 0;
			// ret += exp >= 2 ? (1 << exp)*(1 << exp) : 0;
			// ret += 1 << (exp + i);
			ret += exp == 0 ? 100000 : 0;
			i++;
		}
		// for (int i = 0; i < 4; i++) {
		// 	bool test1 = true;
		// 	bool test2 = true;
		// 	for (int j = 0; j < 3; j++) {
		// 		int diff1 = Game2048::get(state, i, j + 1) - Game2048::get(state, i, j);
		// 		int diff2 = Game2048::get(state, i, j) - Game2048::get(state, i, j + 1);
		// 		test1 &= diff1 == 1 or diff1 == 0;
		// 		test2 &= diff2 == 1 or diff2 == 0;
		// 		if (!test1 and !test2) {
		// 			break;
		// 		}
		// 	}
		// 	if (test1 or test2) {
		// 		ret += 1000;
		// 	}
		// }
		// for (int j = 0; j < 4; j++) {
		// 	bool test1 = true;
		// 	bool test2 = true;
		// 	for (int i = 0; i < 3; i++) {
		// 		int diff1 = Game2048::get(state, i + 1, j) - Game2048::get(state, i, j);
		// 		int diff2 = Game2048::get(state, i, j) - Game2048::get(state, i + 1, j);
		// 		test1 &= diff1 == 1 or diff1 == 0;
		// 		test2 &= diff2 == 1 or diff2 == 0;
		// 		if (!test1 and !test2) {
		// 			break;
		// 		}
		// 	}
		// 	if (test1 or test2) {
		// 		ret += 1000;
		// 	}
		// }
		// ret += 100*(1 << ((state >> 0) & 0xF));
		// ret += 100*(1 << ((state >> 12) & 0xF));
		// ret += 100*(1 << ((state >> 48) & 0xF));
		// ret += 100*(1 << ((state >> 60) & 0xF));
		static int h1[] = {15, 14, 13, 12, 8, 9, 10, 11, 7, 6, 5, 4, 0, 1, 2, 3};
		static int h2[] = {15, 8, 7, 0, 14, 9, 6, 1, 13, 10, 5, 2, 12, 11, 4, 3};
		long ret1 = 0;
		long ret2 = 0;
		for (int i = 0; i < 16; i++) {
			int val = (state >> (4*i)) & 0xF;
			ret1 += val*(1 << h1[i]);
			ret2 += val*(1 << h2[i]);
		}
		return max(ret1, ret2) + ret / 1000;
		return max(ret1, ret2);
		// return rett;
		return ret1 + ret;
		// return ret;
		// return this->score;
	}
	static uint64_t get(uint64_t state, int i, int j) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		return state >> offset & mask;
	}

	static uint64_t set(uint64_t state, int i, int j, uint64_t value) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4 and 0 <= value and value < 16);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		state &= ~(mask << offset); // seteo a cero los bits donde quiero colcar el nuevo valor
		state |= value << offset; // coloco el nuevo valor
		return state;
	}

	// combino las celdas eligiendo los pares de manera similar que se eligen
	// en bubble-sort
	// los booleanos me indican si ya mezcle algunas celdas, asi no
	// las combino de nuevo
	static void precompute_tables() {
		for (int row = 0; row < (1 << 16); row++) {
			int b0 = (row >> 0) & 0xF;
			int b1 = (row >> 4) & 0xF;
			int b2 = (row >> 8) & 0xF;
			int b3 = (row >> 12) & 0xF;
			bool merge0, merge1, merge2;
			merge0 = merge1 = merge2 = false;
			merge0 = Game2048::merge(row, b1, b0);
			merge1 = Game2048::merge(row, b2, b1);
			merge2 = Game2048::merge(row, b3, b2);
			merge0 = merge0 or merge1 ? true : Game2048::merge(row, b1, b0);
			merge1 = merge1 or merge2 ? true : Game2048::merge(row, b2, b1);
			merge0 = merge0 or merge1 ? true : Game2048::merge(row, b1, b0);
			int new_row = ((b3 & 0xF) << 12) | ((b2 & 0xF) << 8) | ((b1 & 0xF) << 4) | ((b0 & 0xF) << 0);
			l_lookup[row] = new_row;
			r_lookup[Game2048::reverse(row)] = reverse(new_row);
		}
	}

	static void print(uint64_t state) {
		// printf("%016lx\n", state);
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				uint64_t cell = state & 0xF;
				// cout << setw(5) << cell << " ";
				cout << setw(5) << (cell == 0 ? 0 : (1 << cell)) << " ";
				state >>= 4;
			}
			cout << endl;
		}
		cout << endl;
	}

	static uint64_t left(uint64_t state) {
		// cout << "left" << endl;
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (state >> (16*i)) & 0xFFFF;
			uint64_t r = l_lookup[row];
			new_state |= r << (16*i);
		}
		return new_state;
	}

	static uint64_t right(uint64_t state) {
		// cout << "right" << endl;
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (state >> (16*i)) & 0xFFFF;
			uint64_t r = r_lookup[row];
			new_state |= r << (16*i);
		}
		return new_state;
	}

	static uint64_t transpose(uint64_t state) {
		uint64_t new_state = 0L;
		// printf("! %016lx\n", state);
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				new_state |= ((state >> 16*i + 4*j) & 0xF) << (16*j + 4*i);
				// printf("%016lx\n", new_state);
			}
		}
		// printf("! %016lx\n", new_state);
		return new_state;
	}

	static uint64_t up(uint64_t state) {
		uint64_t tr = transpose(state);
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (tr >> (16*i)) & 0xFFFF;
			uint64_t r = l_lookup[row];
			new_state |= r << (16*i);
			// printf("up: %016lx\n", new_state);
		}
		return transpose(new_state);
	}

	static uint64_t down(uint64_t state) {
		// cout << "down" << endl;
		uint64_t tr = transpose(state);
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (tr >> (16*i)) & 0xFFFF;
			uint64_t r = r_lookup[row];
			new_state |= r << (16*i);
		}
		return transpose(new_state);
	}

	static uint64_t random_move(uint64_t state) {
		int r = rand() % 4;
		if (r == 0) {
			return Game2048::up(state);
		}
		else if (r == 1) {
			return Game2048::left(state);
		}
		else if (r == 2) {
			return Game2048::down(state);
		}
		else {
			return Game2048::right(state);
		}
	}

	static bool can_move(uint64_t state) {
		return state != up(state) or state != left(state) or state != down(state) or state != right(state);
	}
};

// uint64_t (Game2048::*Game2048::moves[])(uint64_t) = {Game2048::up};
Move Game2048::moves[] = {&Game2048::up, &Game2048::left, &Game2048::down, &Game2048::right};

long simulate(uint64_t state, int iterations) {
	// descomentar para limitar la profundidad
	// for (int i = 0; p2.can_move() and i < iterations; i++) {
	for (int i = 0; Game2048::can_move(state); i++) {
		state = Game2048::random_move(state);
		state = Game2048::place_random_tile(state);
	}
	return Game2048::get_score(state);
}

static string move_name[] = {"UP", "LEFT", "DOWN", "RIGHT"};

uint64_t pure_mcts(uint64_t state, int simulations, int iterations) {
	double best_avg_score = -1.0;
	int best_move = -1;
	uint64_t best_state = 0;
	for (int i = 0; i < 4; i++) {
		auto move = Game2048::moves[i];
		uint64_t new_state = move(state);
		long total_score = 0;
		if (new_state != state) {
			for (int j = 0; j < simulations; j++) {
				uint64_t aux_state = Game2048::place_random_tile(new_state);
				total_score += simulate(aux_state, iterations);
			}
		}
		double avg_score = double(total_score) / simulations;
		// cout << move_name[i] << ": " << avg_score << endl;
		if (avg_score > best_avg_score) {
			best_avg_score = avg_score;
			best_move = i;
			best_state = new_state;
		}
	}
	// cout << move_name[best_move] << ": " << best_avg_score << endl;
	uint64_t ret = Game2048::place_random_tile(best_state);
	return ret;
}

// unordered_map<uint64_t, long> score_cache;
double choice(uint64_t state, int depth);

double chance(uint64_t state, int depth) {
	// if (score_cache.find(state) != score_cache.end()) {
	// 	// cout << "Resultado en cache" << endl;
	// 	return score_cache[state];
	// }
	double expected_score = 0.0;
	int total_weight = 0;
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			if (Game2048::get(state, i, j) == 0) {
				total_weight += 1; // 0.9 + 0.1
				// cout << "depth: " << depth << ", probando 2 en posicion " << i << " " << j << endl;
				 // no olividar que lo guardo como exponente
				uint64_t state2 = Game2048::set(state, i, j, 1);
				// cout << "depth: " << depth << ", probando 4 en posicion " << i << " " << j << endl;
				uint64_t state4 = Game2048::set(state, i, j, 2);
				double score2 = choice(state2, depth - 1);
				double score4 = choice(state4, depth - 1);
				expected_score += 0.9 * score2;
				expected_score += 0.1 * score4;
			}
		}
	}
	return total_weight == 0 ? 0 : expected_score / total_weight;
}


double choice(uint64_t state, int depth) {
	// if (score_cache.find(state) != score_cache.end()) {
	// 	// cout << "Resultado en cache" << endl;
	// 	return score_cache[state];
	// }
	if (depth <= 0) {
		long total_score = 0;
		// int sims = 100;
		// for (size_t i = 0; i < sims; i++) {
		// 	total_score += simulate(state, INF);
		// 	return Game2048::get_score(state) / double(sims);
		// }
		double score = Game2048::get_score(state);
		// score_cache[state] = score;
		return score;
	}
	double best_score = -1.0;
	for (int i = 0; i < 4; i++) {
		// cout << "depth: " << depth << ", probando movimiento " << i << endl;
		auto move = Game2048::moves[i];
		uint64_t new_state = move(state);
		double score = chance(new_state, depth);
		if (score > best_score) {
			best_score = score;
		}
	}
	return best_score;
}

uint64_t expectimax(uint64_t state, int depth) {
	uint64_t best_state = 0;
	double best_score = -1.0;
	int best_move = -1;
	for (int i = 0; i < 4; i++) {
		auto move = Game2048::moves[i];
		uint64_t new_state = move(state);
		if (new_state != state) {
			double score = chance(new_state, depth - 1);
			if (score > best_score) {
				best_score = score;
				best_move = i;
				best_state = new_state;
			}
		}
	}
	cout << move_name[best_move] << endl;
	return Game2048::place_random_tile(best_state);
}

int main(int argc, char const *argv[]) {
	srand(time(0L));
	Game2048::precompute_tables();
	uint64_t state = 0L;
	state = Game2048::place_random_tile(state);
	state = Game2048::place_random_tile(state);
	Game2048::print(state);
	clock_t ti = clock();
	int i;
	int simulations = 1000;
	for (int i = 0; Game2048::can_move(state); i++) {
		state = expectimax(state, 5);
		Game2048::print(state);
	}
	// for (i = 0; Game2048::can_move(state); i++) {
	// 	// cout << "simulations: " << i << endl;
	// 	state = pure_mcts(state, simulations, INF);
	// 	// cout << "current score: " << Game2048::get_score(state) << endl;
	// 	Game2048::print(state);
	// }
	clock_t tf = clock();
	// while (true) {
	// 	char c;
	// 	cin >> c;
	// 	if (c == 'w') {
	// 		state = Game2048::up(state);
	// 	}
	// 	else if (c == 'a') {
	// 		state = Game2048::left(state);
	// 	}
	// 	else if (c == 's') {
	// 		state = Game2048::down(state);
	// 	}
	// 	else if (c == 'd') {
	// 		state = Game2048::right(state);
	// 	}
	// 	Game2048::print(state);
	// 	state = Game2048::place_random_tile(state);
	// 	Game2048::print(state);
	//
	// }
	cout << "GAME OVER!" << endl;
	cout << double(tf - ti) / i << " moves per second" << endl;
	cout << simulations*(double(tf - ti) / i) << " simulations per second" << endl;
	return 0;
}
