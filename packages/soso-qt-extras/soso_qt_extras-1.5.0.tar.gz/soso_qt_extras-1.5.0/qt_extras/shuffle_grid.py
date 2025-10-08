#  qt_extras/shuffle_grid.py
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
"""
Provides the ShuffleGrid class - extends QGridLayout to allow for moving rows up / down and deleting.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout


class ShuffleGrid(QGridLayout):
	"""
	Extends QGridLayout to allow for moving rows up / down and deleting.
	"""

	def delete_row(self, row):
		if row < 0 or row >= self.rowCount():
			raise RuntimeError(f'Cannot delete row {row}')
		for col in range(self.columnCount()):
			item = self.itemAtPosition(row, col)
			index = self.indexOf(item)
			self.takeAt(index)
			item.widget().setParent(None)
			item.widget().deleteLater()

	def move_row_up(self, row):
		if row < 1:
			raise RuntimeError(f'Cannot move row {row} up')
		self.swap_row(row, row - 1)

	def move_row_down(self, row):
		if row >= self.rowCount():
			raise RuntimeError(f'Cannot move row {row} up')
		self.swap_row(row, row + 1)

	def swap_row(self, from_row, to_row):
		for col in range(self.columnCount()):
			from_item = self.itemAtPosition(from_row, col)
			from_widget = from_item.widget()
			to_item = self.itemAtPosition(to_row, col)
			to_widget = to_item.widget()
			to_index = self.indexOf(to_item)
			self.takeAt(to_index)
			item = self.replaceWidget(from_widget, to_widget, Qt.FindDirectChildrenOnly)
			self.addItem(from_item, to_row, col)


#  end qt_extras/shuffle_grid.py
