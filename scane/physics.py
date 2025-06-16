import pybullet as p
import pybullet_data
import time,os
from key_event_manager import KeyEventManager 
# pybulletin sadece fizik küytüphaneleri / tasarım için opengl veyahutta diğer basit tasarım 
class PhysicsSimulation:
    def __init__(self):
        self.physicsClient = p.connect(p.GUI)  # PyBullet başlat (grafiksiz mod)
        self.keymanager = KeyEventManager()
        self.keymanager.register_callback(
            key='w', 
            on_hold=lambda :self.apply_force_up(40)
        )
        self.keymanager.register_callback(
            key='s', 
            on_hold=lambda :self.apply_force_down(40)
        )
        self.keymanager.register_callback(
            key='a', 
            on_hold=lambda :self.apply_force_left(40)
        )
        self.keymanager.register_callback(
            key='d', 
            on_hold=lambda :self.apply_force_right(40)
        )
        
        
        
        
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.configureDebugVisualizer(p.COV_ENABLE_KEYBOARD_SHORTCUTS, 0)  # GUI'yi devre dışı bırak
        
        # Zemin ekle
        
        self.droneId = p.loadURDF(f"{os.getcwd()}/scane/models/drone.urdf",basePosition=[0,0,100.23])

        self.planeId = p.loadURDF(f"{os.getcwd()}/scane/models/real_map.urdf",basePosition=[0,0,0])
        # Yerçekimi ayarla
        p.setGravity(0, 0, -9.1)
        p.changeDynamics(
            self.planeId,-1,mass=0.001
        )
        
        

    
    
    def step_simulation(self):
        """Simülasyonu bir adım ilerletir ve drone’un pozisyonunu döndürür."""
        p.stepSimulation()
        pos, orn = p.getBasePositionAndOrientation(self.droneId)
        return pos, orn
    
    
    
    
    
    def apply_force_up(self,force=0.2):
        
        """Drone'a yukarı doğru kuvvet uygular."""
        
        p.applyExternalForce(
            self.droneId, 
            linkIndex=-1, 
            forceObj=[0, 0, force], 
            posObj=[0, 0, 0], 
            flags=p.WORLD_FRAME
        )
    def apply_force_down(self,force=0.2):
        
        """Drone'a aşağı doğru kuvvet uygular."""
        p.applyExternalForce(
            self.droneId, 
            linkIndex=-1, 
            forceObj=[0, 0, -force], 
            posObj=[0, 0, 0], 
            flags=p.WORLD_FRAME
        )
    def apply_force_left(self,force=0.20):
        """Drone'a sola doğru kuvvet uygular."""
        p.applyExternalForce(
            self.droneId, 
            linkIndex=-1, 
            forceObj=[-force, 0, 0], 
            posObj=[0, 0, 0], 
            flags=p.WORLD_FRAME
        )
    def apply_force_right(self,force=0.2):
        
        """Drone'a sağa doğru kuvvet uygular."""
        p.applyExternalForce(
            self.droneId, 
            linkIndex=-1, 
            forceObj=[force, 0, 0], 
            posObj=[0, 0, 0], 
            flags=p.WORLD_FRAME
        )

    
if __name__ == "__main__":
    sim = PhysicsSimulation()
    while True:
        pos, orn = sim.step_simulation()
        sim.keymanager.process_events()
        time.sleep(1. / 240.) 
        