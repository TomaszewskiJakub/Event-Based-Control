from PySide2.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.simulator import Simulator, SimulatorThread
from controller.controller import Controller, ControllerThread
import sys

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    sim = Simulator()
    controller = Controller()

    # tmpapp = testApp()
    # tmptread = testThread(tmpapp)
    # tmptread.start()

    sim_thread = SimulatorThread(sim)
    sim_thread.start()

    controller_thread = ControllerThread(controller)

    sim.observable_que = controller.observable_que
    controller.controllable_que = sim.controllable_que

    sim.worldGenerated.connect(controller.init_all)

    win = MainWindow(sim, controller)
    win.startSignal.connect(controller_thread.start)

    win.show()

    sys.exit(qt_app.exec_())
