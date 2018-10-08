#!/usr/bin/python
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
import random
from puzzle2048 import Puzzle2048
from ai import AI

class Worker(QtCore.QThread):
	data = QtCore.pyqtSignal(dict)

	def __init__(self, parent=None):
		super(Worker, self).__init__(parent)
		self._stopped = True
		self._mutex = QtCore.QMutex()
		self.parent = parent

	def stop(self):
		self._mutex.lock()
		self._stopped = True
		self._mutex.unlock()

	def run(self):
		# qmb = QMessageBox.question(None, 'Test', 'Test 2', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		# qmb.show()

		while Puzzle2048.can_move(self.parent.puzzle):
			self.parent.auto_play()
		# self.data.emit(data)
		print('GAME OVER!!!')

class Game2048(QWidget):
	def __init__(self,parent,width=340,gridSize=4):
		QWidget.__init__(self,parent)
		self.gameRunning=False
		self.panelHeight=80
		self.backgroundBrush=QtGui.QBrush(QtGui.QColor(0x272822))
		self.gridSize=gridSize
		self.tileMargin=16
		self.gridOffsetX=self.tileMargin
		self.gridOffsetY=self.panelHeight+self.tileMargin
		self.brushes={
			0:QtGui.QBrush(QtGui.QColor(0x323639)),
			1:QtGui.QBrush(QtGui.QColor(0x67001f)),
			2:QtGui.QBrush(QtGui.QColor(0x8c0c25)),
			4:QtGui.QBrush(QtGui.QColor(0xb2182b)),
			8:QtGui.QBrush(QtGui.QColor(0xc43c3c)),
			16:QtGui.QBrush(QtGui.QColor(0xd6604d)),
			32:QtGui.QBrush(QtGui.QColor(0xe58267)),
			64:QtGui.QBrush(QtGui.QColor(0xf4a582)),
			128:QtGui.QBrush(QtGui.QColor(0xd7af9e)),
			256:QtGui.QBrush(QtGui.QColor(0xbababa)),
			512:QtGui.QBrush(QtGui.QColor(0xa0a0a0)),
			1024:QtGui.QBrush(QtGui.QColor(0x878787)),
			2048:QtGui.QBrush(QtGui.QColor(0x6a6a6a)),
			4096:QtGui.QBrush(QtGui.QColor(0x4d4d4d)),
			8192:QtGui.QBrush(QtGui.QColor(0x333333)),
			16384:QtGui.QBrush(QtGui.QColor(0x1a1a1a)),
			32768:QtGui.QBrush(QtGui.QColor(0x000000)),
			# 65536:QtGui.QBrush(QtGui.QColor(0x000000)),
		}
		self.lightPen=QtGui.QPen(QtGui.QColor(0xeff0f1))
		self.darkPen=QtGui.QPen(QtGui.QColor(0xeff0f1))
		self.scoreRect=QtCore.QRect(10,10,80,self.panelHeight-20)
		self.hiScoreRect=QtCore.QRect(100,10,80,self.panelHeight-20)
		self.resetRect=QtCore.QRectF(190,10,80,self.panelHeight-20)
		self.scoreLabel=QtCore.QRectF(10,25,80,self.panelHeight-30)
		self.hiScoreLabel=QtCore.QRectF(100,25,80,self.panelHeight-30)
		self.hiScore=0
		self.lastPoint=None
		self.resize(QtCore.QSize(width,width+self.panelHeight))
		self.reset_game()
		self.iterations = 0
		# while self.puzzle.can_move():
		# 	move = pure_mcts(self.puzzle, 10)
		# 	print(self.puzzle)
		# 	self.update()
		self._worker = Worker(self)
		self._worker.started.connect(self.worker_started_callback)
		self._worker.finished.connect(self.worker_finished_callback)
		self._worker.data.connect(self.worker_data_callback)
		self._worker.start()


	def worker_started_callback(self):
		pass

	def worker_finished_callback(self):
		pass

	def worker_data_callback(self, data):
		print(data['progress'])


	def resizeEvent(self,e):
		width=min(e.size().width(),e.size().height()-self.panelHeight)
		self.tileSize=(width-self.tileMargin*(self.gridSize+1))/self.gridSize
		self.font=QtGui.QFont('Arial',self.tileSize/4)

	def changeGridSize(self,x):
		self.gridSize=x
		self.reset_game()

	def reset_game(self):
		self.puzzle = 0
		self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
		self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
		self.score = 0
		self.update()
		self.gameRunning=True

	def up(self):
		print('UP')
		new_state, score = Puzzle2048.up(self.puzzle)
		if new_state != self.puzzle:
			self.puzzle = new_state
			self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
			self.score += score
			self.update()

	def down(self):
		new_state, score = Puzzle2048.down(self.puzzle)
		if new_state != self.puzzle:
			self.puzzle = new_state
			self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
			self.score += score
			self.update()

	def left(self):
		Puzzle2048.print(self.puzzle)
		new_state, score = Puzzle2048.left(self.puzzle)
		Puzzle2048.print(new_state)
		if new_state != self.puzzle:
			self.puzzle = new_state
			self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
			self.score += score
			self.update()

	def right(self):
		new_state, score = Puzzle2048.right(self.puzzle)
		if new_state != self.puzzle:
			self.puzzle = new_state
			self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
			self.score += score
			self.update()

	def auto_play(self):
		if Puzzle2048.can_move(self.puzzle):
			self.puzzle, score = AI.expectimax(self.puzzle)
			print(hex(self.puzzle))
			# self.puzzle, score = AI.pure_mcts(self.puzzle, 100)
			print('score: ', self.score)
			self.score += score
			self.update()
		else:

			# Game over
			pass

	def keyPressEvent(self,e):
		if not self.gameRunning:
			return
		if e.key()==QtCore.Qt.Key_Escape:
			self.reset_game()
		elif e.key()==QtCore.Qt.Key_Up:
			self.up()
		elif e.key()==QtCore.Qt.Key_Down:
			self.down()
		elif e.key()==QtCore.Qt.Key_Left:
			self.left()
		elif e.key()==QtCore.Qt.Key_Right:
			self.right()
		elif e.key()==QtCore.Qt.Key_Space:
			self.auto_play()
		print(self.puzzle)

	def paintEvent(self,event):
		painter = QtGui.QPainter(self)
		painter.setPen(QtCore.Qt.NoPen)
		painter.setBrush(self.backgroundBrush)
		painter.drawRect(self.rect())
		painter.setBrush(self.brushes[1])
		painter.drawRoundedRect(self.scoreRect,10.0,10.0)
		painter.drawRoundedRect(self.hiScoreRect,10.0,10.0)
		painter.drawRoundedRect(self.resetRect,10.0,10.0)
		painter.setFont(QtGui.QFont('Arial',9))
		painter.setPen(self.darkPen)
		painter.drawText(QtCore.QRectF(10,15,80,20),'SCORE',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.drawText(QtCore.QRectF(100,15,80,20),'HIGHSCORE',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.setFont(QtGui.QFont('Arial',15))
		painter.setPen(self.lightPen)
		painter.drawText(self.resetRect,'RESET',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.setFont(QtGui.QFont('Arial',15))
		painter.setPen(self.lightPen)
		painter.drawText(self.scoreLabel,str(self.score),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.drawText(self.hiScoreLabel,str(self.hiScore),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.setFont(self.font)
		matrix = Puzzle2048.get_matrix(self.puzzle)
		print(matrix)
		for i, row in enumerate(matrix):
			for j, col in enumerate(row):
				if col == 0:
					painter.setBrush(self.brushes[0])
				else:
					# print(col)
					painter.setBrush(self.brushes[col])
				rect=QtCore.QRectF(self.gridOffsetX+j*(self.tileSize+self.tileMargin),
										self.gridOffsetY+i*(self.tileSize+self.tileMargin),
										self.tileSize,self.tileSize)
				painter.setPen(QtCore.Qt.NoPen)
				painter.drawRoundedRect(rect,10.0,10.0)
				if col != 0:
					painter.setPen(self.darkPen if col < 16 else self.lightPen)
					painter.drawText(rect,str(col),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))


if __name__=='__main__':
	Puzzle2048.precompute_tables()
	app = QApplication([])
	g = Game2048(None,340,4)
	g.move(0,0)
	#g.resize(500,400)
	g.changeGridSize(4)
	g.setWindowTitle('2048 Game')
	g.show()

app.exec_()
