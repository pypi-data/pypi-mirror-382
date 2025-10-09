#  qt_extras/tests/menu_button.py
#
#  Copyright 2024 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import logging
from PyQt5.QtCore import pyqtSlot, QVariant
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, \
							QPushButton, QLabel, QShortcut, QVBoxLayout
from qt_extras.list_button import QtListButton


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)

		wid = QWidget(self)
		self.setCentralWidget(wid)
		lo = QVBoxLayout()
		wid.setLayout(lo)

		self.menu_button = QtListButton(self)
		self.menu_button.setPointSize(10)
		self.label_1 = QLabel('THIS IS LABEL 1', self)
		self.label_2 = QLabel('THIS IS LABEL 2', self)

		self.menu_button.setText('Click for menu')
		self.menu_button.addItem("item 1", self.label_1)
		self.menu_button.addItem("item 2", self.label_2)
		self.menu_button.sig_item_selected.connect(self.item_selected)

		select_data_value_button = QPushButton('Test select_data (Choose <label_1>)', self)
		select_data_value_button.clicked.connect(self.select_data_value_button_click)

		set_text_button = QPushButton('Test select_text (Choose "item 2")', self)
		set_text_button.clicked.connect(self.set_text_button_click)

		lo.addWidget(self.label_1)
		lo.addWidget(self.label_2)
		lo.addWidget(self.menu_button)
		lo.addWidget(select_data_value_button)
		lo.addWidget(set_text_button)

	@pyqtSlot(str, QVariant)
	def item_selected(self, _, data):
		# "data" is one of the labels
		data.setText('SELECTED')

	@pyqtSlot()
	def select_data_value_button_click(self):
		self.menu_button.select_data(self.label_1)

	@pyqtSlot()
	def set_text_button_click(self):
		self.menu_button.select_text('item 2')


if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()


#  end qt_extras/tests/menu_button.py
