import pybullet as p
import pybullet_data
import time,os
# pybulletin sadece fizik küytüphaneleri / tasarım için opengl veyahutta diğer basit tasarım 

class PhysicsSimulation:
    def __init__(self):
        self.physicsClient = p.connect(p.GUI)  # PyBullet başlat (grafiksiz mod)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

        # Zemin ekle
        self.planeId = p.loadURDF(f"{os.getcwd()}\scane\models\ground.urdf")

        # Küp (Drone) oluştur
        self.droneId = p.loadURDF("cube_small.urdf", basePosition=[0, 0, 2])

        # Yerçekimi ayarla
        p.setGravity(0, 0, 0)

    def step_simulation(self):
        """Simülasyonu bir adım ilerletir ve drone’un pozisyonunu döndürür."""
        p.stepSimulation()
        pos, orn = p.getBasePositionAndOrientation(self.droneId)
        return pos, orn
    
if __name__ == "__main__":
    sim = PhysicsSimulation()
    while True:
        pos, orn = sim.step_simulation()
        print(f"Drone pozisyonu: {pos}")
        time.sleep(1. / 240.)  # Simülasyon zamanlamasına uygun bekleme
#deneme içib betül