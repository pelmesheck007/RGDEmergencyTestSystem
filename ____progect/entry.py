from PyQt6.QtGui import QFontDatabase
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QMessageBox
import requests
from connection import url


class Entry(QWidget):
    """
    класс для создания окна входа
       методы
            __init__()
       функции:
           orientip()
           style()
           connect_b()
           set_text()
           keyPressEvent()
           login()
           reg_open()
    """

    def __init__(self):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.l_entry = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_log = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_pas = QtWidgets.QLabel(parent=self.centralwidget)
        self.lin_log = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lin_pas = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.btn_entry = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_reg = QtWidgets.QPushButton(parent=self.centralwidget)
        self.l_photo = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_photo.setPixmap(QtGui.QPixmap("images1/icon1.png"))
        self.ok1 = None
        self.ok2 = None
        self.set_text()
        self.connect_b()
        self.orientir()
        self.style()


    def orientir(self):
        """Определяет размеры объектов"""
        self.resize(400, 280)
        self.setFixedSize(self.size())
        self.l_entry.setGeometry(QtCore.QRect(110, 2, 220, 60))
        self.l_log.setGeometry(QtCore.QRect(20, 50, 120, 21))
        self.l_pas.setGeometry(QtCore.QRect(20, 100, 120, 21))
        self.lin_log.setGeometry(QtCore.QRect(20, 70, 161, 22))
        self.lin_pas.setGeometry(QtCore.QRect(20, 120, 161, 22))
        self.btn_entry.setGeometry(QtCore.QRect(140, 170, 100, 40))
        self.btn_reg.setGeometry(QtCore.QRect(120, 220, 141, 28))
        self.l_photo.setGeometry(QtCore.QRect(250, 60, 120, 120))

    def style(self):
        """Определяет стили объектов"""
        self.font_f(self.centralwidget)
        self.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.font_f(self.btn_reg, 10)
        self.font_f(self.l_log, 11)
        self.font_f(self.lin_pas, 11)
        self.font_f(self.lin_log, 11)
        self.font_f(self.l_pas, 11)
        self.font_f(self.l_entry, 23)



    def connect_b(self):
        """Определяет подключение объектов"""
        self.btn_entry.clicked.connect(self.login)
        self.btn_reg.clicked.connect(self.reg_open)

    def set_text(self):
        """Определяет отображаемый текст объектов"""
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "friend&comma"))
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.l_entry.setText(_translate("win_entry2", "friend&comma"))
        self.l_log.setText(_translate("win_entry2", "Введите логин"))
        self.l_pas.setText(_translate("win_entry2", "Введите пароль"))
        self.btn_entry.setText(_translate("win_entry2", "Войти"))
        self.btn_reg.setText(_translate("win_entry2", "Зарегистрироваться"))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Определяет нажатие по клавише enter"""
        if event.key() == QtCore.Qt.Key.Key_Enter or event.key() == QtCore.Qt.Key.Key_Return:
            self.btn_entry.click()
        else:
            super().keyPressEvent(event)

    def font_f(self, xyu, size=12):
        id = QFontDatabase.addApplicationFont("ofont.ru_1Isadora M Bold.ttf")
        # id = QFontDatabase.addApplicationFont("ofont.ru_PF Wonderland Pro.ttf")
        if id < 0: print("Error")

        families = QFontDatabase.applicationFontFamilies(id)
        xyu.setFont(QFont(families[0], size))

    def login(self):
        """Создает переход на главное окно"""
        if requests.get(f"{url}/auf?login={self.lin_log.text()}&password={self.lin_pas.text()}"):
            answer = requests.get(f"{url}/auf?login={self.lin_log.text()}&password={self.lin_pas.text()}")
            from wmane import MainWin

            self.ok1 = MainWin(answer.json())
            self.ok1.show()
            self.close()
        else:
            self.msg("Такого пользователя не существует", "Вот задача")

    def reg_open(self):
        """Создает переход на окно регистрации"""
        from reg import Reg
        self.ok2 = Reg()
        self.ok2.show()
        self.close()

    def msg(self, s1, s2):
        """Создает окно сообщения"""
        msg = QMessageBox(self)
        msg.setText(s1)
        msg.setWindowTitle(s2)
        msg.exec()

