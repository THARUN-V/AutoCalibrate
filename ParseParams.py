import argparse
import logging
import os
import json

from CameraStartUpJsonTemplate import *

class ParseParams:
    
    def __init__(self):
                
        logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s", level=logging.INFO, datefmt="%d/%m/%y %H:%M:%S")
        self.logger = logging.getLogger()
        
        parser = argparse.ArgumentParser(description = "Script to automate the calibration. \n ./AutoCalibrate --videoplayback_build ./VideoPlayback_ECON_vx.y.z",formatter_class=argparse.RawTextHelpFormatter)
        
        parser.add_argument("--json_path",default = "/home/pi/CameraStartUpJson.json",help = "path to json file for read,modify and updating the params. (default : /home/pi/CameraStartUpJson.json)")
        parser.add_argument("--n_cam",type = int ,default = 3,help = "number of cameras connected to bot (default : 3)")
        parser.add_argument("--resolution",type = int, default = 1 , help = "resoultion of image to get from camera. (default : 1) \n supported resolution \n 0 : (640,480) \n 1 : (960,540) \n 2 : (1280,720) \n 3 : (1280,960) \n 4 : (1920,1080)")
        
        #### params related to marker detection #####
        parser.add_argument("--aruco_dict",type = str , default = "DICT_4X4_50",help = "Aruco Dictionary family used for detection. (default : DICT_4X4_50)")
        parser.add_argument("--front_cam_marker_id",type = int , default = 0 , help = "marker id for front camera. (default : 0)")
        parser.add_argument("--right_cam_marker_id",type = int , default = 1 , help = "marker id for right camra. (default : 1)")
        parser.add_argument("--left_cam_marker_id",type = int , default = 2, help = "marker id for left camera. (default : 2)")
        parser.add_argument("--record_frame_count",type = int,default = 100,help = "number of frames to record as video. (default : 100)")
        parser.add_argument("--videoplayback_build",type=str,default = None,help = "path to VideoPlayback build. (default : None)")
        
        #### threshold params for ratio and csa ####
        parser.add_argument("--ratio_without_side_cam_offset_min",type = float,default = 0.4,help = "min ratio to accept without side camera offset. (default : 0.47)")
        parser.add_argument("--ratio_without_side_cam_offset_max",type = float,default = 0.6,help = "max ratio to accept without side camera offset. (default : 0.53)")
        parser.add_argument("--csa_without_offset_min",type = float,default = 87,help = "min current steering angle to accept without sterring angle offset. (default : 87)")
        parser.add_argument("--csa_without_offset_max",type = float,default = 93,help = "max current steering angle to accept without sterring angle offset. (default : 93)")
        
        parser.add_argument("--ratio_with_side_cam_offset_min",type = float,default = 0.495,help = "min ratio to accept with side camera offset. (default : 0.495)")
        parser.add_argument("--ratio_with_side_cam_offset_max",type = float,default = 0.505,help = "max ratio to accept with side camera offset. (default : 0.505)")
        parser.add_argument("--csa_with_offset_min",type = float,default = 89.5,help = "min current steering angle to accept with sterring angle offset. (default : 89.5)")
        parser.add_argument("--csa_with_offset_max",type = float,default = 90.5,help = "max current steering angle to accept with sterring angle offset. (default : 90.5)")
        
        parser.add_argument("--target_ratio",type = float,default = 0.50,help = "target ratio to substiute in equation of side camera offsets. (default : 0.50)")
        parser.add_argument("--target_steering_angle",type = float,default=90.0,help = "targe steering angle. (default : 90.0)")
        
        ### params for running the script in debug mode with the provided video file ###
        parser.add_argument("--debug",action = "store_true",help = "param to run script in debug mode with provided video file")
        parser.add_argument("--video_path",type = str , default = None,help = "path to video file for debug mode")
        
        ### param to skip camera device id mapping and perform only ratio estimation ###
        parser.add_argument("--skip_camera_id_mapping",action="store_true",help = "Param to skip camera device id mapping and estimate only offsets")
        
        #### video file names ####
        parser.add_argument("--right_cam_video_name",type=str,default="RightCam.mp4",help = "Video file name for right cam")
        parser.add_argument("--left_cam_video_name",type=str,default="LeftCam.mp4",help = "Video file name for left cam")
        parser.add_argument("--front_cam_video_name",type=str,default="FrontCam.mp4",help= "Video file name for front cam")
        ##########################
        
        ## param to print offsets in all three stages
        parser.add_argument("--debug_print",action="store_true",help="param to print offsets in all three stages")
        
        self.args = parser.parse_args()
        
        # resolution of camera #
        self.cam_res_dict = {
            0 : (640,480),
            1 : (960,540),
            2 : (1280,720),
            3 : (1280,960),
            4 : (1920,1080)
        }
        self.w , self.h = self.cam_res_dict[self.args.resolution]
        
        
    def check_params(self):
        """
        function to check if all the required params are provided.
        """
            
        if self.args.videoplayback_build == None:
            self.logger.error("path to VideoPlayback build is not provided")
            return False
        
        # if self.args.debug:
        #     return True
        
        return True