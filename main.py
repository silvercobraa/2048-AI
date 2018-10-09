from PyQt5.QtWidgets import QApplication
from puzzle2048 import Puzzle2048
from ai import AI
from ui import Game2048

Puzzle2048.precompute_tables()
AI.EXPECTIMAX_DEPTH = 4
AI.MCTS_ITERATIONS = 100
AI.PURE_MCTS_SIMULATIONS = 100

ai = AI('expectimax')
# ai = AI('pure_mcts')
# ai = AI('mcts')

app = QApplication([])
window = Game2048(None,340, ai)
window.move(0,0)
window.resize(500,400)
window.changeGridSize(4)
window.setWindowTitle('2048 Game')
window.show()

app.exec_()
