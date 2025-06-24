from cgitb import text
from importlib.util import module_for_loader
import math
import os
import sys
import pybullet as p
import pybullet_data

from physics import Floor, Model, PhysicsSimulation, Drone 

from key_event_manager import KeyEventManager, QKeyEventManager
from objects.Camera import Camera

from PyQt5.QtWidgets       import QApplication, QComboBox, QDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget,QHBoxLayout,QInputDialog
from PyQt5.QtCore          import QTimer, QUrl, Qt
from PyQt5.Qt3DCore        import QEntity, QTransform
from PyQt5.Qt3DExtras      import QOrbitCameraController
from PyQt5.Qt3DExtras      import QDiffuseMapMaterial,Qt3DWindow
from PyQt5.Qt3DRender      import QMesh,QTexture2D, QTextureImage
from PyQt5.QtGui           import QVector3D, QQuaternion, QMatrix4x4
from PyQt5.Qt3DRender import QPointLight

from rqt_gauges.bar_gauge import QLabel


            
def euler_to_quaternion(x:float,y:float,z:float):
    """Eğik açılarından quaternion'a dönüşüm."""
    
    cy = math.cos(z * 0.5)
    sy = math.sin(z * 0.5)
    cp = math.cos(y * 0.5)
    sp = math.sin(y * 0.5)
    cr = math.cos(x * 0.5)
    sr = math.sin(x * 0.5)

    return (
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy
        )    



class Simulator3DWidget(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.setGeometry(100, 100, 100, 100)
        
        self.sim_window = Simulator3DWindow(parent)
        self.container = QWidget.createWindowContainer(self.sim_window, self)
        
        
        self.vertBoxLayout = QVBoxLayout(self)
        self.horiBoxLayout = QHBoxLayout(self)
        self.add_model_btn = QPushButton("Add Model Simulation")
        self.add_model_btn.clicked.connect(self.add_model_clicked)        
        self.horiBoxLayout.addWidget(self.add_model_btn)
        self.vertBoxLayout.addWidget(self.container)
        self.vertBoxLayout.addLayout(self.horiBoxLayout)
        self.models = {
            
        }

        self.add_model(
                    "floor",
                    Floor(physics_client=self.sim_window.client),
                    position=(0, 0, 0),
                    orientation=(euler_to_quaternion(0,0,math.pi)))  # Zemin düz bir yüzey olarak ayarlanır

        
        
        
        
        
        self.container.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        

    def add_model_clicked(self):
        """Pop-Up penceresi açılır ve model eklenir."""
        dialog = QDialog(self)
        layout = QVBoxLayout(dialog)
        combo_layout = QHBoxLayout()
        text_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        
        combo_label = QLabel("Model Tipi:")
        combo_box = QComboBox()
        combo_box.addItems([f"{Drone.__name__}",
                            f"{Floor.__name__}"])
        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(combo_box)
        
        name_label = QLabel("Model Adı:")
        name_input = QLineEdit()
        
        orientation_label = QLabel("Model Oryantasyonu (x,y,z):")
        orientation_input = QLineEdit()
        orientation_input.setPlaceholderText("0,0,0")
        position_label = QLabel("Model Pozisyonu (x,y,z):")
        position_input = QLineEdit()
        position_input.setPlaceholderText("0,0,0")
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(name_input)
        text_layout.addWidget(orientation_label)
        text_layout.addWidget(orientation_input)
        text_layout.addWidget(position_label)
        text_layout.addWidget(position_input)
        
        
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(combo_layout)
        layout.addLayout(text_layout)
        layout.addLayout(button_layout)
        
        def on_ok_clicked():
            model_name = name_input.text().strip()
            model_orientation = orientation_input.text().strip()
            model_position = position_input.text().strip()
            #parse orientation and position
            if model_orientation:
                try:
                    orientation = tuple(map(float, model_orientation.split(',')))
                    if len(orientation) != 3:
                        raise ValueError("Orientation must be in the format x,y,z")
                    orientation = euler_to_quaternion(*orientation)
                except ValueError as e:
                    print(f"Invalid orientation format: {e}")
                    return
            if model_position:
                try:
                    position = tuple(map(float, model_position.split(',')))
                    if len(position) != 3:
                        raise ValueError("Position must be in the format x,y,z")
                except ValueError as e:
                    print(f"Invalid position format: {e}")
                    return
            
            if not model_name:
                return
            
            model_type = combo_box.currentText()
            if model_type == Drone.__name__:
                model = Drone(physics_client=self.sim_window.client)
            elif model_type == Floor.__name__:
                model = Floor(physics_client=self.sim_window.client)
            else:
                return
            
            self.add_model(model_name, model)
            dialog.accept()
        
        def on_cancel_clicked():
            dialog.reject()
        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(on_cancel_clicked)
        
        dialog.exec_()
        
            
            
            
    
    def add_model(self,model_name:str, model:Model,
                  position:tuple[float,float,float]=(0,0,0),
                  orientation:tuple[float,float,float,float]=(1,0,0,0)):
        """Modeli simülasyona ekler."""
        
        
        self.sim_window.add_model(model, position, orientation)
        self.models[model_name] = model
        
        
    def add_binding(self,key:Qt.Key, on_press=None, on_release=None, on_hold=None):
        """Klavye tuşu için olay bağlama."""
        self.sim_window.key_manager.register_callback(key, on_press=on_press, on_release=on_release, on_hold=on_hold)
        
    def start_sim(self):
        """Simülasyonu başlatır."""
        self.sim_window.start_sim()
        
        
class Simulator3DWindow(Qt3DWindow):
    def __init__(self,parent):
        super().__init__()
        self.setTitle("SCANE 3D Simulator")
        # 3D Entity
        self.rootEntity = QEntity()
        self.setRootEntity(self.rootEntity)
        cam = self.camera()
        cam.lens().setPerspectiveProjection(60.0, 16.0/9.0, 0.1, 100.0)
        cam.setPosition(QVector3D(0, 0, 10))
        cam.setViewCenter(QVector3D(0, 0, 0))
        self.key_manager = QKeyEventManager(parent)
        
        
        # Point light
        point_light = QPointLight(self.rootEntity)
        point_light.setColor(Qt.white)
        point_light.setIntensity(1.0)
        light_entity = QEntity(self.rootEntity)
        light_entity.addComponent(point_light)
        light_transform = QTransform()
        light_transform.setTranslation(QVector3D(10, 10, 20))
        light_entity.addComponent(light_transform)
        
    

        
        self.cam_ctrl =  QOrbitCameraController(self.rootEntity)
        self.cam_ctrl.setCamera(cam)    
        
        self.client = p.connect(p.DIRECT)
        self.keymgr = KeyEventManager()
        
        
        self.physics_simulation = PhysicsSimulation(
            physics_client=self.client,
            keymgr=self.keymgr,
            use_short_cuts=True,
            use_gui=False
        )
        
        
        self.entities:dict[str,tuple[Model,QTransform]] = {}
        
    
    
    def start_sim(self):
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(8)  # Yaklaşık 60 FPS
        
    
    def add_model(self,model:Model,
                  position:tuple[float,float,float]=(0,0,0),
                  orientation:tuple[float,float,float,float]=(1,0,0,0)):
            """Modeli simülasyona ekler ve 3D sahneye bağlar."""
            
            
            self.physics_simulation.add_model(model,position,orientation)
            
            mesh_file = model.get_mesh_file()
            if not os.path.exists(mesh_file):
                raise FileNotFoundError(f"Mesh dosyası bulunamadı: {mesh_file}")
            
                
                
            
            
            scale = model.get_scale()
            print(f"Model ölçeği: {scale}")
            entity = QEntity(self.rootEntity)
            mesh = QMesh(entity)
            mesh.setSource(QUrl.fromLocalFile(mesh_file))
            transform = QTransform(entity)
            transform.setScale3D(QVector3D(scale[0], scale[1], scale[2]))
            
            entity.addComponent(mesh)
            entity.addComponent(transform)
            
            texture_path = model.get_texture_path()
           
            if texture_path:
                texture = QTexture2D(self.rootEntity)
                texture.setGenerateMipMaps(True)
                
                tex_image = QTextureImage(texture)
                tex_image.setSource(QUrl.fromLocalFile(texture_path))
                texture.addTextureImage(tex_image)
            
                
                mat = QDiffuseMapMaterial(self.rootEntity)
                mat.setDiffuse(texture)
                entity.addComponent(mat)
            
            self.entities[model.model_id] = (model,transform)
            
            
            
            
    
    
    def update_scene(self):
        self.physics_simulation.step_simulation()
        self.keymgr.process_events()
        if self.entities is None:
            return
        for (model,transfrom)  in self.entities.values():
            pos= model.get_position()
            orientation = model.get_orientation()
            mat = QMatrix4x4()
            mat.translate(pos[0], pos[1], pos[2])
            q = QQuaternion(orientation[3], orientation[0], orientation[1], orientation[2]
                            )
            mat.rotate(q)
            mat.scale(*model.get_scale())
            transfrom.setMatrix(mat)
            
            
            
            

              

def main():
    app = QApplication(sys.argv)
    
    # Simülatör uygulamasını başlat
    simulator = Simulator3DWindow()
    drone = Drone(physics_client=simulator.client)
    simulator.key_manager.register_callback(
        Qt.Key.Key_Shift,
        on_hold=lambda x: drone.apply_force([0,100,0]),  # Yukarı doğru kuvvet uygula
    )
    simulator.key_manager.register_callback(
        Qt.Key.Key_Control,
        on_hold=lambda x: drone.apply_force([0, -100, 0]),  # Aşağı doğru kuvvet uygula
    )
    simulator.key_manager.register_callback(
        Qt.Key.Key_A,
        on_hold=lambda x: drone.apply_torque([0, 100, 0]),  # Sola doğru tork uygula
    )
    simulator.key_manager.register_callback(
        Qt.Key.Key_D,
        on_hold=lambda x: drone.apply_torque([0, -100, 0]),  # Sağa doğru tork uygula
    )
    
    simulator.add_model(
        Floor(physics_client=simulator.client),
        position=(0, 0, 0),
        orientation=(euler_to_quaternion(0,0,math.pi))  # Zemin düz bir yüzey olarak ayarlanır
    )
    simulator.add_model(
        drone,
        position=(0, 0, 10),  # Drone başlangıç pozisyonu
        orientation=(euler_to_quaternion(0,0,math.pi/2))  # Drone başlangıç oryantasyonu
    )
  
    simulator.start_sim()
    simulator.show()
    
    sys.exit(app.exec_()) 
    
    


if __name__ == "__main__":
    main()
