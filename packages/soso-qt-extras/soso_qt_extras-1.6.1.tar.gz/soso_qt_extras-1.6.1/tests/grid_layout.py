#  qt_extras/tests/grid_layout.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
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
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QSpinBox, QLabel, \
							QShortcut, QVBoxLayout, QFrame
from qt_extras.list_layout import GListLayout, HORIZONTAL_FLOW


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)

		wid = QWidget(self)
		self.setCentralWidget(wid)
		lo = QVBoxLayout()
		lo.setSpacing(6)
		wid.setLayout(lo)

		button = QPushButton('Add widget', self)
		button.clicked.connect(self.slot_add_widget)
		lo.addWidget(button)

		lo.addWidget(QLabel('Index to add/remove:', self))

		self.spinbox = QSpinBox(self)
		self.spinbox.setMinimum(-1)
		self.spinbox.setMaximum(-1)
		lo.addWidget(self.spinbox)

		button = QPushButton('Insert widget', self)
		button.clicked.connect(self.slot_insert_widget)
		lo.addWidget(button)

		button = QPushButton('Remove widget', self)
		button.clicked.connect(self.slot_remove_widget)
		lo.addWidget(button)

		button = QPushButton('Clear list', self)
		button.clicked.connect(self.slot_clear_list)
		lo.addWidget(button)

		frm = QFrame(self)
		self.list = GListLayout(1, HORIZONTAL_FLOW)
		frm.setLayout(self.list)
		lo.addWidget(frm)


	def resizeEvent(self, event):
		self.list.set_columns(max(1, event.size().width() // Thing.minimum_width))

	@pyqtSlot()
	def slot_add_widget(self):
		self.list.append(Thing(self))
		self.spinbox.setMaximum(len(self.list) - 1)

	@pyqtSlot()
	def slot_insert_widget(self):
		if self.spinbox.value() > -1:
			self.list.insert(self.spinbox.value(), Thing(self))
		self.spinbox.setMaximum(len(self.list) - 1)

	@pyqtSlot()
	def slot_remove_widget(self):
		if self.spinbox.value() > -1:
			self.list.remove(self.list[self.spinbox.value()])
			self.spinbox.setMaximum(len(self.list) - 1)

	@pyqtSlot()
	def slot_clear_list(self):
		self.list.clear()
		self.spinbox.setMaximum(-1)


class Thing(QWidget):

	minimum_width = 78
	ord = 1

	def __init__(self, parent):
		super().__init__(parent)
		self.setMinimumWidth(self.minimum_width)
		self.setLayout(QVBoxLayout())
		self.label = QLabel(f'Thing {Thing.ord}', self)
		self.layout().addWidget(self.label)
		Thing.ord += 1

	def __str__(self):
		return self.label.text()


if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()


#  end qt_extras/tests/grid_layout.py
