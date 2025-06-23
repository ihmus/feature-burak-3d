from abc import ABC,abstractmethod

import pybullet as p
import numpy as np
import xml.etree.ElementTree as ET



class Model(ABC):
    """Model sınıfı, tüm modeller için temel bir soyut sınıftır."""
    
    def __init__(self, physics_client:int=0):
        self.physics_client = physics_client
        self.model_id = None  # Modelin pybullet ID'si
        self.model_path = None
        self.texture_id = None
        self.texture_path = None  # Modelin doku dosyasının yolu
    @abstractmethod
    def load(self, *args, **kwargs):
        """Modeli yükler. Her model için farklı implementasyon gerektirir."""
        pass

    @abstractmethod
    def apply_force(self, force: np.ndarray):
        """Model üzerine kuvvet uygular."""
        pass
    @abstractmethod
    def apply_torque(self, torque: np.ndarray):
        """Model üzerine tork uygular."""
        pass

    @abstractmethod
    def get_position(self) -> tuple:
        """Modelin pozisyonunu ve oryantasyonunu döndürür."""
        pass
    
    @abstractmethod 
    def get_scale(self) -> np.ndarray:
        """Modelin ölçeğini döndürür. Varsayılan olarak birim ölçek."""
        pass
    
    def get_mesh_file(self):
        """Drone'un mesh dosyasını döndürür."""
        mesh_file =  p.getVisualShapeData(self.model_id, physicsClientId=self.physics_client)[0][4].decode('utf-8')
        
        return mesh_file
    
    def get_urdf_file(self) -> str:
        """Modelin URDF dosyasını döndürür."""
        return self.model_path
        
    def get_position(self) -> tuple:
        """Modelin pozisyonunu döndürür."""
        return p.getBasePositionAndOrientation(self.model_id, physicsClientId=self.physics_client)[0]
    
    def get_orientation(self) -> tuple:
        """Modelin oryantasyonunu döndürür."""
        return p.getBasePositionAndOrientation(self.model_id, physicsClientId=self.physics_client)[1]
    def get_texture_path(self)-> str:
        """Modelin doku dosyasının yolunu döndürür."""
        urdf = self.get_urdf_file()
        print(f"URDF file: {urdf}")
        if not urdf:
            return []
        tree = ET.parse(urdf)
        root = tree.getroot()
        tex_file = root.find('.//texture').get('filename').split(':')[-1]  # 'file://' ile başlayan yolu ayır ve son kısmı al
        tex_file = tex_file if tex_file.startswith('/') else f"{urdf.rsplit('/', 1)[0]}/{tex_file}"  # Eğer tam yol değilse, modelin bulunduğu dizine göre tam yol oluştur
        if not tex_file:
            print("URDF dosyasında texture bulunamadı.")
            raise ValueError("URDF dosyasında texture bulunamadı.")
        
        
        return tex_file


