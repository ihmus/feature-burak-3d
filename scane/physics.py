from ast import Mod
from cgitb import text
from logging.config import listen
import math
import pybullet as p
import pybullet_data
import time,os
from key_event_manager import KeyEventManager

from objects.drone import Drone
from objects.Floor import Floor
from objects.Model import Model
# pybulletin sadece fizik küytüphaneleri / tasarım için opengl veyahutta diğer basit tasarım 



class PhysicsSimulation:
    
    def __init__(self,keymgr:KeyEventManager=None,
                 physics_client:int=0,
                 use_short_cuts:bool=True,
                 use_gui:bool=False):
        
            
        self.physicsClient = physics_client
        self.models:dict[str,Model] = {}
        self.keymanager = keymgr if keymgr else KeyEventManager()
        
        
        
        p.configureDebugVisualizer(p.COV_ENABLE_KEYBOARD_SHORTCUTS, 1 if use_short_cuts else 0)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.88, physicsClientId=self.physicsClient)
    
    
    
    def add_model(self,model:Model,position:list[float]=[0,0,0],orientation:list[float]=[0,0,0,1]):
        """Modeli simülasyona ekler."""
        if not isinstance(model,Model):
            raise TypeError(f"Model tipi Model olmalı, verildi: {type(model)}")
        model_id = model.load()
        self.models[model_id] = model
        p.resetBasePositionAndOrientation(model_id, position, orientation, physicsClientId=self.physicsClient)
        return model_id
        
    def get_entities(self):
        """Simülasyondaki tüm modelleri döndürür."""
        return self.models.keys() ,self.models.values()

    def add_binding(self,
                    key:str|int,
                    on_press:callable=None,
                    on_release:callable=None,
                    on_hold:callable=None):
        """Anahtar olaylarını işlemek için bir bağlayıcı ekler."""
        self.keymanager.register_callback(key, on_press, on_release, on_hold)
        
        
                

    def step_simulation(self):
        """Simülasyonu bir adım ilerletir ve drone’un pozisyonunu döndürür."""
        p.stepSimulation()
        
        
        


def euler_to_quaternion(x:float,y:float,z:float):
    """Eğik açılarından quaternion'a dönüşüm."""
    cy = math.cos(z * 0.5)
    sy = math.sin(z * 0.5)
    cp = math.cos(y * 0.5)
    sp = math.sin(y * 0.5)
    cr = math.cos(x * 0.5)
    sr = math.sin(x * 0.5)

    return [
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy
    ]

def main():
    client = p.connect(p.GUI)
    sim = PhysicsSimulation(physics_client=client,use_gui=True,use_short_cuts=False)
    drone = Drone(physics_client=client)
    floor = Floor(physics_client=client)
    sim.add_model(drone,position=[0, 0, 5], orientation=euler_to_quaternion(0, 0, math.pi/2))
    sim.add_model(floor,position=[0, 0, 0], orientation=[0, 0, 0, 1])
    def apply_forward_force():
        """Drone'a ileri yönde kuvvet uygular."""
        force = [-10, 0, 0]
        drone.apply_force(force)
    def apply_backward_force():
        """Drone'a geri yönde kuvvet uygular."""
        force = [10, 0, 0]
        drone.apply_force(force)
    def apply_left_force():
        """Drone'a sola doğru kuvvet uygular."""
        force = [0, 0, 10]
        drone.apply_force(force)
    def apply_right_force():
        """Drone'a sağa doğru kuvvet uygular."""
        force = [0, 0, -10]
        drone.apply_force(force)
    def apply_upward_force():
        """Drone'a yukarı doğru kuvvet uygular."""
        force = [0, 10,0]
        drone.apply_force(force)
    def apply_downward_force():
        """Drone'a aşağı doğru kuvvet uygular."""
        force = [0, -10,0]
        drone.apply_force(force)
        
    def apply_pitch():
        """Drone'a pitch uygular."""
        torque = [0, 0, -10]
        drone.apply_torque(torque)
    def apply_roll():
        """Drone'a roll uygular."""
        torque = [10, 0, 0]
        drone.apply_torque(torque)
    def apply_yaw():
        """Drone'a yaw uygular."""
        torque = [0, 10, 0]
        drone.apply_torque(torque)
        
    sim.add_binding('w', on_hold=apply_forward_force)
    sim.add_binding('s', on_hold=apply_backward_force)
    sim.add_binding('a', on_hold=apply_left_force)
    sim.add_binding('d', on_hold=apply_right_force)
    sim.add_binding('q', on_hold=apply_pitch)
    sim.add_binding('e', on_hold=apply_roll)
    sim.add_binding('r', on_hold=apply_yaw)
    
    sim.add_binding('shift', on_hold=apply_upward_force)
    sim.add_binding('ctrl', on_hold=apply_downward_force)
    
    
    
    
    
    while True:
        sim.step_simulation()
        sim.keymanager.process_events()
        time.sleep(1. / 240.) 

    
if __name__ == "__main__":
    main()