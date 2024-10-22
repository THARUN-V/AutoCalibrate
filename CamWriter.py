import cv2
import os 
from ParseParams import *

class CameraWriter(ParseParams):
    
    def __init__(self,
                 video_path,
                 width,
                 height):
        
        ParseParams.__init__(self)
        
        self.video_path = video_path
        self.width = width
        self.height = height
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.fps = 10
        
        self.front_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.front_cam_video_name),
                                                self.fourcc,
                                                self.fps,
                                                (self.width,self.height))
        self.right_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.right_cam_video_name),
                                                self.fourcc,
                                                self.fps,
                                                (self.width,self.height))
        self.left_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.left_cam_video_name),
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