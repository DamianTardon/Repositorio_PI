# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu1.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QFormLayout, QGridLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPlainTextEdit, QRadioButton,
    QSizePolicy, QStatusBar, QWidget)

from pyqtgraph import PlotWidget

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1920, 1080)
        self.centralwidget = QWidget(Form)
        self.centralwidget.setObjectName(u"centralwidget")
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(430, 40, 900, 661))
        self.label_16 = QLabel(self.centralwidget)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(30, 350, 211, 17))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(12)
        font.setBold(True)
        self.label_16.setFont(font)
        self.label_17 = QLabel(self.centralwidget)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(30, 480, 271, 17))
        self.label_17.setFont(font)
        self.label_26 = QLabel(self.centralwidget)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(30, 10, 151, 17))
        self.label_26.setFont(font)
        self.radioButton_7 = QRadioButton(self.centralwidget)
        self.radioButton_7.setObjectName(u"radioButton_7")
        self.radioButton_7.setGeometry(QRect(2390, 150, 61, 20))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(12)
        self.radioButton_7.setFont(font1)
        self.radioButton_8 = QRadioButton(self.centralwidget)
        self.radioButton_8.setObjectName(u"radioButton_8")
        self.radioButton_8.setGeometry(QRect(2270, 150, 111, 20))
        self.radioButton_8.setFont(font1)
        self.label_44 = QLabel(self.centralwidget)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setGeometry(QRect(1360, 10, 191, 17))
        self.label_44.setFont(font)
        self.radioButton_9 = QRadioButton(self.centralwidget)
        self.radioButton_9.setObjectName(u"radioButton_9")
        self.radioButton_9.setGeometry(QRect(2690, 210, 111, 20))
        self.radioButton_9.setFont(font1)
        self.label_27 = QLabel(self.centralwidget)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(30, 200, 211, 17))
        self.label_27.setFont(font)
        self.label_34 = QLabel(self.centralwidget)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(430, 10, 161, 17))
        self.label_34.setFont(font)
        self.label_46 = QLabel(self.centralwidget)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setGeometry(QRect(1360, 150, 191, 17))
        self.label_46.setFont(font)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(1360, 180, 231, 161))
        self.gridLayout_2 = QGridLayout(self.widget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_22 = QLabel(self.widget)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setFont(font1)

        self.gridLayout_2.addWidget(self.label_22, 2, 0, 1, 1)

        self.label_25 = QLabel(self.widget)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setFont(font1)
        self.label_25.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_25, 3, 2, 1, 1)

        self.label_19 = QLabel(self.widget)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setFont(font1)
        self.label_19.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_19, 0, 2, 1, 1)

        self.label_23 = QLabel(self.widget)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setFont(font1)
        self.label_23.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_23, 2, 2, 1, 1)

        self.label_20 = QLabel(self.widget)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font1)

        self.gridLayout_2.addWidget(self.label_20, 1, 0, 1, 1)

        self.label_18 = QLabel(self.widget)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setEnabled(True)
        self.label_18.setFont(font1)

        self.gridLayout_2.addWidget(self.label_18, 0, 0, 1, 1)

        self.label_24 = QLabel(self.widget)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setFont(font1)

        self.gridLayout_2.addWidget(self.label_24, 3, 0, 1, 1)

        self.label_21 = QLabel(self.widget)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setFont(font1)
        self.label_21.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_21, 1, 2, 1, 1)

        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setFont(font1)
        self.lineEdit.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.lineEdit_2 = QLineEdit(self.widget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setFont(font1)
        self.lineEdit_2.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.lineEdit_3 = QLineEdit(self.widget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setFont(font1)
        self.lineEdit_3.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit_3, 2, 1, 1, 1)

        self.lineEdit_4 = QLineEdit(self.widget)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setFont(font1)
        self.lineEdit_4.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit_4, 3, 1, 1, 1)

        self.widget1 = QWidget(self.centralwidget)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(30, 40, 311, 131))
        self.formLayout = QFormLayout(self.widget1)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget1)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.plainTextEdit = QPlainTextEdit(self.widget1)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setFont(font1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.plainTextEdit)

        self.label_6 = QLabel(self.widget1)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.plainTextEdit_2 = QPlainTextEdit(self.widget1)
        self.plainTextEdit_2.setObjectName(u"plainTextEdit_2")
        self.plainTextEdit_2.setFont(font1)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.plainTextEdit_2)

        self.label_7 = QLabel(self.widget1)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font1)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.plainTextEdit_3 = QPlainTextEdit(self.widget1)
        self.plainTextEdit_3.setObjectName(u"plainTextEdit_3")
        self.plainTextEdit_3.setFont(font1)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.plainTextEdit_3)

        self.label_4 = QLabel(self.widget1)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.dateEdit = QDateEdit(self.widget1)
        self.dateEdit.setObjectName(u"dateEdit")
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(11)
        self.dateEdit.setFont(font2)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateEdit)

        self.widget2 = QWidget(self.centralwidget)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setGeometry(QRect(30, 381, 311, 71))
        self.gridLayout = QGridLayout(self.widget2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.plainTextEdit_4 = QPlainTextEdit(self.widget2)
        self.plainTextEdit_4.setObjectName(u"plainTextEdit_4")
        self.plainTextEdit_4.setFont(font1)

        self.gridLayout.addWidget(self.plainTextEdit_4, 0, 1, 1, 1)

        self.checkBox = QCheckBox(self.widget2)
        self.checkBox.setObjectName(u"checkBox")
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setPointSize(10)
        self.checkBox.setFont(font3)

        self.gridLayout.addWidget(self.checkBox, 0, 2, 1, 1)

        self.label_3 = QLabel(self.widget2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.plainTextEdit_5 = QPlainTextEdit(self.widget2)
        self.plainTextEdit_5.setObjectName(u"plainTextEdit_5")
        self.plainTextEdit_5.setFont(font1)

        self.gridLayout.addWidget(self.plainTextEdit_5, 1, 1, 1, 1)

        self.checkBox_2 = QCheckBox(self.widget2)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setFont(font3)

        self.gridLayout.addWidget(self.checkBox_2, 1, 2, 1, 1)

        self.widget3 = QWidget(self.centralwidget)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setGeometry(QRect(30, 510, 357, 156))
        self.gridLayout_5 = QGridLayout(self.widget3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_31 = QLabel(self.widget3)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setFont(font1)

        self.gridLayout_5.addWidget(self.label_31, 0, 1, 1, 2)

        self.label_28 = QLabel(self.widget3)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setFont(font1)

        self.gridLayout_5.addWidget(self.label_28, 0, 3, 1, 2)

        self.label_30 = QLabel(self.widget3)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setFont(font1)

        self.gridLayout_5.addWidget(self.label_30, 1, 0, 1, 1)

        self.comboBox_27 = QComboBox(self.widget3)
        self.comboBox_27.setObjectName(u"comboBox_27")

        self.gridLayout_5.addWidget(self.comboBox_27, 1, 1, 1, 1)

        self.comboBox_28 = QComboBox(self.widget3)
        self.comboBox_28.setObjectName(u"comboBox_28")

        self.gridLayout_5.addWidget(self.comboBox_28, 1, 2, 1, 1)

        self.comboBox_31 = QComboBox(self.widget3)
        self.comboBox_31.setObjectName(u"comboBox_31")

        self.gridLayout_5.addWidget(self.comboBox_31, 1, 3, 1, 1)

        self.comboBox_29 = QComboBox(self.widget3)
        self.comboBox_29.setObjectName(u"comboBox_29")

        self.gridLayout_5.addWidget(self.comboBox_29, 1, 4, 1, 1)

        self.label_29 = QLabel(self.widget3)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setFont(font1)

        self.gridLayout_5.addWidget(self.label_29, 2, 0, 1, 1)

        self.comboBox_32 = QComboBox(self.widget3)
        self.comboBox_32.setObjectName(u"comboBox_32")

        self.gridLayout_5.addWidget(self.comboBox_32, 2, 1, 1, 1)

        self.comboBox_25 = QComboBox(self.widget3)
        self.comboBox_25.setObjectName(u"comboBox_25")

        self.gridLayout_5.addWidget(self.comboBox_25, 2, 2, 1, 1)

        self.comboBox_30 = QComboBox(self.widget3)
        self.comboBox_30.setObjectName(u"comboBox_30")

        self.gridLayout_5.addWidget(self.comboBox_30, 2, 3, 1, 1)

        self.comboBox_26 = QComboBox(self.widget3)
        self.comboBox_26.setObjectName(u"comboBox_26")

        self.gridLayout_5.addWidget(self.comboBox_26, 2, 4, 1, 1)

        self.label_53 = QLabel(self.widget3)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setFont(font1)

        self.gridLayout_5.addWidget(self.label_53, 3, 1, 1, 1)

        self.label_51 = QLabel(self.widget3)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setFont(font1)

        self.gridLayout_5.addWidget(self.label_51, 3, 2, 1, 1)

        self.label_54 = QLabel(self.widget3)
        self.label_54.setObjectName(u"label_54")
        self.label_54.setFont(font1)

        self.gridLayout_5.addWidget(self.label_54, 4, 0, 1, 1)

        self.comboBox_73 = QComboBox(self.widget3)
        self.comboBox_73.setObjectName(u"comboBox_73")
        self.comboBox_73.setFont(font2)

        self.gridLayout_5.addWidget(self.comboBox_73, 4, 1, 1, 1)

        self.comboBox_70 = QComboBox(self.widget3)
        self.comboBox_70.setObjectName(u"comboBox_70")
        self.comboBox_70.setFont(font2)

        self.gridLayout_5.addWidget(self.comboBox_70, 4, 2, 1, 1)

        self.label_52 = QLabel(self.widget3)
        self.label_52.setObjectName(u"label_52")
        self.label_52.setFont(font1)

        self.gridLayout_5.addWidget(self.label_52, 5, 0, 1, 1)

        self.comboBox_72 = QComboBox(self.widget3)
        self.comboBox_72.setObjectName(u"comboBox_72")
        self.comboBox_72.setFont(font2)

        self.gridLayout_5.addWidget(self.comboBox_72, 5, 1, 1, 1)

        self.comboBox_71 = QComboBox(self.widget3)
        self.comboBox_71.setObjectName(u"comboBox_71")
        self.comboBox_71.setFont(font2)

        self.gridLayout_5.addWidget(self.comboBox_71, 5, 2, 1, 1)

        self.widget4 = QWidget(self.centralwidget)
        self.widget4.setObjectName(u"widget4")
        self.widget4.setGeometry(QRect(30, 690, 285, 52))
        self.gridLayout_6 = QGridLayout(self.widget4)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_56 = QLabel(self.widget4)
        self.label_56.setObjectName(u"label_56")
        self.label_56.setFont(font1)

        self.gridLayout_6.addWidget(self.label_56, 0, 0, 1, 1)

        self.radioButton_12 = QRadioButton(self.widget4)
        self.radioButton_12.setObjectName(u"radioButton_12")
        self.radioButton_12.setFont(font1)

        self.gridLayout_6.addWidget(self.radioButton_12, 0, 1, 1, 1)

        self.label_55 = QLabel(self.widget4)
        self.label_55.setObjectName(u"label_55")
        self.label_55.setFont(font1)

        self.gridLayout_6.addWidget(self.label_55, 0, 2, 1, 1)

        self.comboBox_74 = QComboBox(self.widget4)
        self.comboBox_74.setObjectName(u"comboBox_74")
        self.comboBox_74.setFont(font2)

        self.gridLayout_6.addWidget(self.comboBox_74, 0, 3, 1, 1)

        self.radioButton_13 = QRadioButton(self.widget4)
        self.radioButton_13.setObjectName(u"radioButton_13")
        self.radioButton_13.setFont(font1)

        self.gridLayout_6.addWidget(self.radioButton_13, 1, 1, 1, 1)

        self.widget5 = QWidget(self.centralwidget)
        self.widget5.setObjectName(u"widget5")
        self.widget5.setGeometry(QRect(1360, 40, 231, 50))
        self.gridLayout_7 = QGridLayout(self.widget5)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_45 = QLabel(self.widget5)
        self.label_45.setObjectName(u"label_45")
        font4 = QFont()
        font4.setFamilies([u"Arial"])
        font4.setPointSize(12)
        font4.setBold(False)
        self.label_45.setFont(font4)

        self.gridLayout_7.addWidget(self.label_45, 0, 0, 1, 1)

        self.radioButton_6 = QRadioButton(self.widget5)
        self.radioButton_6.setObjectName(u"radioButton_6")
        self.radioButton_6.setFont(font1)

        self.gridLayout_7.addWidget(self.radioButton_6, 0, 1, 1, 1)

        self.radioButton_5 = QRadioButton(self.widget5)
        self.radioButton_5.setObjectName(u"radioButton_5")
        self.radioButton_5.setFont(font1)

        self.gridLayout_7.addWidget(self.radioButton_5, 1, 1, 1, 1)

        self.widget6 = QWidget(self.centralwidget)
        self.widget6.setObjectName(u"widget6")
        self.widget6.setGeometry(QRect(30, 231, 311, 101))
        self.gridLayout_4 = QGridLayout(self.widget6)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.widget6)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.plainTextEdit_9 = QPlainTextEdit(self.widget6)
        self.plainTextEdit_9.setObjectName(u"plainTextEdit_9")
        self.plainTextEdit_9.setFont(font1)

        self.gridLayout_4.addWidget(self.plainTextEdit_9, 0, 1, 1, 1)

        self.label_32 = QLabel(self.widget6)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setFont(font1)
        self.label_32.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_4.addWidget(self.label_32, 0, 2, 1, 1)

        self.label_38 = QLabel(self.widget6)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setFont(font1)

        self.gridLayout_4.addWidget(self.label_38, 1, 0, 1, 1)

        self.plainTextEdit_10 = QPlainTextEdit(self.widget6)
        self.plainTextEdit_10.setObjectName(u"plainTextEdit_10")
        self.plainTextEdit_10.setFont(font1)

        self.gridLayout_4.addWidget(self.plainTextEdit_10, 1, 1, 1, 1)

        self.label_37 = QLabel(self.widget6)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setFont(font1)
        self.label_37.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_4.addWidget(self.label_37, 1, 2, 1, 1)

        self.label_39 = QLabel(self.widget6)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setFont(font1)

        self.gridLayout_4.addWidget(self.label_39, 2, 0, 1, 1)

        self.plainTextEdit_11 = QPlainTextEdit(self.widget6)
        self.plainTextEdit_11.setObjectName(u"plainTextEdit_11")
        self.plainTextEdit_11.setFont(font1)

        self.gridLayout_4.addWidget(self.plainTextEdit_11, 2, 1, 1, 1)

        self.label_33 = QLabel(self.widget6)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setFont(font1)
        self.label_33.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_4.addWidget(self.label_33, 2, 2, 1, 1)

        Form.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Form)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1920, 22))
        Form.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Form)
        self.statusbar.setObjectName(u"statusbar")
        Form.setStatusBar(self.statusbar)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"Atenuaciones del sistema:", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Configuraciones del osciloscopio:", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"Datos del ensayo:", None))
        self.radioButton_7.setText(QCoreApplication.translate("Form", u"Real", None))
        self.radioButton_8.setText(QCoreApplication.translate("Form", u"Normalizada", None))
        self.label_44.setText(QCoreApplication.translate("Form", u"Resultados del ensayo:", None))
        self.radioButton_9.setText(QCoreApplication.translate("Form", u"Normalizada", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"Condiciones ambientales:", None))
        self.label_34.setText(QCoreApplication.translate("Form", u"Gr\u00e1fico del impulso:", None))
        self.label_46.setText(QCoreApplication.translate("Form", u"Par\u00e1metros del impulso:", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"T2 =", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"%", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"kV", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"\u00b5s", None))
        self.label_20.setText(QCoreApplication.translate("Form", u"T1 =", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"\u00dbe =", None))
        self.label_24.setText(QCoreApplication.translate("Form", u"OS =", None))
        self.label_21.setText(QCoreApplication.translate("Form", u"\u00b5s", None))
        self.label.setText(QCoreApplication.translate("Form", u"Item N.\u00b0:", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Cliente:", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Onda N.\u00b0:", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Fecha:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Divisor resistivo:", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Editable", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Atenuador:", None))
        self.checkBox_2.setText(QCoreApplication.translate("Form", u"Editable", None))
        self.label_31.setText(QCoreApplication.translate("Form", u"Escala vertical:", None))
        self.label_28.setText(QCoreApplication.translate("Form", u"Escala horizontal:", None))
        self.label_30.setText(QCoreApplication.translate("Form", u"CH1:", None))
        self.label_29.setText(QCoreApplication.translate("Form", u"CH2:", None))
        self.label_53.setText(QCoreApplication.translate("Form", u"Posici\u00f3n X:", None))
        self.label_51.setText(QCoreApplication.translate("Form", u"Posici\u00f3n Y:", None))
        self.label_54.setText(QCoreApplication.translate("Form", u"CH1:", None))
        self.label_52.setText(QCoreApplication.translate("Form", u"CH2:", None))
        self.label_56.setText(QCoreApplication.translate("Form", u"Flanco:", None))
        self.radioButton_12.setText(QCoreApplication.translate("Form", u"Positivo", None))
        self.label_55.setText(QCoreApplication.translate("Form", u"Trigger:", None))
        self.radioButton_13.setText(QCoreApplication.translate("Form", u"Negativo", None))
        self.label_45.setText(QCoreApplication.translate("Form", u"Tipo de gr\u00e1fico:", None))
        self.radioButton_6.setText(QCoreApplication.translate("Form", u"Real", None))
        self.radioButton_5.setText(QCoreApplication.translate("Form", u"Normalizado", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Temperatura =", None))
        self.label_32.setText(QCoreApplication.translate("Form", u"\u00b0C", None))
        self.label_38.setText(QCoreApplication.translate("Form", u"Humedad Relativa =", None))
        self.label_37.setText(QCoreApplication.translate("Form", u"%", None))
        self.label_39.setText(QCoreApplication.translate("Form", u"Presi\u00f3n Atmosf\u00e9rica =", None))
        self.label_33.setText(QCoreApplication.translate("Form", u"hPa", None))
    # retranslateUi

