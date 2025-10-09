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

		self.button_actions = [
			(self.slot_delete, 'del'),
			(self.slot_insert, 'ins'),
			(self.slot_move_up, 'up'),
			(self.slot_move_down, 'down')
		]
		self.frame = QFrame(self)
		self.grid = ShuffleGrid(self.frame)
		for row in range(5):
			for col, widget in enumerate(self.construct_row(row)):
				self.grid.addWidget(widget, row, col)
		self.setCentralWidget(self.frame)

	def construct_row(self, row):
		widgets = []
		for col, tup in enumerate(self.button_actions):
			button = QPushButton(f'Row {row} Col {col}: {tup[1]}', self.frame)
			button.clicked.connect(partial(tup[0], button))
			widgets.append(button)
		return widgets

	def get_button_row(self, button):
		idx = self.grid.indexOf(button)
		row, *_ = self.grid.getItemPosition(idx)
		return row

	@pyqtSlot(QPushButton)
	def slot_delete(self, button):
		row = self.get_button_row(button)
		print(f'Delete row {row}')
		self.grid.delete_row(row)
		print(f'  rowCount is now {self.grid.rowCount()}, ' +
			f'with {self.grid.inhabited_row_count()} rows inhabited')
		self.print_contents()

	@pyqtSlot(QPushButton)
	def slot_insert(self, button):
		row = self.get_button_row(button)
		if row <= self.grid.rowCount():
			print(f'Insert at row {row}')
			self.grid.insert_row(self.construct_row(row), row)
			print(f'  rowCount is now {self.grid.rowCount()}, ' +
				f'with {self.grid.inhabited_row_count()} rows inhabited')
		self.print_contents()

	@pyqtSlot(QPushButton)
	def slot_move_up(self, button):
		row = self.get_button_row(button)
		if row > 0:
			print(f'Move row {row} up')
			self.grid.move_row_up(row)
		self.print_contents()

	@pyqtSlot(QPushButton)
	def slot_move_down(self, button):
		row = self.get_button_row(button)
		if row < self.grid.rowCount() - 1:
			print(f'Move row {row} down')
			self.grid.move_row_down(row)
		self.print_contents()

	def show_empty_rows(self):
		for row in range(self.grid.rowCount()):
			s = 'EMPTY' if self.grid.row_is_empty(row) else 'not empty'
			print(f'  row {row} {s}')

	def print_contents(self):
		print('Iteration:')
		for row in self.grid:
			print([ widget.text() for widget in row ])
		print('Column 0:')
		print([ widget.text() for widget in self.grid.column(0) ])
		row = self.grid.inhabited_row_indexes()[0]
		print(f'First inhabited row (row {row}):')
		print([ widget.text() for widget in self.grid.row(row) ])


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
