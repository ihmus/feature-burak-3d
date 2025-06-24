from Simulator3DWidget import Simulator3DWidget
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtGui import QKeyEvent
from physics import PhysicsSimulation, euler_to_quaternion
from objects.drone import Drone
from objects.Floor import Floor
from key_event_manager import QKeyEventManager
import sys



class MainScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulator_widget = Simulator3DWidget(self)
        
        self.setCentralWidget(self.simulator_widget)
        self.setWindowTitle("SCANE 3D Simulator")
        
        self.setGeometry(100, 100, 600, 800)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.installEventFilter(self)
    def show(self):
        super().show()
        self.simulator_widget.start_sim()
        
        
        
def main():
    app = QApplication(sys.argv)
    main_screen = MainScreen()
    main_screen.show()   
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    main()