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
# ai = AI('random')

app = QApplication([])
window = Game2048(None, width=520, height=600, ai=ai)
# window.changeGridSize(4)
window.setWindowTitle('2048 Game')
window.show()

app.exec_()
