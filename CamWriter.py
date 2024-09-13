import cv2
import os 

class CameraWriter:
    
    def __init__(self,
                 video_path,
                 width,
                 height):
        
        self.video_path = video_path
        self.width = width
        self.height = height
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.fps = 30
        
        self.front_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,"FrontCam.mp4"),
                                                self.fourcc,
                                                self.fps,
                                                (self.width,self.height))
        self.right_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,"RightCam.mp4"),
                                                self.fourcc,
                                                self.fps,
                                                (self.width,self.height))
        self.left_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,"LeftCam.mp4"),
                                               self.fourcc,
                                               self.fps,
                                               (self.width,self.height))
        
        # dict to map camera while writing
        self.cam_writer = {
            "FrontCam" : self.front_cam_writer,
            "RightCam" : self.right_cam_writer,
            "LeftCam" : self.left_cam_writer
        }
        
        
    def write_image(self,cam_name,img):
        
        self.cam_writer[cam_name].write(img)
        
        
    def clear_writer(self):
        self.front_cam_writer.release()
        self.right_cam_writer.release()
        self.left_cam_writer.release()