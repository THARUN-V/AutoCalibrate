import cv2
import os 
from ParseParams import *

class CameraWriter(ParseParams):
    
    def __init__(self,
                 video_path,
                 width,
                 height,
                 connected_cams):
        
        ParseParams.__init__(self)
        
        self.video_path = video_path
        self.width = width
        self.height = height
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.fps = 10
        
        # variable to keep track of number of cameras connected
        self.connected_cams = connected_cams
        
        self.cam_writer = dict()
        
        if "FrontCam" in self.connected_cams.keys():
            self.front_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.front_cam_video_name),
                                                    self.fourcc,
                                                    self.fps,
                                                    (self.width,self.height))
            self.cam_writer.update({"FrontCam":self.front_cam_writer})
        if "RightCam" in self.connected_cams.keys():
            self.right_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.right_cam_video_name),
                                                    self.fourcc,
                                                    self.fps,
                                                    (self.width,self.height))
            self.cam_writer.update({"RightCam":self.right_cam_writer})
        if "LeftCam" in self.connected_cams.keys():
            self.left_cam_writer = cv2.VideoWriter(os.path.join(self.video_path,self.args.left_cam_video_name),
                                                self.fourcc,
                                                self.fps,
                                                (self.width,self.height))
            self.cam_writer.update({"LeftCam":self.left_cam_writer})
        
        # dict to map camera while writing
        # self.cam_writer = {
        #     "FrontCam" : self.front_cam_writer,
        #     "RightCam" : self.right_cam_writer,
        #     "LeftCam" : self.left_cam_writer
        # }
        
        
    def write_image(self,cam_name,img):
        
        self.cam_writer[cam_name].write(img)
        
        
    def clear_writer(self):
        # self.front_cam_writer.release()
        # self.right_cam_writer.release()
        # self.left_cam_writer.release()
        
        for writer in self.cam_writer.values():
            writer.release()