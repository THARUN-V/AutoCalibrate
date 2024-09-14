from ParseParams import *
from CamContext import CamContext
from CamCapture import CameraCapture
from MarkerDetector import ArucoMarkerDetector
from CamWriter import CameraWriter
import json
import logging
import cv2
from datetime import datetime
import os
import numpy

class AutoCalibrate(ParseParams,CamContext,ArucoMarkerDetector):
    
    def __init__(self):
        
        ParseParams.__init__(self)
        CamContext.__init__(self)
        ArucoMarkerDetector.__init__(self,self.args.aruco_dict)
        
        
        # check if all the required params are provided from cli
        # else print the appropriate log and exit.
        if not self.check_params():
            exit()    
            
        # load the current json file
        with open(self.args.json_path,"r") as f:
            self.current_json = json.load(f) 
            
        # scan the camera and get camera serial numbers
        self.see_cams = self.get_seecam()
        
        # if no cameras found exit with error message
        if self.see_cams == None:
            self.logger.error("!!! No Cameras Found !!!")
            exit()
        
        # check if the scanned and provided number of cameras match
        if len(self.see_cams) != self.args.n_cam:
            self.logger.error(f"Found {len(self.see_cams)} cameras out of {self.args.n_cam}")
            exit()
            
        self.cam_name_and_index = {
            "FrontCam":None,
            "RightCam":None,
            "LeftCam":None
        }
        
        # path for video file to store
        
        # count to skip frames that is of green color
        self.skip_frame_count = 3
        # count to keep track of frames being written
        self.current_frame_count = 0
        # directory to store video and log files
        self.data_dir = os.path.join(os.getcwd(),datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        # create directory to writer log and video 
        os.mkdir(self.data_dir)
            
    def detect_and_map_cam_ids(self):
        """
        Function to detect markers in image and map the camera ids.
        """
        # mainatin predefined markers to avoid false detection
        predefined_marker_ids = [self.args.front_cam_marker_id,self.args.right_cam_marker_id,self.args.left_cam_marker_id]
        
        # utility function to conver list of list of ids to list of id
        def get_id_from_ids(ids):
            id = ids[0]
            
            if len(id) > 1:
                self.logger.error(f"more than 1 marker detected")
                exit()
            else:
                return id[0]
        
        # iterate over seecam object and detect markers
        for cam in self.see_cams:
            # get the current cam index , fetch frame and detect marker
            cap = cv2.VideoCapture(cam.camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.h)
            
            # flag to check if id is detected for current cam
            id_detected = False
            
            while not id_detected:
                
                ret , frame = cap.read()
                
                if ret:
                    # detect the marker in current camera
                    _ , ids , _ , _ = self.get_marker_id(frame)
                    if ids != None:
                        # since the ids returned is list of list of ids
                        # convert this into single list of one id
                        current_marker_id = get_id_from_ids(ids)
                        # check the id and assign the camera index to corresponding camere name
                        # and update id in json file
                        if current_marker_id in predefined_marker_ids:
                            if current_marker_id == self.args.front_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.current_json["CamParams"][0]["frontCameraId"] = cam.serial_number
                                self.cam_name_and_index["FrontCam"] = cam.camera_index
                                id_detected = True
                            if current_marker_id == self.args.right_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.current_json["CamParams"][0]["rightCameraId"] = cam.serial_number
                                self.cam_name_and_index["RightCam"] = cam.camera_index
                                id_detected = True
                            if current_marker_id == self.args.left_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.current_json["CamParams"][0]["leftCameraId"] = cam.serial_number
                                self.cam_name_and_index["LeftCam"] = cam.camera_index
                                id_detected = True
                            
            if id_detected:
                cap.release()
    
    def get_ratio_csa_from_log_file(self,log_file_path):
        """
        utility function to get ratio and current steering angle from log file provided as a single value
        """
        
        # iterate over log file get the mean ratio from string 
        ratio = [[float(string.split("=")[1]) for string in line.split(";") if "ratio" in string][0]
                 for line in open(log_file_path,"r").readlines() 
                 if ";" in line and "ratio" in line]
        
        ratio_mean = numpy.mean(numpy.array(ratio))
        
        # iterate over log file get the mean current steering angle from string
        csa = [[float(string.split("=")[1]) for string in line.split(";") if "CSA" in string][0]
                 for line in open(log_file_path,"r").readlines() 
                 if ";" in line and "CSA" in line]
        
        csa_mean = numpy.mean(numpy.array(csa))
        
        # print(f"ratio_mean : {ratio_mean}")
        # print(f"csa_mean : {csa_mean}")
        
        return ratio_mean , csa_mean
    
    def estimate_offset(self,measured_ratio,cam_name = None):
        """
        Function to estimate side camera offset using equation.
        """
        
        if cam_name == None:
            self.logger.error(f"!!!!! No came name provided for estimate offset method !!!!!!")
            exit()
        
        if cam_name == "right":
            return int(self.args.lane_width * (self.args.target_ratio - measured_ratio))
        
        if cam_name == "left":
            return int(self.args.lane_width * (1 - measured_ratio - self.args.target_ratio))
        
    def check_and_update_estimated_offset(self,estimated_ratio,cam_name = None):
        """
        utility function to check whether the current estimated ratio without side cam offset lies in acceptable range
        and update the same in json file.
        """
        # check if the estimated ratio is between acceptable ratio that is calculated without applying offset
        if estimated_ratio >= self.args.ratio_without_side_cam_offset_min and estimated_ratio <= self.args.ratio_without_side_cam_offset_max:
            self.logger.info(f"Current {cam_name}_ratio is in acceptable range")
            # if the current measured ratio is in acceptable range, estimate the side camera offset using the equation by setting target ratio to 0.5
            self.logger.info(f"Estimating {cam_name}SideCameraOffset with measured_ratio : {estimated_ratio}")
            Estimated_SideCameraOffset = self.estimate_offset(cam_name = cam_name,measured_ratio = estimated_ratio)
            self.logger.info(f"Estimated {cam_name}SideCameraOffset : {Estimated_SideCameraOffset}")
            # Overwrite right camera offset in json file
            self.logger.info(f"Overwriting {cam_name}SideCameraOffset in Json file")
            with open(self.args.json_path,"w") as updated_json:
                self.current_json["CamParams"][0][f"{cam_name}SideCameraOffset"] = Estimated_SideCameraOffset
                json.dump(self.current_json,updated_json,indent = 4)
            self.logger.info(f"Done , Overwriting of {cam_name}SideCameraOffset in Json file")
        else:
            self.logger.error(f"Current {cam_name} Ratio : {estimated_ratio} does not lie in acceptable range.")
            self.logger.error(f"current position of BOT or CAMERA is not accepted")
            exit()
        
    
        
    def run_calibration(self):
        
        ############################### Camera Id Mapping ####################################################
        self.logger.info("========= Performing Camera Id Mapping =========")
        self.detect_and_map_cam_ids()
        self.logger.info("=========    Done Camera Id Mapping    =========")
        
        self.logger.info(f"Mapped Camera Id's FrontCameraId : {self.current_json['CamParams'][0]['frontCameraId']} | RightCameraId : {self.current_json['CamParams'][0]['rightCameraId']} | LeftCameraId : {self.current_json['CamParams'][0]['leftCameraId']}")
        self.logger.info(f"Mapped Camera Idx FrontCameraIdx : {self.cam_name_and_index['FrontCam']} | RightCameraIdx : {self.cam_name_and_index['RightCam']} | LeftCameraIdx : {self.cam_name_and_index['LeftCam']}")
        # after detecting camera id, update it in json
        with open(self.args.json_path,"w") as updated_json:
            json.dump(self.current_json,updated_json,indent = 4)
        self.logger.info("Updated mapped Camera Id's in Json")
        ############################### End of Camera Id Mapping ##############################################
        
        ############################## Record video of Front,Left and Right for debug and estimating offsets ###################
        # initialize cam writer object
        out = CameraWriter(self.data_dir,self.w,self.h)
        for cam_name , cam_index in self.cam_name_and_index.items():
            cap = cv2.VideoCapture(cam_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.h)
            self.logger.info(f"Recording Video of {cam_name}")
            while self.current_frame_count <= self.args.record_frame_count:
                ret , frame = cap.read()
                if ret:
                    if self.current_frame_count > self.skip_frame_count:
                        out.write_image(cam_name,frame)
                    self.current_frame_count += 1
            self.current_frame_count = 0
                    
        # release the video writer objects
        out.clear_writer()
        ###########################  End Record video of Front,Left and Right for debug and estimating offsets ###################
        
        ########################### side camera offset estimation ######################################################
        
        ### for side camera estimation set the current side camera offsets to zero in current json file ###
        self.logger.info(f"Setting leftSideCameraOffset and rightSideCameraOffset to 0")
        self.current_json["CamParams"][0]["leftSideCameraOffset"] = 0
        self.current_json["CamParams"][0]["rightSideCameraOffset"] = 0
        with open(self.args.json_path,"w") as updated_json:
            json.dump(self.current_json,updated_json,indent = 4)
        self.logger.info(f"Overwritten leftSideCameraOffset : 0 and rightSideCameraOffset : 0")
        ### end of setting side camera offsets to zero in current json file ###
        
        ### run the existing videoplayback build with video/picture mode to estimate ratio with sidecamera offsets set to zroe ###
        # check if the video file exists #
        if len(os.listdir(self.data_dir)) < self.args.n_cam:
            self.logger.error(f"Only {len(os.listdir(self.data_dir))} exists out of {self.args.n_cam}")
        
        self.logger.info(f"Executing VideoPlayback build with lefSideCameraOffset : {self.current_json['CamParams'][0]['leftSideCameraOffset']} , rightCameraOffset : {self.current_json['CamParams'][0]['rightSideCameraOffset']}")
        
        # iterater over the video file generate log 
        for video_file in os.listdir(self.data_dir):
            if ".mp4" in video_file:
                if "Right" in video_file or "Left" in video_file:
                    # print(os.path.join(self.data_dir,video_file))
                    # command to run videoplayback build
                    log_file = os.path.join(self.data_dir,video_file.split(".mp4")[0]+"Log.txt")
                    cmd = f"{self.args.videoplayback_build} -i /home/tharun/THARUN/Data/TestVideos/TKAP_ORANGE_LANES/Left_Camera_Orange_Video_8_161223.mp4 -v > {log_file} 2>&1"
                    
                    # run the command
                    process = os.system(cmd)
                    
                    # check if the process has executed and terminated successfully
                    if process == 0:
                        self.logger.info(f"Done with {os.path.join(self.data_dir,video_file)}")
        
        # get the log file for right cam and left cam
        for log_file in os.listdir(self.data_dir):
            log_file = os.path.join(self.data_dir,log_file)
            if ".txt" in log_file:
                # get the right cam log file
                if "Right" in log_file:
                    # get the ratio and csa using log file

                    right_estimated_ratio_mean , right_csa_mean = self.get_ratio_csa_from_log_file(log_file)
                    
                    self.logger.info(f"right_ratio_mean : {right_estimated_ratio_mean} | right_csa_mean : {right_csa_mean}")
                
                    self.check_and_update_estimated_offset(cam_name = "right", estimated_ratio = right_estimated_ratio_mean)
                        
                # get the left cam log file
                if "Left" in log_file:
                    
                    # get the ratio and csa using the log file
                    
                    left_estimated_ratio_mean , left_csa_mean = self.get_ratio_csa_from_log_file(log_file)
                    
                    self.logger.info(f"left_ratio_mean : {left_estimated_ratio_mean} | left_csa_mean : {left_csa_mean}")
                    
                    self.check_and_update_estimated_offset(cam_name = "left",estimated_ratio = left_estimated_ratio_mean)
        
        ### End of, run the existing videoplayback build with video/picture mode to estimate ratio with sidecamera offsets set to zroe ###
        
            
        

if __name__ == "__main__":
       
    auto_calib = AutoCalibrate()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")
    