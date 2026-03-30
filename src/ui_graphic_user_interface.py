# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graphic_user_interface.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDateEdit, QFrame, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1442, 912)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(12)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"background-color: rgb(47, 97, 101);")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setFont(font)
        self.gridLayout_12 = QGridLayout(self.centralwidget)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.environmental_conditions_block = QFrame(self.centralwidget)
        self.environmental_conditions_block.setObjectName(u"environmental_conditions_block")
        self.environmental_conditions_block.setMinimumSize(QSize(0, 0))
        self.environmental_conditions_block.setMaximumSize(QSize(320, 202))
        self.environmental_conditions_block.setFont(font)
        self.environmental_conditions_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.environmental_conditions_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.environmental_conditions_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_14 = QGridLayout(self.environmental_conditions_block)
        self.gridLayout_14.setSpacing(0)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer, 2, 1, 1, 1)

        self.environmental_conditions_grid = QGridLayout()
        self.environmental_conditions_grid.setSpacing(0)
        self.environmental_conditions_grid.setObjectName(u"environmental_conditions_grid")
        self.relative_humidity_label = QLabel(self.environmental_conditions_block)
        self.relative_humidity_label.setObjectName(u"relative_humidity_label")
        self.relative_humidity_label.setMinimumSize(QSize(160, 30))
        self.relative_humidity_label.setMaximumSize(QSize(160, 30))
        self.relative_humidity_label.setFont(font)

        self.environmental_conditions_grid.addWidget(self.relative_humidity_label, 2, 0, 1, 1)

        self.db_temperature_unit = QLabel(self.environmental_conditions_block)
        self.db_temperature_unit.setObjectName(u"db_temperature_unit")
        self.db_temperature_unit.setMinimumSize(QSize(40, 30))
        self.db_temperature_unit.setMaximumSize(QSize(40, 30))
        self.db_temperature_unit.setFont(font)
        self.db_temperature_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.db_temperature_unit.setMargin(0)

        self.environmental_conditions_grid.addWidget(self.db_temperature_unit, 0, 2, 1, 1)

        self.wb_temperature_unit = QLabel(self.environmental_conditions_block)
        self.wb_temperature_unit.setObjectName(u"wb_temperature_unit")
        self.wb_temperature_unit.setMinimumSize(QSize(40, 30))
        self.wb_temperature_unit.setMaximumSize(QSize(40, 30))
        self.wb_temperature_unit.setFont(font)
        self.wb_temperature_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.wb_temperature_unit.setMargin(0)

        self.environmental_conditions_grid.addWidget(self.wb_temperature_unit, 1, 2, 1, 1)

        self.db_temperature_label = QLabel(self.environmental_conditions_block)
        self.db_temperature_label.setObjectName(u"db_temperature_label")
        self.db_temperature_label.setMinimumSize(QSize(160, 30))
        self.db_temperature_label.setMaximumSize(QSize(160, 30))
        self.db_temperature_label.setFont(font)

        self.environmental_conditions_grid.addWidget(self.db_temperature_label, 0, 0, 1, 1)

        self.pressure_label = QLabel(self.environmental_conditions_block)
        self.pressure_label.setObjectName(u"pressure_label")
        self.pressure_label.setMinimumSize(QSize(160, 30))
        self.pressure_label.setMaximumSize(QSize(160, 30))
        self.pressure_label.setFont(font)

        self.environmental_conditions_grid.addWidget(self.pressure_label, 4, 0, 1, 1)

        self.relative_humidity_value = QLineEdit(self.environmental_conditions_block)
        self.relative_humidity_value.setObjectName(u"relative_humidity_value")
        self.relative_humidity_value.setMinimumSize(QSize(80, 30))
        self.relative_humidity_value.setMaximumSize(QSize(80, 30))
        self.relative_humidity_value.setFont(font)
        self.relative_humidity_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.relative_humidity_value.setClearButtonEnabled(True)

        self.environmental_conditions_grid.addWidget(self.relative_humidity_value, 2, 1, 1, 1)

        self.relative_humidity_unit = QLabel(self.environmental_conditions_block)
        self.relative_humidity_unit.setObjectName(u"relative_humidity_unit")
        self.relative_humidity_unit.setMinimumSize(QSize(40, 30))
        self.relative_humidity_unit.setMaximumSize(QSize(40, 30))
        self.relative_humidity_unit.setFont(font)
        self.relative_humidity_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.relative_humidity_unit.setMargin(0)

        self.environmental_conditions_grid.addWidget(self.relative_humidity_unit, 2, 2, 1, 1)

        self.absolute_humidity_label = QLabel(self.environmental_conditions_block)
        self.absolute_humidity_label.setObjectName(u"absolute_humidity_label")
        self.absolute_humidity_label.setMinimumSize(QSize(160, 30))
        self.absolute_humidity_label.setMaximumSize(QSize(160, 30))
        self.absolute_humidity_label.setFont(font)

        self.environmental_conditions_grid.addWidget(self.absolute_humidity_label, 3, 0, 1, 1)

        self.pressure_unit = QLabel(self.environmental_conditions_block)
        self.pressure_unit.setObjectName(u"pressure_unit")
        self.pressure_unit.setMinimumSize(QSize(40, 30))
        self.pressure_unit.setMaximumSize(QSize(40, 30))
        self.pressure_unit.setFont(font)
        self.pressure_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.pressure_unit.setMargin(0)

        self.environmental_conditions_grid.addWidget(self.pressure_unit, 4, 2, 1, 1)

        self.db_temperature_value = QLineEdit(self.environmental_conditions_block)
        self.db_temperature_value.setObjectName(u"db_temperature_value")
        self.db_temperature_value.setMinimumSize(QSize(80, 30))
        self.db_temperature_value.setMaximumSize(QSize(80, 30))
        self.db_temperature_value.setFont(font)
        self.db_temperature_value.setAutoFillBackground(False)
        self.db_temperature_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.db_temperature_value.setClearButtonEnabled(True)

        self.environmental_conditions_grid.addWidget(self.db_temperature_value, 0, 1, 1, 1)

        self.wb_temperature_label = QLabel(self.environmental_conditions_block)
        self.wb_temperature_label.setObjectName(u"wb_temperature_label")
        self.wb_temperature_label.setMinimumSize(QSize(160, 30))
        self.wb_temperature_label.setMaximumSize(QSize(160, 30))
        self.wb_temperature_label.setFont(font)

        self.environmental_conditions_grid.addWidget(self.wb_temperature_label, 1, 0, 1, 1)

        self.wb_temperature_value = QLineEdit(self.environmental_conditions_block)
        self.wb_temperature_value.setObjectName(u"wb_temperature_value")
        self.wb_temperature_value.setMinimumSize(QSize(80, 30))
        self.wb_temperature_value.setMaximumSize(QSize(80, 30))
        self.wb_temperature_value.setFont(font)
        self.wb_temperature_value.setAutoFillBackground(False)
        self.wb_temperature_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.wb_temperature_value.setClearButtonEnabled(True)

        self.environmental_conditions_grid.addWidget(self.wb_temperature_value, 1, 1, 1, 1)

        self.pressure_value = QLineEdit(self.environmental_conditions_block)
        self.pressure_value.setObjectName(u"pressure_value")
        self.pressure_value.setMinimumSize(QSize(80, 30))
        self.pressure_value.setMaximumSize(QSize(80, 30))
        self.pressure_value.setFont(font)
        self.pressure_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.pressure_value.setClearButtonEnabled(True)

        self.environmental_conditions_grid.addWidget(self.pressure_value, 4, 1, 1, 1)

        self.absolute_humidity_value = QLineEdit(self.environmental_conditions_block)
        self.absolute_humidity_value.setObjectName(u"absolute_humidity_value")
        self.absolute_humidity_value.setMinimumSize(QSize(80, 30))
        self.absolute_humidity_value.setMaximumSize(QSize(80, 30))
        self.absolute_humidity_value.setFont(font)
        self.absolute_humidity_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.absolute_humidity_value.setClearButtonEnabled(True)

        self.environmental_conditions_grid.addWidget(self.absolute_humidity_value, 3, 1, 1, 1)

        self.absolute_humidity_unit = QLabel(self.environmental_conditions_block)
        self.absolute_humidity_unit.setObjectName(u"absolute_humidity_unit")
        self.absolute_humidity_unit.setMinimumSize(QSize(45, 30))
        self.absolute_humidity_unit.setMaximumSize(QSize(45, 30))
        self.absolute_humidity_unit.setFont(font)
        self.absolute_humidity_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.absolute_humidity_unit.setMargin(0)

        self.environmental_conditions_grid.addWidget(self.absolute_humidity_unit, 3, 2, 1, 1)


        self.gridLayout_14.addLayout(self.environmental_conditions_grid, 2, 0, 1, 1)

        self.environmental_conditions_label = QLabel(self.environmental_conditions_block)
        self.environmental_conditions_label.setObjectName(u"environmental_conditions_label")
        self.environmental_conditions_label.setMinimumSize(QSize(210, 30))
        self.environmental_conditions_label.setMaximumSize(QSize(210, 30))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(12)
        font1.setBold(True)
        self.environmental_conditions_label.setFont(font1)

        self.gridLayout_14.addWidget(self.environmental_conditions_label, 1, 0, 1, 1)


        self.gridLayout_12.addWidget(self.environmental_conditions_block, 1, 0, 1, 1)

        self.oscilloscope_configurations_block = QFrame(self.centralwidget)
        self.oscilloscope_configurations_block.setObjectName(u"oscilloscope_configurations_block")
        self.oscilloscope_configurations_block.setMinimumSize(QSize(0, 0))
        self.oscilloscope_configurations_block.setMaximumSize(QSize(100000, 172))
        self.oscilloscope_configurations_block.setFont(font)
        self.oscilloscope_configurations_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.oscilloscope_configurations_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.oscilloscope_configurations_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_6 = QGridLayout(self.oscilloscope_configurations_block)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setVerticalSpacing(0)
        self.oscilloscope_configurations_label = QLabel(self.oscilloscope_configurations_block)
        self.oscilloscope_configurations_label.setObjectName(u"oscilloscope_configurations_label")
        self.oscilloscope_configurations_label.setMinimumSize(QSize(270, 30))
        self.oscilloscope_configurations_label.setMaximumSize(QSize(270, 30))
        self.oscilloscope_configurations_label.setFont(font1)

        self.gridLayout_6.addWidget(self.oscilloscope_configurations_label, 0, 0, 1, 1)

        self.btn_search_instrument = QPushButton(self.oscilloscope_configurations_block)
        self.btn_search_instrument.setObjectName(u"btn_search_instrument")
        self.btn_search_instrument.setMinimumSize(QSize(180, 30))
        self.btn_search_instrument.setMaximumSize(QSize(180, 30))
        font2 = QFont()
        font2.setPointSize(12)
        self.btn_search_instrument.setFont(font2)
        self.btn_search_instrument.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout_6.addWidget(self.btn_search_instrument, 0, 3, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.ch2_voltage_label = QLabel(self.oscilloscope_configurations_block)
        self.ch2_voltage_label.setObjectName(u"ch2_voltage_label")
        self.ch2_voltage_label.setMinimumSize(QSize(40, 30))
        self.ch2_voltage_label.setMaximumSize(QSize(40, 30))
        self.ch2_voltage_label.setFont(font)

        self.gridLayout_3.addWidget(self.ch2_voltage_label, 3, 1, 1, 1)

        self.ch2_voltage_value = QComboBox(self.oscilloscope_configurations_block)
        self.ch2_voltage_value.setObjectName(u"ch2_voltage_value")
        self.ch2_voltage_value.setMinimumSize(QSize(60, 30))
        self.ch2_voltage_value.setMaximumSize(QSize(60, 30))
        self.ch2_voltage_value.setFont(font2)
        self.ch2_voltage_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch2_voltage_value, 3, 2, 1, 1)

        self.vertical_scale_label = QLabel(self.oscilloscope_configurations_block)
        self.vertical_scale_label.setObjectName(u"vertical_scale_label")
        self.vertical_scale_label.setMinimumSize(QSize(120, 30))
        self.vertical_scale_label.setMaximumSize(QSize(300, 30))
        self.vertical_scale_label.setFont(font1)

        self.gridLayout_3.addWidget(self.vertical_scale_label, 0, 0, 1, 7)

        self.ch2_offset_value = QLineEdit(self.oscilloscope_configurations_block)
        self.ch2_offset_value.setObjectName(u"ch2_offset_value")
        self.ch2_offset_value.setEnabled(True)
        self.ch2_offset_value.setMinimumSize(QSize(60, 30))
        self.ch2_offset_value.setMaximumSize(QSize(60, 30))
        self.ch2_offset_value.setFont(font)
        self.ch2_offset_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch2_offset_value.setClearButtonEnabled(False)

        self.gridLayout_3.addWidget(self.ch2_offset_value, 3, 5, 1, 1)

        self.ch1_voltage_value = QComboBox(self.oscilloscope_configurations_block)
        self.ch1_voltage_value.setObjectName(u"ch1_voltage_value")
        self.ch1_voltage_value.setMinimumSize(QSize(60, 30))
        self.ch1_voltage_value.setMaximumSize(QSize(60, 30))
        self.ch1_voltage_value.setFont(font2)
        self.ch1_voltage_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch1_voltage_value, 2, 2, 1, 1)

        self.ch2_voltage_unit = QComboBox(self.oscilloscope_configurations_block)
        self.ch2_voltage_unit.setObjectName(u"ch2_voltage_unit")
        self.ch2_voltage_unit.setMinimumSize(QSize(60, 30))
        self.ch2_voltage_unit.setMaximumSize(QSize(60, 30))
        self.ch2_voltage_unit.setFont(font)
        self.ch2_voltage_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch2_voltage_unit, 3, 3, 1, 1)

        self.offset_label = QLabel(self.oscilloscope_configurations_block)
        self.offset_label.setObjectName(u"offset_label")
        self.offset_label.setMinimumSize(QSize(70, 30))
        self.offset_label.setMaximumSize(QSize(70, 30))
        self.offset_label.setFont(font1)

        self.gridLayout_3.addWidget(self.offset_label, 1, 5, 1, 2)

        self.ch2_enabler = QCheckBox(self.oscilloscope_configurations_block)
        self.ch2_enabler.setObjectName(u"ch2_enabler")
        self.ch2_enabler.setEnabled(True)
        self.ch2_enabler.setMinimumSize(QSize(20, 30))
        self.ch2_enabler.setMaximumSize(QSize(20, 30))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        self.ch2_enabler.setFont(font3)
        self.ch2_enabler.setToolTipDuration(-1)
        self.ch2_enabler.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ch2_enabler.setAutoFillBackground(False)
        self.ch2_enabler.setChecked(False)

        self.gridLayout_3.addWidget(self.ch2_enabler, 3, 0, 1, 1)

        self.ch1_offset_value = QLineEdit(self.oscilloscope_configurations_block)
        self.ch1_offset_value.setObjectName(u"ch1_offset_value")
        self.ch1_offset_value.setEnabled(True)
        self.ch1_offset_value.setMinimumSize(QSize(60, 30))
        self.ch1_offset_value.setMaximumSize(QSize(60, 30))
        self.ch1_offset_value.setFont(font)
        self.ch1_offset_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch1_offset_value.setClearButtonEnabled(False)

        self.gridLayout_3.addWidget(self.ch1_offset_value, 2, 5, 1, 1)

        self.amplitude_div_label = QLabel(self.oscilloscope_configurations_block)
        self.amplitude_div_label.setObjectName(u"amplitude_div_label")
        self.amplitude_div_label.setMinimumSize(QSize(87, 30))
        self.amplitude_div_label.setMaximumSize(QSize(4464, 30))
        self.amplitude_div_label.setFont(font1)

        self.gridLayout_3.addWidget(self.amplitude_div_label, 1, 2, 1, 2)

        self.ch2_offset_unit = QComboBox(self.oscilloscope_configurations_block)
        self.ch2_offset_unit.setObjectName(u"ch2_offset_unit")
        self.ch2_offset_unit.setMinimumSize(QSize(60, 30))
        self.ch2_offset_unit.setMaximumSize(QSize(60, 30))
        self.ch2_offset_unit.setFont(font)
        self.ch2_offset_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch2_offset_unit, 3, 6, 1, 1)

        self.ch1_enabler = QCheckBox(self.oscilloscope_configurations_block)
        self.ch1_enabler.setObjectName(u"ch1_enabler")
        self.ch1_enabler.setEnabled(True)
        self.ch1_enabler.setMinimumSize(QSize(20, 30))
        self.ch1_enabler.setMaximumSize(QSize(20, 30))
        self.ch1_enabler.setFont(font3)
        self.ch1_enabler.setToolTipDuration(-1)
        self.ch1_enabler.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ch1_enabler.setAutoFillBackground(False)
        self.ch1_enabler.setChecked(False)

        self.gridLayout_3.addWidget(self.ch1_enabler, 2, 0, 1, 1)

        self.ch1_voltage_unit = QComboBox(self.oscilloscope_configurations_block)
        self.ch1_voltage_unit.setObjectName(u"ch1_voltage_unit")
        self.ch1_voltage_unit.setMinimumSize(QSize(60, 30))
        self.ch1_voltage_unit.setMaximumSize(QSize(60, 30))
        self.ch1_voltage_unit.setFont(font2)
        self.ch1_voltage_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch1_voltage_unit, 2, 3, 1, 1)

        self.ch1_offset_unit = QComboBox(self.oscilloscope_configurations_block)
        self.ch1_offset_unit.setObjectName(u"ch1_offset_unit")
        self.ch1_offset_unit.setMinimumSize(QSize(60, 30))
        self.ch1_offset_unit.setMaximumSize(QSize(60, 30))
        self.ch1_offset_unit.setFont(font2)
        self.ch1_offset_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.ch1_offset_unit, 2, 6, 1, 1)

        self.ch1_voltage_label = QLabel(self.oscilloscope_configurations_block)
        self.ch1_voltage_label.setObjectName(u"ch1_voltage_label")
        self.ch1_voltage_label.setMinimumSize(QSize(40, 30))
        self.ch1_voltage_label.setMaximumSize(QSize(40, 30))
        self.ch1_voltage_label.setFont(font)

        self.gridLayout_3.addWidget(self.ch1_voltage_label, 2, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_4, 2, 4, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_3, 1, 0, 1, 1)

        self.line = QFrame(self.oscilloscope_configurations_block)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line, 1, 1, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontal_scale_label = QLabel(self.oscilloscope_configurations_block)
        self.horizontal_scale_label.setObjectName(u"horizontal_scale_label")
        self.horizontal_scale_label.setMinimumSize(QSize(240, 30))
        self.horizontal_scale_label.setMaximumSize(QSize(240, 30))
        self.horizontal_scale_label.setFont(font1)

        self.gridLayout_4.addWidget(self.horizontal_scale_label, 0, 0, 1, 5)

        self.time_div_label = QLabel(self.oscilloscope_configurations_block)
        self.time_div_label.setObjectName(u"time_div_label")
        self.time_div_label.setMinimumSize(QSize(120, 30))
        self.time_div_label.setMaximumSize(QSize(120, 30))
        self.time_div_label.setFont(font1)

        self.gridLayout_4.addWidget(self.time_div_label, 1, 0, 1, 2)

        self.delay_value = QLineEdit(self.oscilloscope_configurations_block)
        self.delay_value.setObjectName(u"delay_value")
        self.delay_value.setEnabled(True)
        self.delay_value.setMinimumSize(QSize(60, 30))
        self.delay_value.setMaximumSize(QSize(60, 30))
        self.delay_value.setFont(font)
        self.delay_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.delay_value.setClearButtonEnabled(False)

        self.gridLayout_4.addWidget(self.delay_value, 2, 3, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 3, 0, 1, 5)

        self.time_value = QComboBox(self.oscilloscope_configurations_block)
        self.time_value.setObjectName(u"time_value")
        self.time_value.setMinimumSize(QSize(60, 30))
        self.time_value.setMaximumSize(QSize(60, 30))
        self.time_value.setFont(font)
        self.time_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_4.addWidget(self.time_value, 2, 0, 1, 1)

        self.time_unit = QComboBox(self.oscilloscope_configurations_block)
        self.time_unit.setObjectName(u"time_unit")
        self.time_unit.setMinimumSize(QSize(60, 30))
        self.time_unit.setMaximumSize(QSize(60, 30))
        self.time_unit.setFont(font)
        self.time_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_4.addWidget(self.time_unit, 2, 1, 1, 1)

        self.delay_label = QLabel(self.oscilloscope_configurations_block)
        self.delay_label.setObjectName(u"delay_label")
        self.delay_label.setMinimumSize(QSize(120, 30))
        self.delay_label.setMaximumSize(QSize(120, 30))
        self.delay_label.setFont(font1)

        self.gridLayout_4.addWidget(self.delay_label, 1, 3, 1, 2)

        self.delay_unit = QComboBox(self.oscilloscope_configurations_block)
        self.delay_unit.setObjectName(u"delay_unit")
        self.delay_unit.setMinimumSize(QSize(60, 30))
        self.delay_unit.setMaximumSize(QSize(60, 30))
        self.delay_unit.setFont(font2)
        self.delay_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_4.addWidget(self.delay_unit, 2, 4, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 2, 2, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_4, 1, 3, 1, 1)

        self.line_2 = QFrame(self.oscilloscope_configurations_block)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_2, 1, 4, 1, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.trigger_edge_positive = QRadioButton(self.oscilloscope_configurations_block)
        self.trigger_edge_positive.setObjectName(u"trigger_edge_positive")
        self.trigger_edge_positive.setMinimumSize(QSize(90, 30))
        self.trigger_edge_positive.setMaximumSize(QSize(90, 30))
        self.trigger_edge_positive.setFont(font)
        self.trigger_edge_positive.setChecked(True)

        self.gridLayout_5.addWidget(self.trigger_edge_positive, 2, 0, 1, 1)

        self.trigger_level_value = QLineEdit(self.oscilloscope_configurations_block)
        self.trigger_level_value.setObjectName(u"trigger_level_value")
        self.trigger_level_value.setEnabled(True)
        self.trigger_level_value.setMinimumSize(QSize(60, 30))
        self.trigger_level_value.setMaximumSize(QSize(60, 30))
        self.trigger_level_value.setFont(font)
        self.trigger_level_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.trigger_level_value.setClearButtonEnabled(False)

        self.gridLayout_5.addWidget(self.trigger_level_value, 2, 1, 1, 1)

        self.trigger_label = QLabel(self.oscilloscope_configurations_block)
        self.trigger_label.setObjectName(u"trigger_label")
        self.trigger_label.setMinimumSize(QSize(210, 30))
        self.trigger_label.setMaximumSize(QSize(210, 30))
        self.trigger_label.setFont(font1)

        self.gridLayout_5.addWidget(self.trigger_label, 0, 0, 1, 3)

        self.trigger_edge_negative = QRadioButton(self.oscilloscope_configurations_block)
        self.trigger_edge_negative.setObjectName(u"trigger_edge_negative")
        self.trigger_edge_negative.setMinimumSize(QSize(90, 30))
        self.trigger_edge_negative.setMaximumSize(QSize(90, 30))
        self.trigger_edge_negative.setFont(font)

        self.gridLayout_5.addWidget(self.trigger_edge_negative, 3, 0, 1, 1)

        self.trigger_level_label = QLabel(self.oscilloscope_configurations_block)
        self.trigger_level_label.setObjectName(u"trigger_level_label")
        self.trigger_level_label.setMinimumSize(QSize(120, 30))
        self.trigger_level_label.setMaximumSize(QSize(120, 30))
        self.trigger_level_label.setFont(font1)

        self.gridLayout_5.addWidget(self.trigger_level_label, 1, 1, 1, 2)

        self.trigger_level_unit = QComboBox(self.oscilloscope_configurations_block)
        self.trigger_level_unit.setObjectName(u"trigger_level_unit")
        self.trigger_level_unit.setMinimumSize(QSize(60, 30))
        self.trigger_level_unit.setMaximumSize(QSize(60, 30))
        self.trigger_level_unit.setFont(font2)
        self.trigger_level_unit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_5.addWidget(self.trigger_level_unit, 2, 2, 1, 1)

        self.trigger_edge = QLabel(self.oscilloscope_configurations_block)
        self.trigger_edge.setObjectName(u"trigger_edge")
        self.trigger_edge.setMinimumSize(QSize(90, 30))
        self.trigger_edge.setMaximumSize(QSize(90, 30))
        self.trigger_edge.setFont(font1)

        self.gridLayout_5.addWidget(self.trigger_edge, 1, 0, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 1, 5, 1, 1)


        self.gridLayout_12.addWidget(self.oscilloscope_configurations_block, 9, 0, 1, 2)

        self.impulse_graph_block = QFrame(self.centralwidget)
        self.impulse_graph_block.setObjectName(u"impulse_graph_block")
        self.impulse_graph_block.setMinimumSize(QSize(0, 0))
        self.impulse_graph_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.impulse_graph_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.impulse_graph_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_11 = QGridLayout(self.impulse_graph_block)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.real_type_radio = QRadioButton(self.impulse_graph_block)
        self.real_type_radio.setObjectName(u"real_type_radio")
        self.real_type_radio.setMinimumSize(QSize(60, 30))
        self.real_type_radio.setMaximumSize(QSize(110, 30))
        self.real_type_radio.setFont(font)
        self.real_type_radio.setChecked(True)

        self.gridLayout_11.addWidget(self.real_type_radio, 0, 6, 1, 1)

        self.graph_view = PlotWidget(self.impulse_graph_block)
        self.graph_view.setObjectName(u"graph_view")
        self.graph_view.setEnabled(True)
        self.graph_view.setMinimumSize(QSize(631, 0))
        self.graph_view.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.gridLayout_11.addWidget(self.graph_view, 1, 0, 1, 8)

        self.graph_name = QLineEdit(self.impulse_graph_block)
        self.graph_name.setObjectName(u"graph_name")
        self.graph_name.setEnabled(False)
        self.graph_name.setMinimumSize(QSize(200, 30))
        self.graph_name.setMaximumSize(QSize(200, 30))
        self.graph_name.setFont(font)
        self.graph_name.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.graph_name, 0, 1, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_11.addItem(self.horizontalSpacer_7, 0, 3, 1, 1)

        self.waveform_graph_label = QLabel(self.impulse_graph_block)
        self.waveform_graph_label.setObjectName(u"waveform_graph_label")
        self.waveform_graph_label.setMinimumSize(QSize(160, 30))
        self.waveform_graph_label.setMaximumSize(QSize(160, 30))
        self.waveform_graph_label.setFont(font1)

        self.gridLayout_11.addWidget(self.waveform_graph_label, 0, 0, 1, 1)

        self.normalized_type_radio = QRadioButton(self.impulse_graph_block)
        self.normalized_type_radio.setObjectName(u"normalized_type_radio")
        self.normalized_type_radio.setMinimumSize(QSize(110, 30))
        self.normalized_type_radio.setMaximumSize(QSize(110, 30))
        self.normalized_type_radio.setFont(font)
        self.normalized_type_radio.setChecked(False)

        self.gridLayout_11.addWidget(self.normalized_type_radio, 0, 7, 1, 1)

        self.graph_type_label = QLabel(self.impulse_graph_block)
        self.graph_type_label.setObjectName(u"graph_type_label")
        self.graph_type_label.setMinimumSize(QSize(120, 30))
        self.graph_type_label.setMaximumSize(QSize(110, 30))
        self.graph_type_label.setFont(font1)

        self.gridLayout_11.addWidget(self.graph_type_label, 0, 5, 1, 1)

        self.btn_visibility = QPushButton(self.impulse_graph_block)
        self.btn_visibility.setObjectName(u"btn_visibility")
        self.btn_visibility.setMinimumSize(QSize(110, 30))
        self.btn_visibility.setMaximumSize(QSize(110, 30))
        font4 = QFont()
        font4.setPointSize(12)
        font4.setBold(False)
        self.btn_visibility.setFont(font4)
        self.btn_visibility.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout_11.addWidget(self.btn_visibility, 0, 2, 1, 1)


        self.gridLayout_12.addWidget(self.impulse_graph_block, 0, 1, 9, 4)

        self.test_results_block = QFrame(self.centralwidget)
        self.test_results_block.setObjectName(u"test_results_block")
        self.test_results_block.setMinimumSize(QSize(0, 0))
        self.test_results_block.setMaximumSize(QSize(200, 172))
        self.test_results_block.setFont(font)
        self.test_results_block.setStyleSheet(u"background-color: rgb(247, 242, 222);\n"
"\n"
"QLineEdit:{\n"
"					background-color: transparent;}")
        self.test_results_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.test_results_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_18 = QGridLayout(self.test_results_block)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.gridLayout_18.setHorizontalSpacing(0)
        self.test_results_label = QLabel(self.test_results_block)
        self.test_results_label.setObjectName(u"test_results_label")
        self.test_results_label.setMinimumSize(QSize(180, 30))
        self.test_results_label.setMaximumSize(QSize(180, 30))
        self.test_results_label.setFont(font1)

        self.gridLayout_18.addWidget(self.test_results_label, 0, 0, 1, 1)

        self.test_results_grid = QGridLayout()
        self.test_results_grid.setSpacing(0)
        self.test_results_grid.setObjectName(u"test_results_grid")
        self.t2_label = QLabel(self.test_results_block)
        self.t2_label.setObjectName(u"t2_label")
        self.t2_label.setMinimumSize(QSize(40, 30))
        self.t2_label.setMaximumSize(QSize(40, 30))
        self.t2_label.setFont(font)

        self.test_results_grid.addWidget(self.t2_label, 2, 0, 1, 1)

        self.t2_unit = QLabel(self.test_results_block)
        self.t2_unit.setObjectName(u"t2_unit")
        self.t2_unit.setMinimumSize(QSize(30, 30))
        self.t2_unit.setMaximumSize(QSize(30, 30))
        self.t2_unit.setFont(font)
        self.t2_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.test_results_grid.addWidget(self.t2_unit, 2, 2, 1, 1)

        self.peak_voltage_value = QLineEdit(self.test_results_block)
        self.peak_voltage_value.setObjectName(u"peak_voltage_value")
        self.peak_voltage_value.setMinimumSize(QSize(80, 30))
        self.peak_voltage_value.setMaximumSize(QSize(80, 30))
        self.peak_voltage_value.setFont(font)
        self.peak_voltage_value.setStyleSheet(u"")
        self.peak_voltage_value.setReadOnly(True)

        self.test_results_grid.addWidget(self.peak_voltage_value, 0, 1, 1, 1)

        self.os_label = QLabel(self.test_results_block)
        self.os_label.setObjectName(u"os_label")
        self.os_label.setMinimumSize(QSize(40, 30))
        self.os_label.setMaximumSize(QSize(40, 30))
        self.os_label.setFont(font)

        self.test_results_grid.addWidget(self.os_label, 3, 0, 1, 1)

        self.t2_value = QLineEdit(self.test_results_block)
        self.t2_value.setObjectName(u"t2_value")
        self.t2_value.setMinimumSize(QSize(80, 30))
        self.t2_value.setMaximumSize(QSize(80, 30))
        self.t2_value.setFont(font)
        self.t2_value.setStyleSheet(u"")
        self.t2_value.setReadOnly(True)

        self.test_results_grid.addWidget(self.t2_value, 2, 1, 1, 1)

        self.peak_voltage_label = QLabel(self.test_results_block)
        self.peak_voltage_label.setObjectName(u"peak_voltage_label")
        self.peak_voltage_label.setEnabled(True)
        self.peak_voltage_label.setMinimumSize(QSize(40, 30))
        self.peak_voltage_label.setMaximumSize(QSize(40, 30))
        self.peak_voltage_label.setFont(font)

        self.test_results_grid.addWidget(self.peak_voltage_label, 0, 0, 1, 1)

        self.os_value = QLineEdit(self.test_results_block)
        self.os_value.setObjectName(u"os_value")
        self.os_value.setMinimumSize(QSize(80, 30))
        self.os_value.setMaximumSize(QSize(80, 30))
        self.os_value.setFont(font)
        self.os_value.setStyleSheet(u"")
        self.os_value.setReadOnly(True)

        self.test_results_grid.addWidget(self.os_value, 3, 1, 1, 1)

        self.t1_value = QLineEdit(self.test_results_block)
        self.t1_value.setObjectName(u"t1_value")
        self.t1_value.setMinimumSize(QSize(80, 30))
        self.t1_value.setMaximumSize(QSize(80, 30))
        self.t1_value.setFont(font)
        self.t1_value.setStyleSheet(u"")
        self.t1_value.setReadOnly(True)

        self.test_results_grid.addWidget(self.t1_value, 1, 1, 1, 1)

        self.t1_label = QLabel(self.test_results_block)
        self.t1_label.setObjectName(u"t1_label")
        self.t1_label.setMinimumSize(QSize(40, 30))
        self.t1_label.setMaximumSize(QSize(40, 30))
        self.t1_label.setFont(font)

        self.test_results_grid.addWidget(self.t1_label, 1, 0, 1, 1)

        self.os_unit = QLabel(self.test_results_block)
        self.os_unit.setObjectName(u"os_unit")
        self.os_unit.setMinimumSize(QSize(30, 30))
        self.os_unit.setMaximumSize(QSize(30, 30))
        self.os_unit.setFont(font)
        self.os_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.test_results_grid.addWidget(self.os_unit, 3, 2, 1, 1)

        self.peak_voltage_unit = QLabel(self.test_results_block)
        self.peak_voltage_unit.setObjectName(u"peak_voltage_unit")
        self.peak_voltage_unit.setMinimumSize(QSize(30, 30))
        self.peak_voltage_unit.setMaximumSize(QSize(30, 30))
        self.peak_voltage_unit.setFont(font)
        self.peak_voltage_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.test_results_grid.addWidget(self.peak_voltage_unit, 0, 2, 1, 1)

        self.t1_unit = QLabel(self.test_results_block)
        self.t1_unit.setObjectName(u"t1_unit")
        self.t1_unit.setMinimumSize(QSize(30, 30))
        self.t1_unit.setMaximumSize(QSize(30, 30))
        self.t1_unit.setFont(font)
        self.t1_unit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.test_results_grid.addWidget(self.t1_unit, 1, 2, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.test_results_grid.addItem(self.verticalSpacer_5, 4, 0, 1, 3)


        self.gridLayout_18.addLayout(self.test_results_grid, 1, 0, 1, 1)


        self.gridLayout_12.addWidget(self.test_results_block, 9, 4, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_12.addItem(self.horizontalSpacer_3, 9, 2, 1, 1)

        self.test_block = QFrame(self.centralwidget)
        self.test_block.setObjectName(u"test_block")
        self.test_block.setMinimumSize(QSize(0, 0))
        self.test_block.setMaximumSize(QSize(320, 172))
        self.test_block.setFont(font)
        self.test_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.test_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.test_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.test_block)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(0)
        self.test_label = QLabel(self.test_block)
        self.test_label.setObjectName(u"test_label")
        self.test_label.setMinimumSize(QSize(100, 30))
        self.test_label.setMaximumSize(QSize(100, 30))
        self.test_label.setFont(font1)

        self.gridLayout_2.addWidget(self.test_label, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 5, 0, 1, 1)

        self.btn_save_waveform = QPushButton(self.test_block)
        self.btn_save_waveform.setObjectName(u"btn_save_waveform")
        self.btn_save_waveform.setMinimumSize(QSize(90, 30))
        self.btn_save_waveform.setMaximumSize(QSize(90, 30))
        self.btn_save_waveform.setFont(font2)
        self.btn_save_waveform.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout_2.addWidget(self.btn_save_waveform, 3, 0, 1, 1)

        self.btn_wait_waveform = QPushButton(self.test_block)
        self.btn_wait_waveform.setObjectName(u"btn_wait_waveform")
        self.btn_wait_waveform.setMinimumSize(QSize(90, 30))
        self.btn_wait_waveform.setMaximumSize(QSize(90, 30))
        self.btn_wait_waveform.setFont(font2)
        self.btn_wait_waveform.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout_2.addWidget(self.btn_wait_waveform, 2, 0, 1, 1)

        self.btn_export_results = QPushButton(self.test_block)
        self.btn_export_results.setObjectName(u"btn_export_results")
        self.btn_export_results.setMinimumSize(QSize(90, 30))
        self.btn_export_results.setMaximumSize(QSize(90, 30))
        self.btn_export_results.setFont(font2)
        self.btn_export_results.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout_2.addWidget(self.btn_export_results, 4, 0, 1, 1)


        self.gridLayout_12.addWidget(self.test_block, 9, 3, 1, 1)

        self.test_data_block = QFrame(self.centralwidget)
        self.test_data_block.setObjectName(u"test_data_block")
        self.test_data_block.setMinimumSize(QSize(0, 0))
        self.test_data_block.setMaximumSize(QSize(320, 148))
        self.test_data_block.setFont(font1)
        self.test_data_block.setAutoFillBackground(False)
        self.test_data_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.test_data_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.test_data_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.test_data_block)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.test_data_label = QLabel(self.test_data_block)
        self.test_data_label.setObjectName(u"test_data_label")
        self.test_data_label.setMinimumSize(QSize(150, 30))
        self.test_data_label.setMaximumSize(QSize(150, 30))
        self.test_data_label.setFont(font1)

        self.gridLayout.addWidget(self.test_data_label, 0, 0, 1, 1)

        self.test_data_grid = QGridLayout()
        self.test_data_grid.setSpacing(0)
        self.test_data_grid.setObjectName(u"test_data_grid")
        self.client_label = QLabel(self.test_data_block)
        self.client_label.setObjectName(u"client_label")
        self.client_label.setMinimumSize(QSize(70, 30))
        self.client_label.setMaximumSize(QSize(70, 30))
        self.client_label.setFont(font)

        self.test_data_grid.addWidget(self.client_label, 2, 0, 1, 1)

        self.item_number_value = QLineEdit(self.test_data_block)
        self.item_number_value.setObjectName(u"item_number_value")
        self.item_number_value.setMinimumSize(QSize(160, 30))
        self.item_number_value.setMaximumSize(QSize(160, 30))
        self.item_number_value.setFont(font)
        self.item_number_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.item_number_value.setClearButtonEnabled(False)

        self.test_data_grid.addWidget(self.item_number_value, 1, 1, 1, 1)

        self.date_label = QLabel(self.test_data_block)
        self.date_label.setObjectName(u"date_label")
        self.date_label.setMinimumSize(QSize(70, 30))
        self.date_label.setMaximumSize(QSize(70, 30))
        self.date_label.setFont(font)

        self.test_data_grid.addWidget(self.date_label, 0, 0, 1, 1)

        self.date_value = QDateEdit(self.test_data_block)
        self.date_value.setObjectName(u"date_value")
        self.date_value.setMinimumSize(QSize(212, 30))
        self.date_value.setMaximumSize(QSize(212, 30))
        self.date_value.setFont(font)
        self.date_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.date_value.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.date_value.setTimeSpec(Qt.TimeSpec.LocalTime)
        self.date_value.setDate(QDate(2026, 1, 1))

        self.test_data_grid.addWidget(self.date_value, 0, 1, 1, 3)

        self.client_value = QLineEdit(self.test_data_block)
        self.client_value.setObjectName(u"client_value")
        self.client_value.setMinimumSize(QSize(212, 30))
        self.client_value.setMaximumSize(QSize(212, 30))
        self.client_value.setFont(font)
        self.client_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.client_value.setClearButtonEnabled(True)

        self.test_data_grid.addWidget(self.client_value, 2, 1, 1, 3)

        self.item_year_value = QLineEdit(self.test_data_block)
        self.item_year_value.setObjectName(u"item_year_value")
        self.item_year_value.setMinimumSize(QSize(30, 30))
        self.item_year_value.setMaximumSize(QSize(30, 30))
        self.item_year_value.setFont(font)
        self.item_year_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.item_year_value.setMaxLength(32767)
        self.item_year_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.test_data_grid.addWidget(self.item_year_value, 1, 3, 1, 1)

        self.item_label = QLabel(self.test_data_block)
        self.item_label.setObjectName(u"item_label")
        self.item_label.setMinimumSize(QSize(70, 30))
        self.item_label.setMaximumSize(QSize(70, 30))
        self.item_label.setFont(font)

        self.test_data_grid.addWidget(self.item_label, 1, 0, 1, 1)

        self.item_dash = QLineEdit(self.test_data_block)
        self.item_dash.setObjectName(u"item_dash")
        self.item_dash.setEnabled(False)
        self.item_dash.setMinimumSize(QSize(15, 30))
        self.item_dash.setMaximumSize(QSize(15, 30))
        self.item_dash.setFont(font)
        self.item_dash.setStyleSheet(u"border: None;")
        self.item_dash.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.test_data_grid.addWidget(self.item_dash, 1, 2, 1, 1)


        self.gridLayout.addLayout(self.test_data_grid, 1, 0, 1, 2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.btn_create_folder = QPushButton(self.test_data_block)
        self.btn_create_folder.setObjectName(u"btn_create_folder")
        self.btn_create_folder.setMinimumSize(QSize(0, 0))
        self.btn_create_folder.setMaximumSize(QSize(150, 30))
        self.btn_create_folder.setFont(font2)
        self.btn_create_folder.setStyleSheet(u"background-color: rgba(227, 222, 204, 254);")

        self.gridLayout.addWidget(self.btn_create_folder, 0, 1, 1, 1)


        self.gridLayout_12.addWidget(self.test_data_block, 0, 0, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_7, 8, 0, 1, 1)

        self.system_attenuations_block = QFrame(self.centralwidget)
        self.system_attenuations_block.setObjectName(u"system_attenuations_block")
        self.system_attenuations_block.setMinimumSize(QSize(0, 0))
        self.system_attenuations_block.setMaximumSize(QSize(320, 142))
        self.system_attenuations_block.setFont(font)
        self.system_attenuations_block.setStyleSheet(u"background-color: rgb(247, 242, 222);")
        self.system_attenuations_block.setFrameShape(QFrame.Shape.StyledPanel)
        self.system_attenuations_block.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_20 = QGridLayout(self.system_attenuations_block)
        self.gridLayout_20.setSpacing(0)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.system_attenuations_label = QLabel(self.system_attenuations_block)
        self.system_attenuations_label.setObjectName(u"system_attenuations_label")
        self.system_attenuations_label.setMinimumSize(QSize(210, 30))
        self.system_attenuations_label.setMaximumSize(QSize(210, 30))
        self.system_attenuations_label.setFont(font1)

        self.gridLayout_20.addWidget(self.system_attenuations_label, 0, 0, 1, 1)

        self.system_attenuation_grid = QGridLayout()
        self.system_attenuation_grid.setSpacing(0)
        self.system_attenuation_grid.setObjectName(u"system_attenuation_grid")
        self.attenuations_enabler = QCheckBox(self.system_attenuations_block)
        self.attenuations_enabler.setObjectName(u"attenuations_enabler")
        self.attenuations_enabler.setEnabled(True)
        self.attenuations_enabler.setMinimumSize(QSize(80, 30))
        self.attenuations_enabler.setMaximumSize(QSize(80, 30))
        self.attenuations_enabler.setFont(font3)
        self.attenuations_enabler.setToolTipDuration(-1)
        self.attenuations_enabler.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.attenuations_enabler.setAutoFillBackground(False)
        self.attenuations_enabler.setChecked(False)

        self.system_attenuation_grid.addWidget(self.attenuations_enabler, 0, 0, 1, 1)

        self.ch1_attenuation_label = QLabel(self.system_attenuations_block)
        self.ch1_attenuation_label.setObjectName(u"ch1_attenuation_label")
        self.ch1_attenuation_label.setMinimumSize(QSize(45, 30))
        self.ch1_attenuation_label.setMaximumSize(QSize(45, 30))
        self.ch1_attenuation_label.setFont(font)
        self.ch1_attenuation_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ch1_attenuation_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.ch1_attenuation_label.setMargin(5)

        self.system_attenuation_grid.addWidget(self.ch1_attenuation_label, 0, 3, 1, 1)

        self.ch1_resistive_divider_value = QLineEdit(self.system_attenuations_block)
        self.ch1_resistive_divider_value.setObjectName(u"ch1_resistive_divider_value")
        self.ch1_resistive_divider_value.setEnabled(True)
        self.ch1_resistive_divider_value.setMinimumSize(QSize(80, 30))
        self.ch1_resistive_divider_value.setMaximumSize(QSize(80, 30))
        self.ch1_resistive_divider_value.setFont(font)
        self.ch1_resistive_divider_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch1_resistive_divider_value.setClearButtonEnabled(False)

        self.system_attenuation_grid.addWidget(self.ch1_resistive_divider_value, 1, 3, 1, 1)

        self.resistive_divider_label = QLabel(self.system_attenuations_block)
        self.resistive_divider_label.setObjectName(u"resistive_divider_label")
        self.resistive_divider_label.setMinimumSize(QSize(130, 30))
        self.resistive_divider_label.setMaximumSize(QSize(130, 30))
        self.resistive_divider_label.setFont(font)

        self.system_attenuation_grid.addWidget(self.resistive_divider_label, 1, 0, 1, 1)

        self.ch2_attenuator_value = QLineEdit(self.system_attenuations_block)
        self.ch2_attenuator_value.setObjectName(u"ch2_attenuator_value")
        self.ch2_attenuator_value.setEnabled(True)
        self.ch2_attenuator_value.setMinimumSize(QSize(80, 30))
        self.ch2_attenuator_value.setMaximumSize(QSize(80, 30))
        self.ch2_attenuator_value.setFont(font)
        self.ch2_attenuator_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch2_attenuator_value.setClearButtonEnabled(False)

        self.system_attenuation_grid.addWidget(self.ch2_attenuator_value, 2, 4, 1, 1)

        self.attenuator_label = QLabel(self.system_attenuations_block)
        self.attenuator_label.setObjectName(u"attenuator_label")
        self.attenuator_label.setMinimumSize(QSize(130, 30))
        self.attenuator_label.setMaximumSize(QSize(130, 30))
        self.attenuator_label.setFont(font)

        self.system_attenuation_grid.addWidget(self.attenuator_label, 2, 0, 1, 1)

        self.ch2_resistive_divider_value = QLineEdit(self.system_attenuations_block)
        self.ch2_resistive_divider_value.setObjectName(u"ch2_resistive_divider_value")
        self.ch2_resistive_divider_value.setEnabled(True)
        self.ch2_resistive_divider_value.setMinimumSize(QSize(80, 30))
        self.ch2_resistive_divider_value.setMaximumSize(QSize(80, 30))
        self.ch2_resistive_divider_value.setFont(font)
        self.ch2_resistive_divider_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch2_resistive_divider_value.setClearButtonEnabled(False)

        self.system_attenuation_grid.addWidget(self.ch2_resistive_divider_value, 1, 4, 1, 1)

        self.ch1_attenuator_value = QLineEdit(self.system_attenuations_block)
        self.ch1_attenuator_value.setObjectName(u"ch1_attenuator_value")
        self.ch1_attenuator_value.setEnabled(True)
        self.ch1_attenuator_value.setMinimumSize(QSize(80, 30))
        self.ch1_attenuator_value.setMaximumSize(QSize(80, 30))
        self.ch1_attenuator_value.setFont(font)
        self.ch1_attenuator_value.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.ch1_attenuator_value.setClearButtonEnabled(False)

        self.system_attenuation_grid.addWidget(self.ch1_attenuator_value, 2, 3, 1, 1)

        self.ch2_attenuation_label = QLabel(self.system_attenuations_block)
        self.ch2_attenuation_label.setObjectName(u"ch2_attenuation_label")
        self.ch2_attenuation_label.setMinimumSize(QSize(45, 30))
        self.ch2_attenuation_label.setMaximumSize(QSize(45, 30))
        self.ch2_attenuation_label.setFont(font)
        self.ch2_attenuation_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ch2_attenuation_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.ch2_attenuation_label.setMargin(5)

        self.system_attenuation_grid.addWidget(self.ch2_attenuation_label, 0, 4, 1, 1)


        self.gridLayout_20.addLayout(self.system_attenuation_grid, 1, 0, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_20.addItem(self.horizontalSpacer_8, 1, 1, 1, 1)


        self.gridLayout_12.addWidget(self.system_attenuations_block, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.date_value, self.item_number_value)
        QWidget.setTabOrder(self.item_number_value, self.item_year_value)
        QWidget.setTabOrder(self.item_year_value, self.client_value)
        QWidget.setTabOrder(self.client_value, self.db_temperature_value)
        QWidget.setTabOrder(self.db_temperature_value, self.wb_temperature_value)
        QWidget.setTabOrder(self.wb_temperature_value, self.relative_humidity_value)
        QWidget.setTabOrder(self.relative_humidity_value, self.absolute_humidity_value)
        QWidget.setTabOrder(self.absolute_humidity_value, self.pressure_value)
        QWidget.setTabOrder(self.pressure_value, self.btn_create_folder)
        QWidget.setTabOrder(self.btn_create_folder, self.attenuations_enabler)
        QWidget.setTabOrder(self.attenuations_enabler, self.ch1_resistive_divider_value)
        QWidget.setTabOrder(self.ch1_resistive_divider_value, self.ch1_attenuator_value)
        QWidget.setTabOrder(self.ch1_attenuator_value, self.ch2_resistive_divider_value)
        QWidget.setTabOrder(self.ch2_resistive_divider_value, self.ch2_attenuator_value)
        QWidget.setTabOrder(self.ch2_attenuator_value, self.btn_search_instrument)
        QWidget.setTabOrder(self.btn_search_instrument, self.ch1_enabler)
        QWidget.setTabOrder(self.ch1_enabler, self.ch1_voltage_unit)
        QWidget.setTabOrder(self.ch1_voltage_unit, self.ch1_voltage_value)
        QWidget.setTabOrder(self.ch1_voltage_value, self.ch1_offset_unit)
        QWidget.setTabOrder(self.ch1_offset_unit, self.ch1_offset_value)
        QWidget.setTabOrder(self.ch1_offset_value, self.ch2_enabler)
        QWidget.setTabOrder(self.ch2_enabler, self.ch2_voltage_unit)
        QWidget.setTabOrder(self.ch2_voltage_unit, self.ch2_voltage_value)
        QWidget.setTabOrder(self.ch2_voltage_value, self.ch2_offset_unit)
        QWidget.setTabOrder(self.ch2_offset_unit, self.ch2_offset_value)
        QWidget.setTabOrder(self.ch2_offset_value, self.time_unit)
        QWidget.setTabOrder(self.time_unit, self.time_value)
        QWidget.setTabOrder(self.time_value, self.delay_unit)
        QWidget.setTabOrder(self.delay_unit, self.delay_value)
        QWidget.setTabOrder(self.delay_value, self.trigger_edge_positive)
        QWidget.setTabOrder(self.trigger_edge_positive, self.trigger_edge_negative)
        QWidget.setTabOrder(self.trigger_edge_negative, self.trigger_level_unit)
        QWidget.setTabOrder(self.trigger_level_unit, self.trigger_level_value)
        QWidget.setTabOrder(self.trigger_level_value, self.btn_wait_waveform)
        QWidget.setTabOrder(self.btn_wait_waveform, self.btn_save_waveform)
        QWidget.setTabOrder(self.btn_save_waveform, self.real_type_radio)
        QWidget.setTabOrder(self.real_type_radio, self.normalized_type_radio)
        QWidget.setTabOrder(self.normalized_type_radio, self.btn_visibility)
        QWidget.setTabOrder(self.btn_visibility, self.graph_name)
        QWidget.setTabOrder(self.graph_name, self.graph_view)
        QWidget.setTabOrder(self.graph_view, self.peak_voltage_value)
        QWidget.setTabOrder(self.peak_voltage_value, self.t1_value)
        QWidget.setTabOrder(self.t1_value, self.t2_value)
        QWidget.setTabOrder(self.t2_value, self.os_value)
        QWidget.setTabOrder(self.os_value, self.item_dash)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Analizador de impulsos 1,2/50 \u00b5s", None))
        self.relative_humidity_label.setText(QCoreApplication.translate("MainWindow", u"Humedad Relativa =", None))
        self.db_temperature_unit.setText(QCoreApplication.translate("MainWindow", u" \u00b0C", None))
        self.wb_temperature_unit.setText(QCoreApplication.translate("MainWindow", u" \u00b0C", None))
        self.db_temperature_label.setText(QCoreApplication.translate("MainWindow", u"Temperatura (BS) =", None))
        self.pressure_label.setText(QCoreApplication.translate("MainWindow", u"Presi\u00f3n Atmosf\u00e9rica =", None))
        self.relative_humidity_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"55.0", None))
        self.relative_humidity_unit.setText(QCoreApplication.translate("MainWindow", u" %", None))
        self.absolute_humidity_label.setText(QCoreApplication.translate("MainWindow", u"Humedad Absoluta =", None))
        self.pressure_unit.setText(QCoreApplication.translate("MainWindow", u" hPa", None))
        self.db_temperature_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"25.0", None))
        self.wb_temperature_label.setText(QCoreApplication.translate("MainWindow", u"Temperatura (BH) =", None))
        self.wb_temperature_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"25.0", None))
        self.pressure_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"970.5", None))
        self.absolute_humidity_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"55.0", None))
        self.absolute_humidity_unit.setText(QCoreApplication.translate("MainWindow", u" g/m3", None))
        self.environmental_conditions_label.setText(QCoreApplication.translate("MainWindow", u"Condiciones ambientales:", None))
        self.oscilloscope_configurations_label.setText(QCoreApplication.translate("MainWindow", u"Configuraciones del osciloscopio:", None))
        self.btn_search_instrument.setText(QCoreApplication.translate("MainWindow", u"Buscar instrumento", None))
        self.ch2_voltage_label.setText(QCoreApplication.translate("MainWindow", u"CH2:", None))
        self.vertical_scale_label.setText(QCoreApplication.translate("MainWindow", u"Escala vertical:", None))
        self.offset_label.setText(QCoreApplication.translate("MainWindow", u"Offset:", None))
        self.ch2_enabler.setText("")
        self.amplitude_div_label.setText(QCoreApplication.translate("MainWindow", u"Amplitud / DIV", None))
        self.ch1_enabler.setText("")
        self.ch1_voltage_label.setText(QCoreApplication.translate("MainWindow", u"CH1:", None))
        self.horizontal_scale_label.setText(QCoreApplication.translate("MainWindow", u"Escala horizontal:", None))
        self.time_div_label.setText(QCoreApplication.translate("MainWindow", u"Tiempo / DIV", None))
        self.delay_label.setText(QCoreApplication.translate("MainWindow", u"Delay:", None))
        self.trigger_edge_positive.setText(QCoreApplication.translate("MainWindow", u"Positivo", None))
        self.trigger_label.setText(QCoreApplication.translate("MainWindow", u"Trigger:", None))
        self.trigger_edge_negative.setText(QCoreApplication.translate("MainWindow", u"Negativo", None))
        self.trigger_level_label.setText(QCoreApplication.translate("MainWindow", u"Nivel:", None))
        self.trigger_edge.setText(QCoreApplication.translate("MainWindow", u"Flanco:", None))
        self.real_type_radio.setText(QCoreApplication.translate("MainWindow", u"Real", None))
        self.waveform_graph_label.setText(QCoreApplication.translate("MainWindow", u"Gr\u00e1fico de Onda N.\u00b0:", None))
        self.normalized_type_radio.setText(QCoreApplication.translate("MainWindow", u"Normalizado", None))
        self.graph_type_label.setText(QCoreApplication.translate("MainWindow", u"Tipo de gr\u00e1fico:", None))
        self.btn_visibility.setText(QCoreApplication.translate("MainWindow", u"Ver Ondas", None))
        self.test_results_label.setText(QCoreApplication.translate("MainWindow", u"Resultados del ensayo:", None))
        self.t2_label.setText(QCoreApplication.translate("MainWindow", u"T2 =", None))
        self.t2_unit.setText(QCoreApplication.translate("MainWindow", u" \u00b5s", None))
        self.os_label.setText(QCoreApplication.translate("MainWindow", u"OS =", None))
        self.peak_voltage_label.setText(QCoreApplication.translate("MainWindow", u"\u00dbt =", None))
        self.t1_label.setText(QCoreApplication.translate("MainWindow", u"T1 =", None))
        self.os_unit.setText(QCoreApplication.translate("MainWindow", u" %", None))
        self.peak_voltage_unit.setText(QCoreApplication.translate("MainWindow", u" kV", None))
        self.t1_unit.setText(QCoreApplication.translate("MainWindow", u" \u00b5s", None))
        self.test_label.setText(QCoreApplication.translate("MainWindow", u"Ensayo:", None))
        self.btn_save_waveform.setText(QCoreApplication.translate("MainWindow", u"Guardar", None))
        self.btn_wait_waveform.setText(QCoreApplication.translate("MainWindow", u"Iniciar", None))
        self.btn_export_results.setText(QCoreApplication.translate("MainWindow", u"Exportar", None))
        self.test_data_label.setText(QCoreApplication.translate("MainWindow", u"Datos del ensayo:", None))
        self.client_label.setText(QCoreApplication.translate("MainWindow", u"Cliente:", None))
        self.item_number_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"xxxx", None))
        self.date_label.setText(QCoreApplication.translate("MainWindow", u"Fecha:", None))
        self.date_value.setDisplayFormat(QCoreApplication.translate("MainWindow", u"dd/MM/yyyy", None))
        self.client_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Cliente", None))
        self.item_year_value.setPlaceholderText(QCoreApplication.translate("MainWindow", u"yy", None))
        self.item_label.setText(QCoreApplication.translate("MainWindow", u"Item N.\u00b0:", None))
        self.item_dash.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.btn_create_folder.setText(QCoreApplication.translate("MainWindow", u"Crear/Abrir Carpeta", None))
        self.system_attenuations_label.setText(QCoreApplication.translate("MainWindow", u"Atenuaciones del sistema:", None))
        self.attenuations_enabler.setText(QCoreApplication.translate("MainWindow", u"Editable", None))
        self.ch1_attenuation_label.setText(QCoreApplication.translate("MainWindow", u"CH1:", None))
        self.resistive_divider_label.setText(QCoreApplication.translate("MainWindow", u"Divisor resistivo =", None))
        self.attenuator_label.setText(QCoreApplication.translate("MainWindow", u"Atenuador =", None))
        self.ch2_attenuation_label.setText(QCoreApplication.translate("MainWindow", u"CH2:", None))
    # retranslateUi

