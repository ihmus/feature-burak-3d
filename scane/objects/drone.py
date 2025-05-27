import pybullet as p
import os

class Drone:
    def __init__(self, physics_client):
        self.physics_client = physics_client
        drone_path =  os.path.join(os.getcwd(), "scane\\models", "drone.urdf")
        print(drone_path)
        self.drone = p.loadURDF(drone_path, basePosition=[0, 0, 1], physicsClientId=self.physics_client)

    def apply_force(self, force):
        
        p.applyExternalForce(
            self.drone, 
            linkIndex=-1, 
            forceObj=[force, 0, 0], 
            posObj=[0, 0, 0], 
            flags=p.WORLD_FRAME, 
            physicsClientId=self.physics_client
        )

    def update_position(self):
        """Drone'un güncel pozisyonunu ve oryantasyonunu döndür"""
        pos, orn = p.getBasePositionAndOrientation(self.drone, physicsClientId=self.physics_client)
        return pos, orn