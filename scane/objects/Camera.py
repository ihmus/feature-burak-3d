from re import X
import pybullet as p
import numpy as np

class Camera:
    def __init__(self,client_id:int=0,
                 camera_id:str="camera",
                 fov:float=60.0,
                 aspect_ratio:float=640/480,
                 near_val:float=0.1,
                 far_val:float=100.0)-> None:
        """Kamera nesnesi oluşturur."""
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_val = near_val
        self.far_val = far_val
        
        
        self.camera_id = camera_id
        
        self.camera_position = [0, 0, 0]  
        self.camera_target = [0, 0, 1]
        self.camera_up =  [0,0,1]
    
    def  _compute_matrices(self):
        view_matrix = p.computeViewMatrix(
            cameraEyePosition=self.camera_position,
            cameraTargetPosition=self.camera_target,
            cameraUpVector=self.camera_up,
            physicsClientId=self.client_id
        )
        projection_matrix = p.computeProjectionMatrixFOV(
            fov=self.fov,
            aspect=self.aspect_ratio,
            nearVal=self.near_val,
            farVal=self.far_val,
            physicsClientId=self.client_id
        )
        return view_matrix, projection_matrix
    
    def capture_image(self,width:int=640, height:int=480,renderer_mode:int=p.ER_BULLET_HARDWARE_OPENGL):
        """Kameradan görüntü yakalar."""
        view_matrix, projection_matrix = self._compute_matrices()
        
        w, h, rgb_img, depth_img, seg_img = p.getCameraImage(
            width=640,
            height=480,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix,
            physicsClientId=self.client_id,
            Xrenderer=renderer_mode
        )
        
        return {
            "rgb": np.array(rgb_img),
            "depth": np.array(depth_img),
            "segmentation": np.array(seg_img)
        }
        