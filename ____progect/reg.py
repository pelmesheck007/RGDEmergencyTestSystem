from random import randint
import requests
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QMessageBox
from connection import url
from icon import IconW

class Reg(QWidget):
    """
    класс для создания окна регистрации
       методы
            __init__()
       функции:
           orientip()
           style()
           connect_b()
           set_text()
           registration()
           entry_open()
           msg()

        """
    def __init__(self):
        super().__init__()
        self.hobby_cl = {}
        pix = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "8.png", "9.png"]
        self.pixmap = [QtGui.QIcon('images1/' + path) for path in pix]
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.le_nick = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.l_reg = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_nick = QtWidgets.QLabel(parent=self.centralwidget)
        self.le_number = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.l_nuber = QtWidgets.QLabel(parent=self.centralwidget)
        self.le_email = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.l_email = QtWidgets.QLabel(parent=self.centralwidget)
        self.dateEdit = QtWidgets.QDateEdit(parent=self.centralwidget)
        self.l_dateb = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_pol = QtWidgets.QLabel(parent=self.centralwidget)
        self.rb_man = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.rb_woman = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.lab_aboutme = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_12 = QtWidgets.QLabel(parent=self.centralwidget)
        self.btn_reg = QtWidgets.QPushButton(parent=self.centralwidget)
        self.te_about = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.le_pass = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.l_log = QtWidgets.QLabel(parent=self.centralwidget)
        self.l_pas = QtWidgets.QLabel(parent=self.centralwidget)
        self.le_log = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.btn_back = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_icon = QtWidgets.QPushButton(parent=self.centralwidget)
        self.l_photo = QtWidgets.QPushButton(parent=self.centralwidget)
        self.entry = None
        self.icon = IconW()
        self.icon.sig.connect(self.icon_set)
        self.set_text()
        self.style()
        self.connect_b()
        self.orientir()
        self.photo = 0



    def orientir(self):
        """Определяет размеры объектов"""
        self.resize(600, 425)
        self.setFixedSize(self.size())
        self.le_nick.setGeometry(QtCore.QRect(10, 90, 180, 21))
        self.l_reg.setGeometry(QtCore.QRect(180, 0, 241, 61))
        self.l_nick.setGeometry(QtCore.QRect(10, 70, 61, 16))
        self.le_number.setGeometry(QtCore.QRect(10, 150, 171, 21))
        self.l_nuber.setGeometry(QtCore.QRect(10, 130, 121, 21))
        self.le_email.setGeometry(QtCore.QRect(10, 210, 180, 21))
        self.l_email.setGeometry(QtCore.QRect(10, 190, 160, 21))
        self.dateEdit.setGeometry(QtCore.QRect(10, 270, 110, 22))
        self.l_dateb.setGeometry(QtCore.QRect(10, 240, 125, 29))
        self.l_pol.setGeometry(QtCore.QRect(20, 300, 60, 31))
        self.rb_man.setGeometry(QtCore.QRect(10, 330, 95, 20))
        self.rb_woman.setGeometry(QtCore.QRect(10, 350, 95, 20))
        self.lab_aboutme.setGeometry(QtCore.QRect(200, 190, 50, 21))
        self.label_12.setGeometry(QtCore.QRect(390, 70, 41, 21))
        self.btn_reg.setGeometry(QtCore.QRect(210, 370, 171, 41))
        self.te_about.setGeometry(QtCore.QRect(200, 210, 391, 121))
        self.le_pass.setGeometry(QtCore.QRect(200, 150, 161, 22))
        self.l_log.setGeometry(QtCore.QRect(200, 70, 120, 21))
        self.l_pas.setGeometry(QtCore.QRect(200, 130, 130, 21))
        self.le_log.setGeometry(QtCore.QRect(200, 90, 161, 22))
        self.btn_back.setGeometry(QtCore.QRect(10, 10, 35, 35))
        self.btn_icon.setGeometry(QtCore.QRect(400, 150, 150, 35))
        self.l_photo.setGeometry(QtCore.QRect(430, 50, 90, 91))
        self.l_photo.setIcon(self.pixmap[0])
        self.l_photo.setIconSize(QtCore.QSize(89, 90))


    def style(self):
        """Определяет стили объектов"""
        self.font_f(self.centralwidget)
        self.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.font_f(self.l_reg, 22)
        self.font_f(self.le_log, 11)
        self.font_f(self.le_pass, 11)
        self.font_f(self.le_nick, 11)
        self.font_f(self.le_email, 11)
        self.font_f(self.le_number, 11)
        self.font_f(self.te_about, 11)
        self.font_f(self.btn_back, 15)

    def icon_set(self, res):
        self.photo = res
        self.l_photo.setIcon(self.pixmap[self.photo])
        self.l_photo.setIconSize(QtCore.QSize(89, 90))

    def icon_open(self):
        self.icon.show()

    def connect_b(self):
        """Определяет подключение объектов"""
        self.btn_reg.clicked.connect(self.registration)
        self.btn_back.clicked.connect(self.entry_open2)
        self.btn_icon.clicked.connect(self.icon_open)

    def set_text(self):
        """Определяет отображаемый текст объектов"""
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "friend&comma"))
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.l_reg.setText(_translate("MainWindow", "Регистрация"))
        self.l_nick.setText(_translate("MainWindow", "Ник"))
        self.l_nuber.setText(_translate("MainWindow", "Номер телефона"))
        self.l_email.setText(_translate("MainWindow", "Электронная почта"))
        self.l_dateb.setText(_translate("MainWindow", "Дата рождения"))
        self.l_pol.setText(_translate("MainWindow", "Пол"))
        self.rb_man.setText(_translate("MainWindow", "мужчина"))
        self.rb_woman.setText(_translate("MainWindow", "женщина"))
        self.lab_aboutme.setText(_translate("MainWindow", "О себе"))
        self.btn_reg.setText(_translate("MainWindow", "Зарегистрироваться"))
        self.l_log.setText(_translate("MainWindow", "Введите логин"))
        self.l_pas.setText(_translate("MainWindow", "Введите пароль"))
        self.le_number.setText("")
        self.le_email.setText("")
        self.btn_back.setText("<-")
        self.btn_icon.setText("Выбрать фотку")

    def entry_open2(self):
        """Создает переход на окно входа"""
        from entry import Entry
        self.entry = Entry()
        self.close()
        self.entry.show()


    def registration(self):
        """Создает пользователя и делает переход в главное окно"""
        if (self.le_pass.text() == "" or self.le_log.text() == "" or self.le_nick.text() == "" or self.le_number.text()
                == "" or self.le_number.text() == "" or self.le_email.text() == "" or self.te_about.toPlainText() == ""
                or (self.rb_man.isChecked() == False and self.rb_woman.isChecked() == False)):
            self.msg('Поля не могут быть пустыми', "Вот задача")
        else:
            data = {
                "login": self.le_log.text(),
                "nickname": self.le_nick.text()
            }
            if requests.get(f"{url}/proverka", json=data).json():
                self.msg('Такой пользователь уже существует', "Вот задача")
            else:
                if self.rb_woman.isChecked():
                    pol = 1
                else:
                    pol = 0
                data = {
                    "login": self.le_log.text(),
                    "password": self.le_pass.text(),
                    "nickname": self.le_nick.text(),
                    "number_phone": self.le_number.text(),
                    "email": self.le_email.text(),
                    "about_me": self.te_about.toPlainText(),
                    "gender": pol,
                    "photo": self.photo,
                    "date_birth": str(self.dateEdit.date().toPyDate())
                }
                requests.post(f"{url}/reg", json=data)
                self.entry_open()

    def entry_open(self):
        """Создает переход на окно входа"""
        from entry import Entry
        self.entry = Entry()
        self.entry.lin_log.setText(self.le_log.text())
        self.entry.lin_pas.setText(self.le_pass.text())
        self.entry.login()
        self.close()

    def msg(self, s1, s2):
        """Создает окно сообщения"""
        msg = QMessageBox(self)
        msg.setText(s1)
        msg.setWindowTitle(s2)
        msg.exec()

    def font_f(self, xyu, size=12):
        id = QFontDatabase.addApplicationFont("ofont.ru_1Isadora M Bold.ttf")
        # id = QFontDatabase.addApplicationFont("ofont.ru_PF Wonderland Pro.ttf")
        if id < 0: print("Error")

        families = QFontDatabase.applicationFontFamilies(id)
        xyu.setFont(QFont(families[0], size))
