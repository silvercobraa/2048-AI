#include <iostream>
#include <vector>
#include <cassert>
#include <iomanip>

#define INF 99999999

using namespace std;

// Se almacenan solo los exponentes de los valores de cada celda,
// Se ocupa un entero de 64 bits para el estado, donde 16 bits consecutivos
// corresponden a una fila

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
	// typedef uint64_t (Game2048::*MoveFunction)();
	// static MoveFunction moves[4] = {Game2048::up, Game2048::left, Game2048::down, Game2048::right};

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
			ret += exp >= 3 ? (1 << exp) : 0;
			// ret += exp >= 4 ? exp*(1 << exp) : 0;
			// ret += exp >= 2 ? (1 << exp)*(1 << exp) : 0;
			// ret += 1 << (exp + i);
			i++;
		}
		return ret;
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


long simulate(uint64_t state, int iterations) {
	// descomentar para limitar la profundidad
	// for (int i = 0; p2.can_move() and i < iterations; i++) {
	for (int i = 0; Game2048::can_move(state); i++) {
		state = Game2048::random_move(state);
		state = Game2048::place_random_tile(state);
	}
	return Game2048::get_score(state);
}

uint64_t pure_mcts(uint64_t state, int simulations, int iterations) {
	uint64_t u = state;
	uint64_t l = state;
	uint64_t d = state;
	uint64_t r = state;
	u = Game2048::up(state);
	l = Game2048::left(state);
	d = Game2048::down(state);
	r = Game2048::right(state);
	long ansu = 0;
	long ansl = 0;
	long ansd = 0;
	long ansr = 0;
	for (int i = 0; i < simulations; i++) {
		if (u != state) {
			u = Game2048::place_random_tile(u);
			ansu += simulate(u, iterations);
		}
		if (l != state) {
			l = Game2048::place_random_tile(l);
			ansl += simulate(l, iterations);
		}
		if (d != state) {
			d = Game2048::place_random_tile(d);
			ansd += simulate(d, iterations);
		}
		if (r != state) {
			r = Game2048::place_random_tile(r);
			ansr += simulate(r, iterations);
		}
	}
	cout << "u: " << ansu << endl;
	cout << "l: " << ansl << endl;
	cout << "d: " << ansd << endl;
	cout << "r: " << ansr << endl;
	long max = std::max(std::max(ansu, ansl), std::max(ansd, ansr));
	cout << "best score: " << max << endl;
	if (max == ansu) {
		cout << "UP" << endl;
		state = Game2048::up(state);
	}
	else if (max == ansl) {
		cout << "LEFT" << endl;
		state = Game2048::left(state);
	}
	else if (max == ansd) {
		cout << "DOWN" << endl;
		state = Game2048::down(state);
	}
	else if (max == ansr) {
		cout << "RIGHT" << endl;
		state = Game2048::right(state);
	}
	return Game2048::place_random_tile(state);
}


int main(int argc, char const *argv[]) {
	srand(time(0L));
	Game2048::precompute_tables();

	uint64_t state = 0L;
	state = Game2048::place_random_tile(state);
	state = Game2048::place_random_tile(state);
	Game2048::print(state);
	for (int i = 0; Game2048::can_move(state); i++) {
		cout << "simulations: " << i << endl;
		state = pure_mcts(state, 1000, INF);
		cout << "current score: " << Game2048::get_score(state) << endl;
		Game2048::print(state);
	}
	cout << "GAME OVER!" << endl;

	return 0;
}
