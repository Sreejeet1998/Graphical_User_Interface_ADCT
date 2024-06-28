import os, sys
from PyQt5.QtWidgets import QApplication, QPushButton
import warnings
import GUIWINDOW

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from INTERNAL_SCENE.calc_window import ADCTWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = ADCTWindow()
    warnings.filterwarnings("ignore")
    wnd.show()

    sys.exit(app.exec_())
