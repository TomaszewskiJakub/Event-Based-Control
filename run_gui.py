from PySide2.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.simulator import Simulator, SimulatorThread, Controller 
import sys

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    sim = Simulator()
    win = MainWindow(sim)
    win.show()

    controller = Controller(sim.trees)
    sys.exit(qt_app.exec_())
