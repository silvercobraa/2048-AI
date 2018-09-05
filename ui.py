#!/usr/bin/python
from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
from puzzle2048 import Puzzle2048, simulate, pure_mcts

class Worker(QThread):
	def __init__(self, parent = None, game=None):
		QThread.__init__(self, parent)
		# self.exiting = False
		# self.size = QSize(0, 0)
		# self.stars = 0
		self.game = game

	def run(self):
		# Note: This is never called directly. It is called by Qt once the
		# thread environment has been set up.
		while self.game.puzzle.can_move():
			print('asdadsad')
			move = pure_mcts(self.game.puzzle, 1)
			print(self.game.puzzle)
			self.game.update()

class Game2048(QtGui.QWidget):
	def __init__(self,parent,width=340,gridSize=4):
		QtGui.QWidget.__init__(self,parent)
		self.gameRunning=False
		self.panelHeight=80
		self.backgroundBrush=QtGui.QBrush(QtGui.QColor(0xbbada0))
		self.gridSize=gridSize
		self.tileMargin=16
		self.gridOffsetX=self.tileMargin
		self.gridOffsetY=self.panelHeight+self.tileMargin
		self.brushes={
			0:QtGui.QBrush(QtGui.QColor(0xcdc1b4)),
			1:QtGui.QBrush(QtGui.QColor(0x999999)),
			2:QtGui.QBrush(QtGui.QColor(0xeee4da)),
			4:QtGui.QBrush(QtGui.QColor(0xede0c8)),
			8:QtGui.QBrush(QtGui.QColor(0xf2b179)),
			16:QtGui.QBrush(QtGui.QColor(0xf59563)),
			32:QtGui.QBrush(QtGui.QColor(0xf67c5f)),
			64:QtGui.QBrush(QtGui.QColor(0xf65e3b)),
			128:QtGui.QBrush(QtGui.QColor(0xedcf72)),
			256:QtGui.QBrush(QtGui.QColor(0xedcc61)),
			512:QtGui.QBrush(QtGui.QColor(0xedc850)),
			1024:QtGui.QBrush(QtGui.QColor(0xedc53f)),
			2048:QtGui.QBrush(QtGui.QColor(0xedc22e)),
		}
		self.lightPen=QtGui.QPen(QtGui.QColor(0xf9f6f2))
		self.darkPen=QtGui.QPen(QtGui.QColor(0x776e65))
		self.scoreRect=QtCore.QRect(10,10,80,self.panelHeight-20)
		self.hiScoreRect=QtCore.QRect(100,10,80,self.panelHeight-20)
		self.resetRect=QtCore.QRectF(190,10,80,self.panelHeight-20)
		self.scoreLabel=QtCore.QRectF(10,25,80,self.panelHeight-30)
		self.hiScoreLabel=QtCore.QRectF(100,25,80,self.panelHeight-30)
		self.hiScore=0
		self.lastPoint=None
		self.resize(QtCore.QSize(width,width+self.panelHeight))
		self.reset_game()
		self.thread = Worker(game=self)
		self.iterations = 0
		# while self.puzzle.can_move():
		# 	move = pure_mcts(self.puzzle, 10)
		# 	print(self.puzzle)
		# 	self.update()


	def resizeEvent(self,e):
		width=min(e.size().width(),e.size().height()-self.panelHeight)
		self.tileSize=(width-self.tileMargin*(self.gridSize+1))/self.gridSize
		self.font=QtGui.QFont('Arial',self.tileSize/4)

	def changeGridSize(self,x):
		self.gridSize=x
		self.reset_game()

	def reset_game(self):
		self.puzzle = Puzzle2048(initial_tiles=1)
		print(self.puzzle)
		self.score=0
		self.update()
		self.gameRunning=True

	def up(self):
		self.puzzle.move_up()
		# print(self.puzzle)
		self.score = self.puzzle.get_score()
		self.update()
		# return

	def down(self):
		self.puzzle.move_down()
		self.score = self.puzzle.get_score()
		self.update()
		# print(self.puzzle)
		# return

	def left(self):
		self.puzzle.move_left()
		self.score = self.puzzle.get_score()
		self.update()
		# print(self.puzzle)
		# return

	def right(self):
		self.puzzle.move_right()
		self.score = self.puzzle.get_score()
		self.update()
		# print(self.puzzle)
		# return


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
			# print('asdasdasd')
			# self.puzzle.random_move()
			# while self.puzzle.can_move():
			# move = pure_mcts(self.puzzle, self.score // 100)
			move = pure_mcts(self.puzzle, self.iterations // 10)
			print(move)
			self.score = self.puzzle.get_score()
			# print('score:', self.score)
			# 	print(self.puzzle)
			# 	self.update()
			self.iterations += 1
			self.update()
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
		for i, row in enumerate(self.puzzle.get_state()):
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
	app=QtGui.QApplication([])
	g = Game2048(None,340,4)
	g.move(0,0)
	#g.resize(500,400)
	g.changeGridSize(4)
	g.setWindowTitle('2048 Game')
	g.show()

app.exec_()
