#include <iostream>
#include <vector>
#include <cassert>
#include <iomanip>

using namespace std;

// Se almacenan solo los exponentes de los valores de cada celda,
// Se ocupa un entero de 64 bits para el estado, donde 16 bits consecutivos
// corresponden a una fila
static int l_lookup[1 << 16];
static int r_lookup[1 << 16];
static int score_lookup[1 << 16];

class Puzzle2048 {
private:

public:
	uint64_t state;
	long score;

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

	// retorna un 1 (probabilidad 0.9) o un 2 (con probabilidad 0.1)
	int random_value() {
		int random = rand() % 10;
		return random == 0 ? 2 : 1;
	}
	uint64_t place_random_tile(uint64_t st) {
		vector<pair<int, int>> empty_cells;
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				if (get(st, i, j) == 0) {
					empty_cells.push_back({i, j});
				}
			}
		}
		if (empty_cells.empty()) {
			return st;
		}
		int random = rand() % empty_cells.size();
		auto cell = empty_cells[random];
		return set(st, cell.first, cell.second, random_value());
	}

	Puzzle2048 () {
		this->state = 0L;
		this->score = 0L;
		this->state = place_random_tile(this->state);
		this->state = place_random_tile(this->state);
	}
	long get_score() {
		long ret = 0;
		int i = 1;
		for (uint64_t st = this->state; st != 0; st >>= 4) {
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
	uint64_t get_state() {
		return this->state;
	}

	uint64_t get(uint64_t st, int i, int j) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		return st >> offset & mask;
	}

	uint64_t set(uint64_t st, int i, int j, uint64_t value) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4 and 0 <= value and value < 16);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		st &= ~(mask << offset); // seteo a cero los bits donde quiero colcar el nuevo valor
		st |= value << offset; // coloco el nuevo valor
		return st;
	}

	static void precompute_tables() {
		for (int row = 0; row < (1 << 16); row++) {
			int b0 = (row >> 0) & 0xF;
			int b1 = (row >> 4) & 0xF;
			int b2 = (row >> 8) & 0xF;
			int b3 = (row >> 12) & 0xF;
			bool merge0, merge1, merge2;
			merge0 = merge1 = merge2 = false;
			merge0 = Puzzle2048::merge(row, b1, b0);
			merge1 = Puzzle2048::merge(row, b2, b1);
			merge2 = Puzzle2048::merge(row, b3, b2);
			merge0 = merge0 or merge1 ? true : Puzzle2048::merge(row, b1, b0);
			merge1 = merge1 or merge2 ? true : Puzzle2048::merge(row, b2, b1);
			merge0 = merge0 or merge1 ? true : Puzzle2048::merge(row, b1, b0);
			int new_row = ((b3 & 0xF) << 12) | ((b2 & 0xF) << 8) | ((b1 & 0xF) << 4) | ((b0 & 0xF) << 0);
			l_lookup[row] = new_row;
			r_lookup[Puzzle2048::reverse(row)] = reverse(new_row);
			// TODO: crear una lookup table para la fila reversa
		}
	}
	void print() {
		// printf("%016lx\n", state);
		uint64_t curr_state = this->state;
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				uint64_t cell = curr_state & 0xF;
				// cout << setw(5) << cell << " ";
				cout << setw(5) << (cell == 0 ? 0 : (1 << cell)) << " ";
				curr_state >>= 4;
			}
			cout << endl;
		}
		cout << endl;
	}
	// combino las celdas eligiendo los pares de manera similar que se eligen
	// en bubble-sort
	// los booleanos me indican si ya mezcle algunas celdas, asi no
	// las combino de nuevo
	uint64_t left() {
		// cout << "left" << endl;
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (this->state >> (16*i)) & 0xFFFF;
			uint64_t r = l_lookup[row];
			new_state |= r << (16*i);
		}
		return new_state;
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
	uint64_t right() {
		// cout << "right" << endl;
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (this->state >> (16*i)) & 0xFFFF;
			uint64_t r = r_lookup[row];
			new_state |= r << (16*i);
		}
		return new_state;
	}
	uint64_t transpose(uint64_t st) {
		// TODO: implementar esto
		uint64_t new_state = 0L;
		// printf("! %016lx\n", st);
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				new_state |= ((st >> 16*i + 4*j) & 0xF) << (16*j + 4*i);
				// printf("%016lx\n", new_state);
			}
		}
		// printf("! %016lx\n", new_state);
		return new_state;
	}
	uint64_t up() {
		uint64_t tr = transpose(this->state);
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (tr >> (16*i)) & 0xFFFF;
			uint64_t r = l_lookup[row];
			new_state |= r << (16*i);
			// printf("up: %016lx\n", new_state);
		}
		return transpose(new_state);
	}

	uint64_t down() {
		// cout << "down" << endl;
		uint64_t tr = transpose(this->state);
		uint64_t new_state = 0L;
		for (size_t i = 0; i < 4; i++) {
			int row = (tr >> (16*i)) & 0xFFFF;
			uint64_t r = r_lookup[row];
			new_state |= r << (16*i);
		}
		return transpose(new_state);
	}

	uint64_t random_move() {
		int r = rand() % 4;
		if (r == 0) {
			return up();
		}
		else if (r == 1) {
			return left();
		}
		else if (r == 2) {
			return down();
		}
		else {
			return right();
		}
	}

	bool can_move() {
		return state != up() or state != left() or state != down() or state != right();
	}
};

long simulate(Puzzle2048& p) {
	Puzzle2048 p2 = p;
	while(p2.can_move()) {
		p2.state = p2.random_move();
		p2.state = p2.place_random_tile(p2.state);
	}
	return p2.get_score();
}

void pure_mcts(Puzzle2048& p, int simulations) {
	Puzzle2048 pu = p;
	Puzzle2048 pl = p;
	Puzzle2048 pd = p;
	Puzzle2048 pr = p;
	pu.state = p.up();
	pl.state = p.left();
	pd.state = p.down();
	pr.state = p.right();
	long ansu = 0;
	long ansl = 0;
	long ansd = 0;
	long ansr = 0;
	for (int i = 0; i < simulations; i++) {
		if (pu.state != p.state) {
			pu.state = pu.place_random_tile(pu.state);
			ansu += simulate(pu);
		}
		if (pl.state != p.state) {
			pl.state = pl.place_random_tile(pl.state);
			ansl += simulate(pl);
		}
		if (pd.state != p.state) {
			pd.state = pd.place_random_tile(pd.state);
			ansd += simulate(pd);
		}
		if (pr.state != p.state) {
			pr.state = pr.place_random_tile(pr.state);
			ansr += simulate(pr);
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
		p.state = p.up();
	}
	else if (max == ansl) {
		cout << "LEFT" << endl;
		p.state = p.left();
	}
	else if (max == ansd) {
		cout << "DOWN" << endl;
		p.state = p.down();
	}
	else if (max == ansr) {
		cout << "RIGHT" << endl;
		p.state = p.right();
	}
	p.state = p.place_random_tile(p.state);
}

int main(int argc, char const *argv[]) {
	srand(time(0L));
	Puzzle2048 p;
	// simulate(p, 1000);
	Puzzle2048::precompute_tables();
	p.print();
	for (int i = 0; p.can_move(); i++) {
		pure_mcts(p, 3000);
		cout << "current score: " << p.get_score() << endl;
		p.print();
	}
	cout << "GAME OVER!" << endl;

	return 0;
}
