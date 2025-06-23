from cgitb import text
import os
import sys
import pybullet as p
import pybullet_data

from physics import Floor, Model, PhysicsSimulation, Drone 

from key_event_manager import KeyEventManager
from objects.Camera import Camera

from PyQt5.QtWidgets       import QApplication
from PyQt5.QtCore          import QTimer, QUrl, Qt
from PyQt5.Qt3DCore        import QEntity, QTransform
from PyQt5.Qt3DExtras      import Qt3DWindow, QOrbitCameraController
from PyQt5.Qt3DExtras      import QDiffuseMapMaterial
from PyQt5.Qt3DRender      import QMesh,QTexture2D, QTextureImage
from PyQt5.QtGui           import QVector3D, QQuaternion, QMatrix4x4
from PyQt5.Qt3DRender import QPointLight
class Simulator3DApplication(Qt3DWindow):
    def __init__(self):
        super().__init__()
        self.setTitle("SCANE 3D Simulator")
        
        # 3D Entity
        self.rootEntity = QEntity()
        self.setRootEntity(self.rootEntity)
        cam = self.camera()
        cam.lens().setPerspectiveProjection(60.0, 16.0/9.0, 0.1, 100.0)
        cam.setPosition(QVector3D(0, 0, 10))
        cam.setViewCenter(QVector3D(0, 0, 0))
        
        # Ambient Light

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
        
        self.client = p.connect(p.GUI)

        self.physics_simulation = PhysicsSimulation(
            physics_client=self.client,
            keymgr=KeyEventManager(),
            use_short_cuts=True,
            use_gui=False
        )
        
        
        self.entities:dict[str,tuple[Model,QTransform]] = {}
    
    def start_sim(self):
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # Yaklaşık 60 FPS
    
    def add_model(self,model:Model,
                  position:tuple[float,float,float]=(0,0,0),
                  orientation:tuple[float,float,float,float]=(1,0,0,0)):
            """Modeli simülasyona ekler ve 3D sahneye bağlar."""
            
            
            self.physics_simulation.add_model(model,position,orientation)
            
            mesh_file = model.get_mesh_file()
            if not os.path.exists(mesh_file):
                raise FileNotFoundError(f"Mesh dosyası bulunamadı: {mesh_file}")
            
                
                
            
            
            scale = model.get_scale()
            
            
            entity = QEntity(self.rootEntity)
            mesh = QMesh(entity)
            mesh.setSource(QUrl.fromLocalFile(mesh_file))
            transform = QTransform(entity)
            transform.setScale3D(QVector3D(*scale))
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
            transfrom.setMatrix(mat)
            
            
            
            
            
            
              

def main():
    app = QApplication(sys.argv)
    
    # Simülatör uygulamasını başlat
    simulator = Simulator3DApplication()
    simulator.add_model(
        Floor(physics_client=simulator.client),
        position=(0, 0, 0),
        orientation=(1, 0, 0, 0)  # Zemin düz bir yüzey olarak ayarlanır
    )
  
    simulator.start_sim()
    simulator.show()
    
    sys.exit(app.exec_()) 
    
    

    
if __name__ == "__main__":
    main()
    