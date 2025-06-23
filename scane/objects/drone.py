import pybullet as p
import os
from objects.Model import Model
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Drone(Model):
    """Drone modelini temsil eden sınıf."""
    
    def __init__(self, physics_client:int=0, 
                 model_path:str=None,
                 ):
        super().__init__(physics_client)
        logging.info("Drone modelini başlatılıyor...")
        
        self.model_path = model_path if model_path else os.path.join(os.path.abspath(os.path.curdir), 'scane/models', 'drone.urdf')
        self.model_id = None  # Drone'un pybullet ID'si
        self.texture_path = self.get_texture_path()
        self.texture_id = None
        

    def load(self):
        """Drone modelini yükler."""
        logging.info(f"Drone modeli yükleniyor: {self.model_path}")
        self.model_id = p.loadURDF(self.model_path, physicsClientId=self.physics_client)
        print(f"Drone modeline doku ekleniyor: {self.texture_path}")
        self.texture_id = p.loadTexture(self.texture_path, physicsClientId=self.physics_client)
        print(f"Drone modeline doku ekleniyor: {self.texture_id}")
        if self.texture_id!=-1:
            p.changeVisualShape(self.model_id, -1, textureUniqueId=self.texture_id, physicsClientId=self.physics_client)
            logging.info(f"Drone modeline doku eklendi: {self.texture_path}")
        else:
            logging.warning("Drone modeline doku eklenemedi, doku yolu bulunamadı.")
        
        
        return self.model_id
    
    def apply_force(self, force: list):
        """Drone üzerine kuvvet uygular."""
        p.applyExternalForce(self.model_id, -1, force, [0, 0, 0], p.LINK_FRAME, physicsClientId=self.physics_client)
    
    def apply_torque(self, torque: list):
        """Drone üzerine tork uygular."""
        p.applyExternalTorque(self.model_id, -1, torque, p.LINK_FRAME, physicsClientId=self.physics_client)
    
    def get_scale(self) -> list:
        """Drone'un ölçeğini döndürür. Varsayılan olarak birim ölçek."""
        return p.getVisualShapeData(self.model_id, physicsClientId=self.physics_client)[0][3]