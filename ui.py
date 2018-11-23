#!/usr/bin/python
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
import random
import sys
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
		print('STOP')
		self._mutex.lock()
		self._stopped = True
		self._mutex.unlock()

	def toggle(self):
		self._mutex.lock()
		self._stopped = not self._stopped
		if self._stopped:
			print('STOP')
		else:
			print('START')
		self._mutex.unlock()

	def run(self):
		while True:
			if not self._stopped:
				self.parent.mutex.lock()
				self.parent.auto_play()
				self.parent.mutex.unlock()
		# self.data.emit(data)

class Game2048(QWidget):
	def __init__(self,parent, width=800, height=800, ai=AI('expectimax')):
		QWidget.__init__(self,parent)
		self.panelHeight=80
		self.backgroundBrush=QtGui.QBrush(QtGui.QColor(0x272822))
		self.tileMargin=16
		self.gridOffsetX=self.tileMargin
		self.gridOffsetY=self.panelHeight+self.tileMargin
		self.resize(width, height)
		# powers = [2**i for i in range(16)]
		# powers.append(0)
		# print(powers)
		# self.brushes = {
		# 	i: QtGui.QBrush(QtGui.QColor(random.randint(0, 2**24)))
		# 	for i in powers
		# }
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
		}
		self.lightPen=QtGui.QPen(QtGui.QColor(0xeff0f1))
		self.scoreRect=QtCore.QRect(10,10,80,self.panelHeight-20)
		self.hiScoreRect=QtCore.QRect(100,10,80,self.panelHeight-20)
		self.resetRect=QtCore.QRectF(190,10,80,self.panelHeight-20)
		self.scoreLabel=QtCore.QRectF(10,25,80,self.panelHeight-30)
		self.hiScoreLabel=QtCore.QRectF(100,25,80,self.panelHeight-30)
		self.high_score=0
		self.score=0
		self.ai = ai
		# self.resize(QtCore.QSize(self.width, self.width + self.panelHeight))
		self.reset_game()
		qmb = QMessageBox.question(self, 'Instrucciones', 'Utilice las teclas direccionales para mover las baldosas.', QMessageBox.Ok)


		self._worker = Worker(self)
		self._worker.start()
		self.mutex = QtCore.QMutex()
		# self.timer = QtCore.QTimer()
		# self.timer.setSingleShot(True)
		# self.timer.timeout.connect(self.hola)
		# self.timer.start(1000)

	def resizeEvent(self,e):
		width=min(e.size().width(),e.size().height()-self.panelHeight)
		self.tileSize=(width-self.tileMargin*(4+1)) / 4
		self.font=QtGui.QFont('Inconsolata',self.tileSize / 4)

	def changeGridSize(self,x):
		self.gridSize=x
		self.reset_game()

	def reset_game(self):
		self.puzzle = 0
		self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
		self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
		self.high_score = max(self.high_score, self.score)
		self.score = 0
		self.update()

	def play(self, move):
		new_state, score = move(self.puzzle)
		if new_state != self.puzzle:
			self.puzzle = new_state
			self.puzzle = Puzzle2048.place_random_tile(self.puzzle)
			self.score += score
			self.update()
			if not Puzzle2048.can_move(self.puzzle):
				self.game_over()

	def auto_play(self):
		if Puzzle2048.can_move(self.puzzle):
			print(hex(self.puzzle))
			self.puzzle, score = self.ai.play(self.puzzle)
			print(hex(self.puzzle))
			print('score: ', self.score)
			self.score += score
			self.update()
		else:
			self.game_over()

	def game_over(self):
		self._worker.stop()
		qmb = QMessageBox.question(self, 'RIP', 'GAME OVER! Quiere seguir jugando?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if qmb == QMessageBox.Yes:
			print('RESETEANDO...')
			self.reset_game()
		else:
			sys.exit(0)

	def keyPressEvent(self,e):
		if e.key()==QtCore.Qt.Key_Escape:
			self._worker.stop()
			self.reset_game()
		elif e.key()==QtCore.Qt.Key_Up:
			self.play(Puzzle2048.up)
		elif e.key()==QtCore.Qt.Key_Down:
			self.play(Puzzle2048.down)
		elif e.key()==QtCore.Qt.Key_Left:
			self.play(Puzzle2048.left)
		elif e.key()==QtCore.Qt.Key_Right:
			self.play(Puzzle2048.right)
		elif e.key()==QtCore.Qt.Key_Space:
			self._worker.toggle()
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
		painter.setFont(QtGui.QFont('Inconsolata',9))
		painter.setPen(self.lightPen)
		painter.drawText(QtCore.QRectF(10,15,80,20),'SCORE',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.drawText(QtCore.QRectF(100,15,80,20),'HIGHSCORE',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.setFont(QtGui.QFont('Inconsolata',15))
		painter.drawText(self.resetRect,'RESET',QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.drawText(self.scoreLabel,str(self.score),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.drawText(self.hiScoreLabel,str(self.high_score),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
		painter.setFont(self.font)
		matrix = Puzzle2048.get_matrix(self.puzzle)
		for i, row in enumerate(matrix):
			for j, col in enumerate(row):
				if col == 0:
					painter.setBrush(self.brushes[0])
				else:
					painter.setBrush(self.brushes[col])
				rect=QtCore.QRectF(self.gridOffsetX+j*(self.tileSize+self.tileMargin),
										self.gridOffsetY+i*(self.tileSize+self.tileMargin),
										self.tileSize,self.tileSize)
				painter.setPen(QtCore.Qt.NoPen)
				painter.drawRoundedRect(rect,10.0,10.0)
				if col != 0:
					painter.setPen(self.lightPen)
					painter.drawText(rect,str(col),QtGui.QTextOption(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter))
