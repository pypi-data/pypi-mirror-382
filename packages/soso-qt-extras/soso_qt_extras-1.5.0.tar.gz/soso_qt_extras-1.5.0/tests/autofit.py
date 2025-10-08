#  qt_extras/tests/autofit.py
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
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QShortcut, \
							QPushButton, QCheckBox, QRadioButton, QLabel, \
							QLineEdit, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QKeySequence
from qt_extras.autofit import autofit


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		layout = QVBoxLayout()
		ed = QLineEdit()

		layout.addWidget(QLabel('QPushbutton:', self))
		w = QPushButton(self)
		autofit(w)
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QPushbutton with padding:', self))
		w = QPushButton(self)
		autofit(w)
		w.setStyleSheet('QPushButton { padding: 16px; }')
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QLabel:', self))
		w = QLabel(self)
		autofit(w)
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QLabel with padding:', self))
		w = QLabel(self)
		autofit(w)
		w.setStyleSheet('QLabel { padding: 16px; }')
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QCheckBox:', self))
		w = QCheckBox(self)
		autofit(w)
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QCheckBox with padding:', self))
		w = QCheckBox(self)
		autofit(w)
		w.setStyleSheet('QCheckBox { padding: 16px; }')
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QRadioButton:', self))
		w = QRadioButton(self)
		autofit(w)
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(QLabel('QRadioButton with padding:', self))
		w = QRadioButton(self)
		autofit(w)
		w.setStyleSheet('QRadioButton { padding: 16px; }')
		w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		ed.textChanged.connect(w.setText)
		layout.addWidget(w)

		layout.addWidget(ed)

		w = QWidget()
		w.setLayout(layout)
		self.setCentralWidget(w)

		self.quit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
		self.quit_shortcut.activated.connect(self.close)
		self.esc_shortcut = QShortcut(QKeySequence('Esc'), self)
		self.esc_shortcut.activated.connect(self.close)


if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)
	app = QApplication([])
	window = MainWindow()
	window.move(QPoint(300,300))
	window.show()
	app.exec()


#  end qt_extras/tests/autofit.py
