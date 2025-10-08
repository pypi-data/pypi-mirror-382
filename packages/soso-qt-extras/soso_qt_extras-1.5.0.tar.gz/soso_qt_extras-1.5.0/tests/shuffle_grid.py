#  qt_extras/tests/shuffle_grid.py
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
from functools import partial
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QFrame
from qt_extras.shuffle_grid import ShuffleGrid


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setMinimumWidth(800)
		shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		shortcut.activated.connect(self.close)
		shortcut = QShortcut(QKeySequence('Esc'), self)
		shortcut.activated.connect(self.close)

		frm = QFrame(self)
		self.grid = ShuffleGrid(frm)
		for row in range(5):
			for col in range(5):
				btn = QPushButton(f'Row {row} Col {col}', frm)
				btn.clicked.connect(partial(self.slot_btn_click, btn))
				self.grid.addWidget(btn, row, col)
		self.setCentralWidget(frm)

	@pyqtSlot(QPushButton)
	def slot_btn_click(self, btn):
		idx = self.grid.indexOf(btn)
		row, col, *_ = self.grid.getItemPosition(idx)
		print(f'idx {idx}: row {row} col {col}')
		if col == 3:
			if row > 0:
				self.grid.move_row_up(row)
		elif col == 4:
			if row < 4:
				self.grid.move_row_down(row)
		else:
			self.grid.delete_row(row)


if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)
	app = QApplication([])
	main_window = MainWindow()
	main_window.show()
	app.exec()


#  end qt_extras/tests/shuffle_grid.py
