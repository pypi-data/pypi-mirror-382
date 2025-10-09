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
	Extends QGridLayout to allow for moving rows up / down, inserting, and deleting.
	"""

	def __iter__(self):
		"""
		Generator which returns a list of widgets occupying each row on iteration.

		Where there is no widget in a particular column, the list yielded will contain
		None at that index. The rows returned on each iteration will be the same as the
		number of INHABITED rows (rows that are completely empty are skipped).
		"""
		for row in self.inhabited_row_indexes():
			yield self.row(row)

	def row(self, row):
		"""
		Returns a list of widgets occupying the given row.

		Where there is no widget in a particular column, the list yielded will contain
		None at that index.
		"""
		return [ None if self.itemAtPosition(row, col) is None \
			else self.itemAtPosition(row, col).widget() \
			for col in range(self.columnCount()) ]

	def column(self, column):
		"""
		Returns a list of widgets occupying the given column.

		Where there is no widget in a particular row, the list yielded will contain
		None at that index. In any case, the number of elements returned in the list
		will be the same as the number of INHABITED rows (rows that are completely
		empty are skipped).
		"""
		return [ None if self.itemAtPosition(row, column) is None \
			else self.itemAtPosition(row, column).widget() \
			for row in self.inhabited_row_indexes() ]

	def row_is_empty(self, row):
		"""
		Returns True if given row has no items (used for skipping empty rows).
		"""
		return all(self.itemAtPosition(row, col) is None \
			for col in range(self.columnCount()))

	def inhabited_row_count(self):
		"""
		Returns the count of rows which are inhabited with at least one item.
		"""
		return self.rowCount() - sum(self.row_is_empty(row) for row in range(self.rowCount()))

	def inhabited_row_indexes(self):
		"""
		Returns a list of row indexes for rows which are inhabited with at least one item.
		"""
		return [row for row in range(self.rowCount()) if not self.row_is_empty(row)]

	def delete_row(self, row):
		"""
		Delete the items on the given row.

		The row number given is numbered according to QGridLayout conventions, which
		may include uninhabited rows left over from a row deletion operation - NOT
		according to ShuffleGrid.inhabited_row_indexes().
		"""
		if row < 0 or row >= self.rowCount():
			raise RuntimeError(f'Cannot delete row {row}')
		if self.row_is_empty(row):
			raise ValueError(f'Deletion of empty row {row} has no effect')
		for col in range(self.columnCount()):
			item = self.itemAtPosition(row, col)
			if not item is None:
				index = self.indexOf(item)
				self.takeAt(index)
				widget = item.widget()
				if not widget is None:
					widget.setParent(None)
					widget.deleteLater()
		self.invalidate()

	def insert_row(self, widgets, row):
		"""
		Insert the given list of widgets at the given row

		The row number given is numbered according to QGridLayout conventions, which
		may include uninhabited rows left over from a row deletion operation - NOT
		according to ShuffleGrid.inhabited_row_indexes().
		"""
		if self.rowCount() < 2:
			raise RuntimeError(f'Cannot insert row - grid only has one row')
		if row < 0 or row >= self.rowCount():
			raise RuntimeError(f'Cannot insert row at {row}')
		if not self.row_is_empty(row):
			for iter_row in range(self.rowCount() - 1, row - 1, -1):
				if self.row_is_empty(iter_row):
					continue
				for col in range(self.columnCount()):
					item = self.itemAtPosition(iter_row, col)
					if not item is None:
						index = self.indexOf(item)
						self.takeAt(index)
						self.addItem(item, iter_row + 1, col)
		for col, widget in enumerate(widgets):
			self.addWidget(widget, row, col)
		self.invalidate()

	def move_row_up(self, row):
		"""
		Swap the items in the given row with the items in the previous inhabited row.

		Raises IndexError if the given row is the first inhabited row.

		Raises ValueError if the given row is empty.

		The row number given is numbered according to QGridLayout conventions, which
		may include uninhabited rows left over from a row deletion operation - NOT
		according to ShuffleGrid.inhabited_row_indexes().
		"""
		valid_indexes = self.inhabited_row_indexes()
		try:
			index = valid_indexes.index(row)
		except ValueError:
			raise ValueError(f'Cannot move empty row {row}')
		if index == 0:
			raise IndexError(f'Cannot move first row {row} up')
		self.swap_rows(row, valid_indexes[index - 1])

	def move_row_down(self, row):
		"""
		Swap the items in the given row with the items in the next row.

		Raises IndexError if given row is the last inhabited row.

		Raises ValueError if the given row is empty.

		The row number given is numbered according to QGridLayout conventions, which
		may include uninhabited rows left over from a row deletion operation - NOT
		according to ShuffleGrid.inhabited_row_indexes().
		"""
		valid_indexes = self.inhabited_row_indexes()
		try:
			index = valid_indexes.index(row)
		except ValueError:
			raise ValueError(f'Cannot move empty row {row}')
		if index + 1 == len(valid_indexes):
			raise IndexError(f'Cannot move last row {row} down')
		self.swap_rows(row, valid_indexes[index + 1])

	def swap_rows(self, a, b):
		"""
		Swap the items in row "a" with the items in row "b".
		"""
		for col in range(self.columnCount()):
			item_a = self.itemAtPosition(a, col)
			widget_a = item_a.widget()
			item_b = self.itemAtPosition(b, col)
			widget_b = item_b.widget()
			self.takeAt(self.indexOf(item_b))
			item = self.replaceWidget(widget_a, widget_b, Qt.FindDirectChildrenOnly)
			self.addItem(item_a, b, col)
		self.invalidate()


#  end qt_extras/shuffle_grid.py
