#! /usr/bin/env python

import os
import sys
import random
import xlrd 

from PyQt4 import QtCore, QtGui, uic, Qt

class DraftApp(QtGui.QMainWindow):
	def __init__(self):

		QtGui.QMainWindow.__init__(self)
		self.ui = uic.loadUi("/home/adam/Documents/fantasyfootball/draftapp.ui")
		self.createActions()
		self.setupUi()
		self.ui.label.setMinimumSize(1, 1)
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.Time)
		self.setupPlayerRankings()
		self.ui.show()

	def createActions(self):
		self.ui.actionGenerate_Draft_Order.triggered.connect(self.randomizeDraftOrder)
		self.ui.actionStart_Draft.triggered.connect(self.startDraft)
		self.ui.actionPause_Draft.triggered.connect(self.pauseDraft)
		self.ui.actionResume_Draft.triggered.connect(self.resumeDraft)
		self.ui.pushButton.clicked.connect(self.nextPick)
		self.ui.pushButton_2.clicked.connect(self.draftPlayer)

	def setupUi(self):

		self.ui.lineEdit.setReadOnly(True)
		self.ui.actionStart_Draft.setEnabled(False)
		self.ui.actionResume_Draft.setEnabled(False)
		self.ui.actionPause_Draft.setEnabled(False)
		self.ui.pushButton.setEnabled(False)
		self.ui.pushButton_2.setEnabled(False)

	def randomizeDraftOrder(self):
		self.players = ['Adam', 'Demetri', 'Austin', 'Stubbs', 'Jack', 'Zack', 'Brett', 'Carlson', 'JJ', 'Mike', 'Lucas', 'Robbie']
		random.shuffle(self.players)
		self.ui.listWidget.repaint()
		self.ui.actionGenerate_Draft_Order.setEnabled(False)
		self.reversedPlayers = list(reversed(self.players))
		for i in range(12):
			roundNum = i + 1
			for j in range(12):
				pick = j + 1 + 12*i
				if roundNum % 2 != 0:	
					item = QtGui.QListWidgetItem(str(pick) + ": " + self.players[j])
				else:
					item = QtGui.QListWidgetItem(str(pick) + ": " + self.reversedPlayers[j])
				self.ui.listWidget.addItem(item)
		self.ui.listWidget.setCurrentRow(0)

		self.ui.listWidget.repaint()
		self.ui.actionStart_Draft.setEnabled(True)
		self.ui.actionGenerate_Draft_Order.setEnabled(False)



	def startDraft(self):
		self.Reset(True)
		self.ui.actionPause_Draft.setEnabled(True)
		self.ui.pushButton_2.setEnabled(True)
		self.ui.pushButton.setEnabled(True)
		self.ui.actionStart_Draft.setEnabled(False)
	
	def pauseDraft(self):
		self.timer.stop()
		self.ui.actionResume_Draft.setEnabled(True)
		self.ui.actionPause_Draft.setEnabled(False)

	def resumeDraft(self):
		self.timer.start()
		self.ui.actionResume_Draft.setEnabled(False)
		self.ui.actionPause_Draft.setEnabled(True)

	def nextPick(self):
		self.Reset()

	def eventFilter(self, source, event):
	    if (source is self.ui.label and event.type() == QtCore.QEvent.Resize):
	        # re-scale the pixmap when the label resizes
	        self.ui.label.setPixmap(self.pixmap.scaled(
	            self.ui.label.size(), QtCore.Qt.KeepAspectRatio,
	            QtCore.Qt.SmoothTransformation))
	    return super(QtGui.QMainWindow, self).eventFilter(source, event)

	def setImage(self, playername):
		self.pixmap = QtGui.QPixmap(os.getcwd() + "/" + playername + ".jpg")
   		self.ui.label.setPixmap(self.pixmap)
   		self.ui.label.setScaledContents(True)
   		#self.ui.label.installEventFilter(self)		

	def Reset(self, first=False):
		self.minutes = 1
		self.seconds = 30
		player = self.ui.listWidget.currentItem().text()
		self.setImage(str(player).lower().split(" ")[1])
		item = self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
		item = None
		self.ui.listWidget.repaint()
		self.ui.lineEdit.setText("Player:{0}        Pick:{1}       Round:{2}".format(player.split(":")[1], player.split(":")[0], str(int(player.split(":")[0])/12 + 1)))
		time = ("{0}:{1}".format(self.minutes, self.seconds))
		self.ui.lcdNumber.setDigitCount(len(time))
		self.ui.lcdNumber.display(time)
		self.timer.start(1000)
		
	def Time(self):

		if self.seconds > 0:
			self.seconds -= 1
		elif self.minutes > 0:
			self.minutes -= 1
			self.seconds = 59
		else:
			self.Reset()
		if self.seconds > 9:
			time = ("{0}:{1}".format(self.minutes, self.seconds))
		else:
			time = ("{0}:0{1}".format(self.minutes, self.seconds))
		self.ui.lcdNumber.setDigitCount(len(time))
		self.ui.lcdNumber.display(time)

	def setupPlayerRankings(self):

		xl_workbook = xlrd.open_workbook("/home/adam/Documents/fantasyfootball/rankings.xlsx")
		sheet_names = xl_workbook.sheet_names()
		xl_sheet = xl_workbook.sheet_by_index(0)
		self.playerList = []
		for i in range(252):
			tempPlayerString = "Rank: "
			for j in range(1, 4):
				cell_obj = self.setupSpacing(xl_sheet.cell(i, j).value, j)
				tempPlayerString += str(cell_obj)
				if j == 1:
					tempPlayerString += "  Pos: "
				if j == 2:
					tempPlayerString += "  Team:  "

			tempPlayerString += "      Player: "
			tempPlayerString += xl_sheet.cell(i, 0).value

			self.playerList.append(tempPlayerString)
		for player in self.playerList:
			item = QtGui.QListWidgetItem(player)
			self.ui.listWidgetPlayers.addItem(item)
		self.ui.listWidgetPlayers.repaint()

	def draftPlayer(self):

		player = str(self.ui.lineEdit_2.text())
		if player != "":
			self.searchAndDelete(player)

	def setupSpacing(self, name, section):

		if section == 1:
			rank = str(name).split(".")[0]
			extraSpace = False
			if len(rank) == 1:
				extraSpace = True
			while len(rank) < 3:
				rank += " "
			if extraSpace:
				rank += " "
			return rank
		elif section == 2:
			position = ''.join(k for k in str(name) if not k.isdigit())
			extraSpace = False
			if "WR" not in position and "DST" not in position:
				extraSpace = True
			while len(position) < 3:
				position += " "
			if extraSpace:
				position += " "
			if "K" in position:
				position += " "
			return position
		elif section == 3:
			team = str(name)
			while len(team) < 3:
				team += "  "
			return team

	def searchAndDelete(self, player):
		
		for index in range(self.ui.listWidgetPlayers.count()):
			if player.lower().translate(None, "'.-") in str(self.ui.listWidgetPlayers.item(index).text()).lower().translate(None, "'.-"):
				self.ui.listWidgetPlayers.takeItem(index)
				print player
				self.ui.listWidgetPlayers.repaint()
				break
			

	
			
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = DraftApp()
	sys.exit(app.exec_())

