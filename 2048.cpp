#include <iostream>
#include <vector>
#include <cassert>
#include <iomanip>

using namespace std;

// Se almacenan solo los exponentes de los valores de cada celda,
// Se ocupa un entero de 64 bits para el estado, donde 16 bits consecutivos
// corresponden a una fila
static int move_table[1 << 16];
static int score_table[1 << 16];

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
			score_table[row] += (1 << destiny);
			return true;
		}
		return false;
	}

	// retorna un 1 (probabilidad 0.9) o un 2 (con probabilidad 0.1)
	int random_value() {
		int random = rand() % 10;
		return random == 0 ? 2 : 1;
	}
	void place_random_tile() {
		vector<pair<int, int>> empty_cells;
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				if (get(i, j) == 0) {
					empty_cells.push_back({i, j});
				}
			}
		}
		if (empty_cells.empty()) {
			cerr << "Game Over!" << endl;
			return;
		}
		int random = rand() % empty_cells.size();
		auto cell = empty_cells[random];
		set(cell.first, cell.second, random_value());
	}

	Puzzle2048 () {
		this->state = 0L;
		this->score = 0L;
		place_random_tile();
		place_random_tile();
	}
	long get_score() {
		return this->score;
	}
	uint64_t get_state() {
		return this->state;
	}
	bool empty(int i, int j) {
		return get(i, j) == 0;
	}
	uint64_t get(int i, int j) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		return this->state >> offset & mask;
	}

	void set(int i, int j, uint64_t value) {
		// assert(0 <= i and i < 4 and 0 <= j and j < 4 and 0 <= value and value < 16);
		int offset = 16*i + 4*j;
		uint64_t mask = 0xF;
		this->state &= ~(mask << offset); // seteo a cero los bits donde quiero colcar el nuevo valor
		this->state |= value << offset; // coloco el nuevo valor
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
			move_table[row] = ((b3 & 0xF) << 12) | ((b2 & 0xF) << 8) | ((b1 & 0xF) << 4) | ((b0 & 0xF) << 0);
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
	bool merge(int i1, int j1, int i2, int j2) {
		int v1 = get(i1, j1);
		int v2 = get(i2, j2);
		if (v1 == 0) {
			set(i1, j1, v2);
			set(i2, j2, 0);
			return false;
		}
		else if (v1 == v2) {
			set(i1, j1, v1 + 1);
			score += (2 << (v1 + 1));
			// cout << "score +" << (1 << (v1 + 1)) << endl;
			set(i2, j2, 0);
			return true;
		}
		return false;
	}
	// combino las celdas eligiendo los pares de manera similar que se eligen
	// en bubble-sort
	// los booleanos me indican si ya mezcle algunas celdas, asi no
	// las combino de nuevo
	bool move_left() {
		// cout << "left" << endl;
		uint64_t prev_state = this->state;
		bool merge0, merge1, merge2;
		for (int row = 0; row < 4; row++) {
			merge0 = merge1 = merge2 = false;
			merge0 = merge(row, 0, row, 1);
			merge1 = merge(row, 1, row, 2);
			merge2 = merge(row, 2, row, 3);
			merge0 = merge0 or merge1 ? true : merge(row, 0, row, 1);
			merge1 = merge1 or merge2 ? true : merge(row, 1, row, 2);
			merge0 = merge0 or merge1 ? true : merge(row, 0, row, 1);
		}
		// print();
		// printf("%016lx\n", prev_state);
		// printf("%016lx\n", this->state);
		if (prev_state != this->state) {
			place_random_tile();
			// print();
			return true;
		}
		return false;
	}

	bool move_right() {
		// cout << "right" << endl;
		uint64_t prev_state = this->state;
		bool merge0, merge1, merge2;
		for (int row = 0; row < 4; row++) {
			merge0 = merge1 = merge2 = false;
			merge0 = merge(row, 3, row, 2);
			merge1 = merge(row, 2, row, 1);
			merge2 = merge(row, 1, row, 0);
			merge0 = merge0 or merge1 ? true : merge(row, 3, row, 2);
			merge1 = merge1 or merge2 ? true : merge(row, 2, row, 1);
			merge0 = merge0 or merge1 ? true : merge(row, 3, row, 2);
		}
		// print();
		// printf("%016lx\n", prev_state);
		// printf("%016lx\n", this->state);
		if (prev_state != this->state) {
			place_random_tile();
			// print();
			return true;
		}
		return false;
	}

	bool move_up() {
		// cout << "up" << endl;
		uint64_t prev_state = this->state;
		bool merge0, merge1, merge2;
		for (int col = 0; col < 4; col++) {
			merge0 = merge1 = merge2 = false;
			merge0 = merge(0, col, 1, col);
			merge1 = merge(1, col, 2, col);
			merge2 = merge(2, col, 3, col);
			merge0 = merge0 or merge1 ? true : merge(0, col, 1, col);
			merge1 = merge1 or merge2 ? true : merge(1, col, 2, col);
			merge0 = merge0 or merge1 ? true : merge(0, col, 1, col);
		}
		// print();
		// printf("%016lx\n", prev_state);
		// printf("%016lx\n", this->state);
		if (prev_state != this->state) {
			place_random_tile();
			// print();
			return true;
		}
		return false;
	}

	bool move_down() {
		// cout << "down" << endl;
		uint64_t prev_state = this->state;
		bool merge0, merge1, merge2;
		for (int col = 0; col < 4; col++) {
			merge0 = merge1 = merge2 = false;
			merge0 = merge(3, col, 2, col);
			merge1 = merge(2, col, 1, col);
			merge2 = merge(1, col, 0, col);
			merge0 = merge0 or merge1 ? true : merge(3, col, 2, col);
			merge1 = merge1 or merge2 ? true : merge(2, col, 1, col);
			merge0 = merge0 or merge1 ? true : merge(3, col, 2, col);
		}
		// print();
		// printf("%016lx\n", prev_state);
		// printf("%016lx\n", this->state);
		if (prev_state != this->state) {
			place_random_tile();
			// print();
			return true;
		}
		return false;
	}
	bool random_move() {
		int r = rand() % 4;
		if (r == 0) {
			return move_up();
		}
		else if (r == 1) {
			return move_left();
		}
		else if (r == 2) {
			return move_down();
		}
		else if (r == 3) {
			return move_right();
		}
		else {
			return false;
		}
	}
	bool can_move() {
		Puzzle2048 u = *this;
		Puzzle2048 l = *this;
		Puzzle2048 d = *this;
		Puzzle2048 r = *this;
		u.move_up();
		l.move_left();
		d.move_down();
		r.move_right();
		return !(state == u.get_state() and state == l.get_state() and state == d.get_state() and state == r.get_state());
	}
};

long simulate(Puzzle2048& p, int iterations) {
	Puzzle2048 p2 = p;
	int i = 0;
	bool ret = true;
	do {
		i++;
		ret = p2.random_move();
	} while (i < iterations and ret);
	// cout << p2.get_score() << endl;
	return p2.get_score();
}

long simulate2(Puzzle2048& p) {
	Puzzle2048 p2 = p;
	while(p2.can_move()) {
		p2.random_move();
	}
	return p2.get_score();
}

void pure_mcts(Puzzle2048& p, int simulations) {
	Puzzle2048 pu = p;
	Puzzle2048 pl = p;
	Puzzle2048 pd = p;
	Puzzle2048 pr = p;
	pu.move_up();
	pl.move_left();
	pd.move_down();
	pr.move_right();
	long ansu = 0;
	long ansl = 0;
	long ansd = 0;
	long ansr = 0;
	for (int i = 0; i < simulations; i++) {
		ansu += simulate2(pu);
		ansl += simulate2(pl);
		ansd += simulate2(pd);
		ansr += simulate2(pr);
	}
	cout << "u: " << ansu << endl;
	cout << "l: " << ansl << endl;
	cout << "d: " << ansd << endl;
	cout << "r: " << ansr << endl;
	long max = std::max(std::max(ansu, ansl), std::max(ansd, ansr));
	cout << "best score: " << max << endl;
	if (max == ansu) {
		cout << "UP" << endl;
		p.move_up();
	}
	else if (max == ansl) {
		cout << "LEFT" << endl;
		p.move_left();
	}
	else if (max == ansd) {
		cout << "DOWN" << endl;
		p.move_down();
	}
	else if (max == ansr) {
		cout << "RIGHT" << endl;
		p.move_right();
	}
}

int main(int argc, char const *argv[]) {
	srand(time(0L));
	Puzzle2048 p;
	// simulate(p, 1000);
	Puzzle2048::precompute_tables();
	p.print();
	// for (int i = 0; p.can_move(); i++) {
	// 	pure_mcts(p, 1000);
	// 	cout << "current score: " << p.get_score() << endl;
	// 	p.print();
	// }
	// cout << "GAME OVER!" << endl;

	return 0;
}
