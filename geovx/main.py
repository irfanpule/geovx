from PyQt5.QtWidgets import QApplication
from geovx.app import GeoVXMainWindow
import sys


def main():
    app = QApplication(sys.argv)
    main_window = GeoVXMainWindow()
    main_window.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')


if __name__ == '__main__':
    main()
