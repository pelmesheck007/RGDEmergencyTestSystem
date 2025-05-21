from PyQt6 import QtWidgets
from entry import Entry


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Entry()
    ui.show()
    sys.exit(app.exec())
