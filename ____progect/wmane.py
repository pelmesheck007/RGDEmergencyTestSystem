from datetime import datetime
import PyQt6
import requests
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont
from PyQt6.QtWidgets import QWidget, QMessageBox
from connection import url


class MainWin(QWidget):
    """
    класс для создания главного окна
        методы
            __init__()
        функции:
           orientip()
           style()
           connect_b()
           set_text()
           people_sort()
           infa()
           keyPressEvent()
           hobby_ans()
           entry_open()
           hobby_add()
           hobby_user1()
           peop()
           recommendation()
           save()
           add_friend()
           add_friend()
           add_block()
           all_friends()
           chat_create()
           chat_open()
           msg()
    """

    def __init__(self, user):
        super().__init__()
        pix = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "8.png"]
        self.pixmap = [QPixmap('images1/' + path) for path in pix]
        self.user = user
        self.id_user, self.id_user2, self.name_user = user["id"], user["id"], user["nickname"]
        self.people = requests.get(f"{url}/peo?date={self.user['date_birth']}").json()
        self.people_cl = {}
        self.hobby_cl = {}
        self.hobby_clrev = {}
        self.hobby_ans()
        self.hobby_list = []
        self.people_create()
        self.ras = iter(self.people_sort())

        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tab_3 = QtWidgets.QWidget()
        self.btn_add_friend = QtWidgets.QPushButton(parent=self.tab_3)
        self.l_photo = QtWidgets.QLabel(parent=self.tab_3)
        self.l_nick = QtWidgets.QLabel(parent=self.tab_3)
        self.tb_about = QtWidgets.QTextBrowser(parent=self.tab_3)
        self.btn_next = QtWidgets.QPushButton(parent=self.tab_3)
        self.l_hobby_2 = QtWidgets.QLabel(parent=self.tab_3)
        self.l_hello = QtWidgets.QLabel(parent=self.tab_3)
        self.l_about1 = QtWidgets.QLabel(parent=self.tab_3)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QtWidgets.QWidget()
        self.pte_chat = QtWidgets.QTextEdit(parent=self.tab)
        self.btn_send = QtWidgets.QPushButton(parent=self.tab)
        self.le_text_send = QtWidgets.QLineEdit(parent=self.tab)
        self.cb_chat_open = QtWidgets.QComboBox(parent=self.tab)
        self.btn_add_chs = QtWidgets.QPushButton(parent=self.tab)
        self.tabWidget.addTab(self.tab, "")
        self.tab_4 = QtWidgets.QWidget()
        self.l_log = QtWidgets.QLabel(parent=self.tab_4)
        self.lin_log = QtWidgets.QLineEdit(parent=self.tab_4)
        self.l_pas = QtWidgets.QLabel(parent=self.tab_4)
        self.le_number = QtWidgets.QLineEdit(parent=self.tab_4)
        self.l_email = QtWidgets.QLabel(parent=self.tab_4)
        self.l_nick_2 = QtWidgets.QLabel(parent=self.tab_4)
        self.lin_pas = QtWidgets.QLineEdit(parent=self.tab_4)
        self.le_nick = QtWidgets.QLineEdit(parent=self.tab_4)
        self.l_number = QtWidgets.QLabel(parent=self.tab_4)
        self.le_email = QtWidgets.QLineEdit(parent=self.tab_4)
        self.l_about = QtWidgets.QLabel(parent=self.tab_4)
        self.te_about = QtWidgets.QTextEdit(parent=self.tab_4)
        self.l_hobby = QtWidgets.QLabel(parent=self.tab_4)
        self.cb_hobby = QtWidgets.QComboBox(parent=self.tab_4)
        self.btn_save = QtWidgets.QPushButton(parent=self.tab_4)
        self.btn_exit = QtWidgets.QPushButton(parent=self.tab_4)
        self.tb_hobby_user = QtWidgets.QTextBrowser(parent=self.tab_4)
        self.tb_hobby = QtWidgets.QTextBrowser(parent=self.tab_3)
        self.tabWidget.addTab(self.tab_4, "")
        self.tabWidget.setCurrentIndex(0)

        self.all_friends()
        self.ok = None
        self.set_text()
        self.style()
        self.connect_b()
        self.orientir()

    def orientir(self):
        """Определяет размеры объектов"""
        self.resize(537, 373)
        self.setFixedSize(self.size())
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 521, 361))
        self.tabWidget.setFocusPolicy(QtCore.Qt.FocusPolicy.WheelFocus)
        self.l_photo.setGeometry(QtCore.QRect(10, 10, 130, 131))
        self.l_nick.setGeometry(QtCore.QRect(150, 10, 350, 30))
        self.tb_about.setGeometry(QtCore.QRect(180, 80, 331, 192))
        self.btn_next.setGeometry(QtCore.QRect(370, 280, 141, 41))
        self.l_hobby_2.setGeometry(QtCore.QRect(30, 150, 91, 21))
        self.pte_chat.setGeometry(QtCore.QRect(10, 40, 481, 221))
        self.btn_add_friend.setGeometry(QtCore.QRect(210, 280, 149, 41))
        self.btn_send.setGeometry(QtCore.QRect(450, 280, 41, 41))
        self.le_text_send.setGeometry(QtCore.QRect(10, 280, 441, 41))
        self.cb_chat_open.setGeometry(QtCore.QRect(10, 10, 231, 25))
        self.btn_add_chs.setGeometry(QtCore.QRect(380, 10, 110, 25))
        self.l_log.setGeometry(QtCore.QRect(0, 190, 61, 21))
        self.lin_log.setGeometry(QtCore.QRect(0, 270, 171, 22))
        self.l_pas.setGeometry(QtCore.QRect(0, 250, 61, 21))
        self.le_number.setGeometry(QtCore.QRect(0, 90, 171, 21))
        self.l_email.setGeometry(QtCore.QRect(0, 130, 161, 21))
        self.l_nick_2.setGeometry(QtCore.QRect(0, 10, 61, 16))
        self.lin_pas.setGeometry(QtCore.QRect(0, 210, 171, 22))
        self.le_nick.setGeometry(QtCore.QRect(0, 30, 171, 21))
        self.l_number.setGeometry(QtCore.QRect(0, 70, 121, 21))
        self.le_email.setGeometry(QtCore.QRect(0, 150, 171, 21))
        self.te_about.setGeometry(QtCore.QRect(190, 150, 311, 121))
        self.l_about.setGeometry(QtCore.QRect(190, 130, 61, 21))
        self.l_hobby.setGeometry(QtCore.QRect(190, 10, 50, 21))
        self.cb_hobby.setGeometry(QtCore.QRect(190, 30, 311, 25))
        self.btn_save.setGeometry(QtCore.QRect(350, 290, 151, 30))
        self.btn_exit.setGeometry(QtCore.QRect(190, 290, 151, 30))
        self.tb_hobby_user.setGeometry(QtCore.QRect(190, 60, 311, 61))
        self.tb_hobby.setGeometry(QtCore.QRect(20, 180, 131, 141))
        self.l_hello.setGeometry(QtCore.QRect(70, 50, 440, 192))
        self.l_about1.setGeometry(QtCore.QRect(440, 50, 61, 21))
        self.pte_chat.raise_()
        self.le_text_send.raise_()
        self.btn_send.raise_()
        self.cb_chat_open.raise_()
        self.btn_add_chs.raise_()
        self.tb_hobby.close()
        self.btn_add_friend.close()
        self.l_hobby_2.close()
        self.tb_about.close()
        self.l_photo.close()
        self.l_about1.close()
        self.cb_hobby.addItems(self.hobby_ans())

        self.pte_chat.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def style(self):
        """Определяет стили объектов"""
        self.pte_chat.setStyleSheet("QPlainTextEdit {\n" "border: 1px solid black;\n" "}\n" "")
        self.font_f(self.tabWidget)
        self.font_f(self.pte_chat)
        self.font_f(self.btn_add_friend, 11)
        self.font_f(self.btn_save, 11)
        self.font_f(self.le_text_send)
        self.font_f(self.l_nick, 18)
        self.font_f(self.l_hello, 15)
        self.font_f(self.tb_hobby, 10)
        self.font_f(self.tb_about, 10)
        self.font_f(self.tb_hobby_user, 10)
        self.font_f(self.cb_hobby, 10)
        self.font_f(self.cb_chat_open, 11)
        self.font_f(self.btn_add_chs, 10)


        self.l_photo.setStyleSheet("QLabel {"
                             "border-style: solid;"
                             "border-width: 1px;"
                             "border-color: black; "
                             "}")
        self.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.tb_about.setStyleSheet("background-color: rgb(204, 204, 204);\n" "")
        self.tb_hobby.setStyleSheet("background-color: rgb(211, 211, 211);\n" "")

    def set_text(self):
        """Определяет текст для объектов"""
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "friend&comma"))
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.btn_add_friend.setText(_translate("MainWindow", "Добавить в друзья"))
        self.btn_next.setText(_translate("MainWindow", "Далее"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Рекомендации"))
        self.btn_send.setText(_translate("MainWindow", "->"))
        self.le_text_send.setPlaceholderText(_translate("MainWindow", "Текст сообщения.."))
        self.btn_add_chs.setText(_translate("MainWindow", "Добавить в чс"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Чат"))
        self.l_log.setText(_translate("MainWindow", "Логин"))
        self.l_pas.setText(_translate("MainWindow", "Пароль"))
        self.l_email.setText(_translate("MainWindow", "Электронная почта"))
        self.l_nick_2.setText(_translate("MainWindow", "Ник"))
        self.l_number.setText(_translate("MainWindow", "Номер телефона"))
        self.l_about.setText(_translate("MainWindow", "О себе"))
        self.l_hobby.setText(_translate("MainWindow", "Хобби"))
        self.btn_save.setText(_translate("MainWindow", "Сохранить"))
        self.btn_exit.setText(_translate("MainWindow", "Выйти"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Профиль"))
        self.l_hobby_2.setText(_translate("MainWindow", "Хобби"))
        self.l_about1.setText(_translate("MainWindow", "О себе"))
        self.l_photo.setText("")
        self.le_email.setText("")
        self.le_number.setText("")
        self.tb_hobby_user.setText("\n".join(self.hobby_user1(self.id_user)))
        self.l_hello.setText("Добро пожаловать! Начнем общение!\nНажмите кнопку \"далее\" для начала поиска.")

    def people_sort(self):
        """возвращает список отсортированных людей, которых нет в блоке или в друзьях"""
        people_sort = []
        hb1 = self.hobby_user1(self.user["id"])
        for c in self.people:
            data = {
                "id_user1": self.user["id"],
                "id_user2": c["id"]
            }
            if not (int(c["id"]) == int(self.id_user) or requests.get(f"{url}/proverkafr", json=data).json()):
                hb2 = self.hobby_user1(c["id"])
                s = 0
                for i in hb2:
                    if i in hb1:
                        s += 1
                c["count_hobby"] = s
                people_sort.append(c)
        people_sort = sorted(people_sort, key=lambda x: -x['count_hobby'])
        return people_sort

    def infa(self):
        """Определяет информацию для объектов полей ввода"""
        _translate = QtCore.QCoreApplication.translate
        self.lin_log.setText(_translate("MainWindow", str(self.user['login'])))
        self.lin_pas.setText(_translate("MainWindow", str(self.user['password'])))
        self.le_email.setText(_translate("MainWindow", str(self.user['email'])))
        self.le_nick.setText(_translate("MainWindow", str(self.user['nickname'])))
        self.te_about.setText(_translate("MainWindow", str(self.user['about_me'])))
        self.le_number.setText(_translate("MainWindow", str(self.user['number_phone'])))

    def connect_b(self):
        """Определяет подключение объектов"""
        self.btn_save.clicked.connect(self.save)
        self.btn_next.clicked.connect(self.recommendation)
        self.btn_add_friend.clicked.connect(self.add_friend)
        self.btn_send.clicked.connect(self.chat_create)
        self.btn_add_chs.clicked.connect(self.add_block)
        self.btn_exit.clicked.connect(self.entry_open)
        self.infa()
        self.cb_chat_open.activated.connect(self.chat_open)
        self.cb_hobby.activated.connect(self.hobby_add)
        return True

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Определяет нажатие по клавише enter"""
        if event.key() == QtCore.Qt.Key.Key_Enter or event.key() == QtCore.Qt.Key.Key_Return:
            self.btn_send.click()
        else:
            super().keyPressEvent(event)

    def hobby_ans(self):
        """Возвращает все хобби"""
        answer = requests.get(f"{url}/hobby")
        hobby = answer.json()
        for i in hobby:
            self.hobby_cl[i["name"]] = i["id"]
            self.hobby_clrev[i["id"]] = i["name"]
        return self.hobby_cl.keys()

    def hobby_add(self):
        """Добавляет новые хобби"""
        if self.cb_hobby.currentText() not in self.hobby_user1(self.id_user):
            hb_id = self.hobby_cl[self.cb_hobby.currentText()]
            data = {
                "id_user": self.id_user,
                "id_hobby": hb_id
            }
            requests.post(f"{url}/hobbyadd", json=data)
            self.hobby_list.append(self.cb_hobby.currentText())
            self.tb_hobby_user.setText("\n".join(self.hobby_user1(self.id_user)))

    def hobby_user1(self, user_id):
        """Возвращает список хобби по id пользователя"""
        answer = requests.get(f"{url}/hobbyuser?id_user={user_id}").json()
        if answer != {}:
            hb = []
            for i in answer:
                hb.append(self.hobby_clrev[i["id_hobby"]])
            return hb

    def people_create(self):
        """Создает словарь людей"""
        for i in self.people:
            self.people_cl[i["nickname"]] = i["id"]

    def recommendation(self):
        """Отображает рекомендации людей"""
        try:
            c = next(self.ras)
            self.btn_add_friend.show()
            self.tb_hobby.show()
            self.l_nick.show()
            self.l_hobby_2.show()
            self.tb_about.show()
            self.l_hello.close()
            self.l_photo.show()
            self.l_about1.show()
            self.tb_hobby.setText("\n".join(self.hobby_user1(int(c["id"]))))
            self.l_nick.setText(str(c['nickname']))
            self.tb_about.setText(str(c['about_me']))
            self.id_user2 = int(c['id'])
            self.l_photo.setPixmap(self.pixmap[int(c["photo"])-1])
        except:
            self.msg('Вы дошли до конца', "Вот задача")

    def entry_open(self):
        """Создает выход из профиля пользователя"""
        from entry import Entry
        self.ok = Entry()
        self.ok.show()
        self.close()

    def save(self):
        """Создает изменения данных профиля"""
        if (self.lin_pas.text() == "" or self.lin_log.text() == "" or self.le_email.text() == "" or self.le_nick.text() ==
                "" or self.te_about.toPlainText() == "" or self.le_number.text() == ""):
            self.msg('Поля не могут быть пустыми', "Вот задача")
        else:
            data = {
                "login": self.lin_log.text(),
                "password": self.lin_pas.text(),
                "nickname": self.le_nick.text(),
                "number_phone": self.le_number.text(),
                "email": self.le_email.text(),
                "about_me": self.te_about.toPlainText()
            }
            idd = self.user["id"]
            requests.put(f"{url}/update?user_id={idd}", json=data)

    def add_friend(self):
        """Добавляет новых друзей"""
        data = {
            "id_user1": self.user["id"],
            "id_user2": self.id_user2
        }

        if requests.get(f"{url}/proverkafr", json=data).json():
            self.msg('Друг уже добавлен', "Вот задача")
        else:
            data = {
                "id_user1": int(self.user["id"]),
                "id_user2": int(self.id_user2),
                "status": 1
            }

            requests.post(f"{url}/friendadd", json=data)
            self.all_friends()
            self.msg("Поздравляем! У Вас появился новый друг!!!", "Ура")

    def add_block(self):
        """Добавляет друзей в черный список"""
        id_user1 = int(self.user["id"])
        id_user2 = int(self.id_user)
        requests.put(f"{url}/updatefriend?id_user1={id_user1}&id_user2={id_user2}")
        requests.delete(f"{url}/chatdel/{id_user1}/{id_user2}")
        self.all_friends()
        self.chat_open()

    def all_friends(self):
        """Отображает список всех добавленных друзей в выподающий список"""
        self.cb_chat_open.clear()
        id = self.user["id"]
        answer = requests.get(f"{url}/myfriends?id_user={id}").json()
        self.cb_chat_open.addItem("Я")
        self.cb_chat_open.addItems(answer)

    def chat_create(self):
        """Добавляет новые сообщения в чате"""
        self.name_user = self.cb_chat_open.currentText()
        if self.name_user == "Я":
            self.id_user = self.user["id"]
        else:
            self.id_user = self.people_cl[self.name_user]
        if self.le_text_send.text() != "":
            data = {
                "id_sender": int(self.user["id"]),
                "id_recipient": int(self.id_user),
                "date": str(datetime.now().date()),
                "time": str(datetime.now().time().strftime('%H:%M:%S')),
                "message": self.le_text_send.text()
            }
            requests.post(f"{url}/chatot", json=data)
            self.chat_open()
            self.le_text_send.clear()

    def chat_open(self):
        """Отображает сообщения в чате"""
        idd = self.user["id"]
        self.name_user = self.cb_chat_open.currentText()
        if self.name_user == "Я":
            self.id_user = self.user["id"]
        else:
            self.id_user = self.people_cl[self.name_user]
        answer = requests.get(f"{url}/chat?id_sender={idd}&id_recipient={self.id_user}")
        messg = answer.json()
        mee = []
        for i in range(len(messg)):
            if messg[i]["id_sender"] == self.user["id"]:
                name = "Вы"
            else:
                name = self.name_user
            mee.append("\t\t\t\t" + messg[i]["time"] + "\n" + name + ": " + messg[i]["message"] + "\n")
        self.pte_chat.setText("\n".join(mee))
        cursor = self.pte_chat.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.pte_chat.setTextCursor(cursor)
        self.pte_chat.ensureCursorVisible()
        return "\n".join(mee)

    def font_f(self, xyu, size=12):
        id = QFontDatabase.addApplicationFont("ofont.ru_1Isadora M Bold.ttf")
        # id = QFontDatabase.addApplicationFont("ofont.ru_PF Wonderland Pro.ttf")
        if id < 0: print("Error")

        families = QFontDatabase.applicationFontFamilies(id)
        xyu.setFont(QFont(families[0], size))

    def msg(self, s1, s2):
        """Создает окно сообщения"""
        msg = QMessageBox(self)
        msg.setText(s1)
        msg.setWindowTitle(s2)
        msg.exec()
