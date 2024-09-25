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
import sys
import threading
import time
from prettytable import PrettyTable

class AutoCalibrate(ParseParams,CamContext,ArucoMarkerDetector):
    
    def __init__(self):
        
        ParseParams.__init__(self)
        CamContext.__init__(self)
        ArucoMarkerDetector.__init__(self,self.args.aruco_dict)
        
        
        # check if all the required params are provided from cli
        # else print the appropriate log and exit.
        if not self.check_params():
            sys.exit()    
            
        # load the current json file
        with open(self.args.json_path,"r") as f:
            self.current_json = json.load(f) 
            
        # scan the camera and get camera serial numbers
        self.see_cams = self.get_seecam()
        
        # if no cameras found exit with error message
        if self.see_cams == None:
            self.logger.error("!!! No Cameras Found !!!")
            sys.exit()
        
        # check if the scanned and provided number of cameras match
        if len(self.see_cams) != self.args.n_cam:
            self.logger.error(f"Found {len(self.see_cams)} cameras out of {self.args.n_cam}")
            sys.exit()
            
        self.cam_name_and_index = {
            "FrontCam":None,
            "RightCam":None,
            "LeftCam":None
        }
        
        # path for video file to store
        
        # count to skip frames that is of green color
        self.skip_frame_count = 3
        # count to keep track of frames being written
        self.current_frame_count = 1
        # directory to store video and log files
        self.data_dir = os.path.join(os.getcwd(),datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        # create directory to writer log and video 
        os.mkdir(self.data_dir)
        
        # flag to print progress
        self.first_prog_msg = True
        
        # flag to indicate the progress of executing video playback with recorded video
        self.progress_done = threading.Event()
        self.progress_msg = None
        
        # videoplayback build name to pring in cli
        self.build_name = self.args.videoplayback_build if len(self.args.videoplayback_build.split("/")) == 1 else self.args.videoplayback_build.split("/")[-1]
        
        self.table = PrettyTable()
        self.table.field_names = ["CamName","CamId","RatioWithoutOffset","RatioWithOffset","CsaWithoutOffset","CsaWithOffset","RatioOffset","SteeringAngleOffset","ResultCamTilt","ResultCamRotate"]
        # self.table.add_row(["","","WithoutOffset","WithOffset","WithoutOffset","WithOffset","",""])
        
        self.FrontCamRow = ["FrontCam","","","","","","","","",""]
        self.RightCamRow = ["RightCam","","","","","","","","",""]
        self.LeftCamRow  = ["LeftCam","","","","","","","","",""]
            
    def color_text(self,text, color):
        # Define ANSI escape codes
        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"  # Reset to default color

        # Choose the color based on input
        if color.lower() == 'red':
            return f"{RED}{text}{RESET}"
        elif color.lower() == 'green':
            return f"{GREEN}{text}{RESET}"
        else:
            return text  # Return the original text if the color is not recognized
        
    
    def print_pretty_table(self):
        
        
        # check for pass or fail based on ratio and steering angle, without offsets
        ########## RIGHT CAMERA ##############
        if not (self.RightCamRow[2] >= self.args.ratio_without_side_cam_offset_min and self.RightCamRow[2] <= self.args.ratio_without_side_cam_offset_max):
            self.RightCamRow[8] = self.color_text("FAIL","red")
        else:
            self.RightCamRow[8] = self.color_text("PASS","green")
        if not (self.RightCamRow[4] >= self.args.csa_without_offset_min and self.RightCamRow[4] <= self.args.csa_without_offset_max):
            self.RightCamRow[9] = self.color_text("FAIL","red")
        else:
            self.RightCamRow[9] = self.color_text("PASS","green")
        ######################################
        
        ########### LEFT CAMERA ######################
        if not(self.LeftCamRow[2] >= self.args.ratio_without_side_cam_offset_min and self.RightCamRow[2] <= self.args.ratio_without_side_cam_offset_max):
            self.LeftCamRow[8] = self.color_text("FAIL","red")
        else:
            self.LeftCamRow[8] = self.color_text("PASS","green")
        if not(self.LeftCamRow[4] >= self.args.csa_without_offset_min and self.LeftCamRow[4] <= self.args.csa_without_offset_max):
            self.LeftCamRow[9] = self.color_text("FAIL","red")
        else:
            self.LeftCamRow[9] = self.color_text("PASS","green")
        ##############################################
        
        ############# FRONT CAM #########################
        if not(self.FrontCamRow[2] >= self.args.ratio_without_side_cam_offset_min and self.FrontCamRow[2] <= self.args.ratio_without_side_cam_offset_max):
            self.FrontCamRow[8] = self.color_text("FAIL","red")
        else:
            self.FrontCamRow[8] = self.color_text("PASS","green")
        if not(self.FrontCamRow[4] >= self.args.csa_without_offset_min and self.FrontCamRow[4] <= self.args.csa_without_offset_max):
            self.FrontCamRow[9] = self.color_text("FAIL","red")
        else:
            self.FrontCamRow[9] = self.color_text("PASS","green")
        #################################################
        
        self.table.add_row(self.FrontCamRow)
        self.table.add_row(self.RightCamRow)
        self.table.add_row(self.LeftCamRow)
        
        print(self.table)
            
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
                sys.exit()
            else:
                return id[0]
        
        # iterate over seecam object and detect markers
        for cam in self.see_cams:
            # get the current cam index , fetch frame and detect marker
            cap = cv2.VideoCapture(cam.camera_index)
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.h)
            cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
            cap.set(cv2.CAP_PROP_FPS,15)
            
            
            # flag to check if id is detected for current cam
            id_detected = False
            
            while not id_detected:
                
                ret , frame = cap.read()
                
                if ret:
                    cv2.imwrite("test_auto_calib.png",frame)
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
                                self.FrontCamRow[1] = cam.serial_number
                                id_detected = True
                            if current_marker_id == self.args.right_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.current_json["CamParams"][0]["rightCameraId"] = cam.serial_number
                                self.cam_name_and_index["RightCam"] = cam.camera_index
                                self.RightCamRow[1] = cam.serial_number
                                id_detected = True
                            if current_marker_id == self.args.left_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.current_json["CamParams"][0]["leftCameraId"] = cam.serial_number
                                self.cam_name_and_index["LeftCam"] = cam.camera_index
                                self.LeftCamRow[1] = cam.serial_number
                                id_detected = True
                            
            if id_detected:
                cap.release()
                
    def record_video(self):
        """
        utility function to record video of front, right and left for generating log file to estimate offsets.
        """
        
        # initialize cam writer object
        out = CameraWriter(self.data_dir,self.w,self.h)
        for cam_name , cam_index in self.cam_name_and_index.items():
            cap = cv2.VideoCapture(cam_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.h)
            cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
            cap.set(cv2.CAP_PROP_FPS,15)
            
            while self.current_frame_count <= self.args.record_frame_count:
                ret , frame = cap.read()
                if ret:
                    if self.current_frame_count > self.skip_frame_count:
                        out.write_image(cam_name,frame)
                        
                        #### print progress of writing frames ######
                        self.log_progress(f"{self.get_formatted_timestamp()} Recording Video Of {cam_name} [{self.current_frame_count}/{self.args.record_frame_count} frames]")
                        # End of, print progress of writing frames #
                        
                    self.current_frame_count += 1
            self.current_frame_count = 0
        # release the video writer objects
        out.clear_writer()
        
    def generate_log_using_existing_build(self):
        """
        Utility function to genreate log to get ratio and steering angle, using the existing build.
        """
                
        # check if the video file exists #
        if len(os.listdir(self.data_dir)) < self.args.n_cam:
            self.logger.error(f"Only {len(os.listdir(self.data_dir))} exists out of {self.args.n_cam}")
        
        self.logger.info(f"Executing VideoPlayback build [{self.build_name}] with lefSideCameraOffset : {self.current_json['CamParams'][0]['leftSideCameraOffset']} , rightCameraOffset : {self.current_json['CamParams'][0]['rightSideCameraOffset']}")
        
        # before executing, check if HostCommunication and HybridSwitch is set to 0 and false
        if self.current_json["DebugParams"][0]["HostCommnFlag"] != 0 and self.current_json["DebugParams"][0]["HybridSwitch"] != False:
            self.current_json["DebugParams"][0]["HostCommnFlag"] = 0
            self.current_json["DebugParams"][0]["HybridSwitch"] = False
            # update the params in json file before executing videoplayback script
            with open(self.args.json_path,"w") as updated_json:
                json.dump(self.current_json,updated_json,indent = 4)
        
        # iterater over the video file and generate log 
        for video_file in os.listdir(self.data_dir):
            self.progress_done.clear()
            if ".mp4" in video_file:    
                # set the flag for changing camera to left or right in CameraStartUpJson 
                if "Right" in video_file:
                    # set SelectCameraForOfflineMode to 1
                    self.current_json["DebugParams"][0]["SelectCameraForOfflineMode"] = 1
                    # update in json before executing videoplayback build
                    with open(self.args.json_path,"w") as updated_json:
                        json.dump(self.current_json,updated_json,indent = 4)
                if "Left" in video_file:
                    # set SelectCameraForOfflineMode to 2
                    self.current_json["DebugParams"][0]["SelectCameraForOfflineMode"] = 2
                    # update in json before executing videoplayback build
                    with open(self.args.json_path,"w") as updated_json:
                        json.dump(self.current_json,updated_json,indent = 4)
                        
                if "Front" in video_file:
                    # set SelectCameraForOfflineMode to 0
                    self.current_json["DebugParams"][0]["SelectCameraForOfflineMode"] = 0
                    # update in json before executing videoplayback build
                    with open(self.args.json_path,"w") as updated_json:
                        json.dump(self.current_json,updated_json,indent = 4)
                        
                # command to run videoplayback build
                log_file = os.path.join(self.data_dir,video_file.split(".mp4")[0]+"Log.txt")
                
                # Start the progress indicator thread
                self.progress_msg = f"{self.get_formatted_timestamp()} Executing VideoPlayback build [{self.build_name}] with {video_file}"
                progress_thread = threading.Thread(target = self.print_progress)
                progress_thread.start()
                
                ### for debug ###
                # print(f"VideoName : {os.path.join(self.data_dir,video_file)}")
                # cmd = f"{self.args.videoplayback_build} -i /home/tharun/THARUN/Data/TestVideos/TKAP_ORANGE_LANES/Left_Camera_Orange_Video_8_161223.mp4 -v > {log_file} 2>&1"yyy
                if self.args.debug:
                    if os.path.exists(self.args.video_path):
                        cmd = f"{self.args.videoplayback_build} --offline -i {self.args.video_path} -v > {log_file} 2>&1"
                    else:
                        self.logger.error(f"!!! Video File {self.args.video_path} doesn't Exist !!!")
                
                # execute VideoPlayback with recorded video
                else:
                    cmd = f"{self.args.videoplayback_build} --offline -i {os.path.join(self.data_dir,video_file)} -v > {log_file} 2>&1"
                
                # run the command
                process = os.system(cmd)
                
                # check if the process has executed and terminated successfully
                if process == 0:
                    self.progress_done.set()
                    progress_thread.join()
                    # self.logger.info(f"Done with {os.path.join(self.data_dir,video_file)}")
                else:
                    self.progress_done.set()
                    progress_thread.join()
                    self.logger.error(f"!!!! Error in Executing VideoPlayback Build with current {video_file} file !!!!")
                    sys.exit()
    
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
        
        return ratio_mean , csa_mean
    
    def estimate_offset(self,measured_ratio,measured_steering_angle,cam_name = None):
        """
        Function to estimate side camera offset using equation and offset in steering angle.
        """
        
        if cam_name == None:
            self.logger.error(f"!!!!! No camera name provided for estimate offset method !!!!!!")
            sys.exit()
        
        if cam_name == "right":
            return int(self.current_json["DebugParams"][0]["PathWidth"] * (self.args.target_ratio - measured_ratio)) , int(self.args.target_steering_angle - measured_steering_angle)
        
        if cam_name == "left":
            return int(self.current_json["DebugParams"][0]["PathWidth"] * (1 - measured_ratio - self.args.target_ratio)) , int(self.args.target_steering_angle - measured_steering_angle)
        
    def check_and_update_estimated_offset(self,estimated_ratio,estimated_csa,cam_name = None):
        """
        utility function to check whether the current estimated ratio without side cam offset lies in acceptable range
        and update the same in json file.
        """            
        Estimated_SideCameraOffset , Estimated_SideCameraSteeringOffset = self.estimate_offset(cam_name = cam_name,measured_ratio = estimated_ratio,measured_steering_angle = estimated_csa)
            
        # Overwrite right camera offset in json file
        with open(self.args.json_path,"w") as updated_json:
            self.current_json["CamParams"][0][f"{cam_name}SideCameraOffset"] = Estimated_SideCameraOffset
            self.current_json["CamParams"][0][f"{cam_name}SideSteeringOffset"] = Estimated_SideCameraSteeringOffset
            json.dump(self.current_json,updated_json,indent = 4)
        self.logger.info(f"Done , Overwriting of {cam_name}SideCameraOffset and {cam_name}SteeringOffset in Json file")
        
        if cam_name == "right": self.RightCamRow[6] = Estimated_SideCameraOffset ; self.RightCamRow[7] = Estimated_SideCameraSteeringOffset
        if cam_name == "left" : self.LeftCamRow[6] = Estimated_SideCameraOffset ; self.LeftCamRow[7] = Estimated_SideCameraSteeringOffset
        
    def get_formatted_timestamp(self):
        """
        Utility function to add formatted string with time stamp and log level, while taking user input.
        """
        
        log_level = "INFO"
        timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        
        return f"[{timestamp}, {log_level}]"
    
    def log_progress(self,message):
        """
        Utility function to log the progress.
        """
        if abs(self.current_frame_count-self.args.record_frame_count == 0):
            sys.stdout.write(f"\r{message}")    
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\r{message}")
            sys.stdout.flush()
        
        
    def print_progress(self):
        """
        Utility function to print the progress of executing VideoPlayback build with the recorded video.
        """
        symbols = ['./','.\\']
        while not self.progress_done.is_set():
            for symbol in symbols:
                sys.stdout.write(f"\r{self.progress_msg} {symbol}")
                sys.stdout.flush()
                time.sleep(0.5)
        sys.stdout.write(f'\r{self.progress_msg} [Done] \n')
        sys.stdout.flush()
        
    def run_calibration(self):
        
        
        ########## Prompt the user regarding overwritting of current json file and instruct the user to take backup of current json file ################
        self.logger.info("**** This Script overwrites the current json file for updating params , Take backup of current json file before proceeding if needed ****")
        # choice = input(f"{self.get_formatted_timestamp()} Enter y,to proceed , n to exit : ")
        bkp_choice = input(f"{self.get_formatted_timestamp()} Enter y to take backup , n to skip : ")
        
        if bkp_choice == "y":
            # create a bkp of current json file
            bkp_json_path = f'CameraStartUpJson_bkp_{datetime.now().strftime("%d-%m-%y_%H-%M-%S")}.json' 
            with open(bkp_json_path,"w") as bkp_json:
                json.dump(self.current_json,bkp_json,indent = 4)
            self.logger.info(f"Successfully backed up current json at {bkp_json_path}")
        if bkp_choice == "n":
            pass
        ####### End of, Prompt the user regarding overwritting of current json file and instruct the user to take backup of current json file ###########
        
        ######### Instruct the user asking if the bot is palced in predefined postion, and whether to proceed for calibartion ##########
        choice = input(f"{self.get_formatted_timestamp()} Enter y when BOT is positioned properly [predefined calibration position] , n to exit : ")
        
        if choice == "y": pass
        if choice == "n": sys.exit()
        ##### End of, Instruct the user asking if the bot is palced in predefined postion, and whether to proceed for calibartion ######
        
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
                
                
        ### Record video of Front,Left and Right for debug and estimating offsets #########
        self.record_video()
        ###  End Record video of Front,Left and Right for debug and estimating offsets ####
        
        ########################### side camera offset estimation ######################################################
        
        ### for side camera estimation set the current side camera offsets to zero in current json file ###
        self.logger.info(f"Setting leftSideCameraOffset and rightSideCameraOffset to 0")
        self.current_json["CamParams"][0]["leftSideCameraOffset"] = 0
        self.current_json["CamParams"][0]["rightSideCameraOffset"] = 0
        with open(self.args.json_path,"w") as updated_json:
            json.dump(self.current_json,updated_json,indent = 4)
        self.logger.info(f"Overwritten leftSideCameraOffset : 0 and rightSideCameraOffset : 0")
        ############## end of setting side camera offsets to zero in current json file ####################
        
        ##### run the existing videoplayback build with video/picture mode to estimate ratio with sidecamera offsets set to zero  #######
        self.generate_log_using_existing_build()
        ### End of, run the existing videoplayback build with video/picture mode to estimate ratio with sidecamera offsets set to zero ###
        
        # get the log file for right cam and left cam
        for log_file in os.listdir(self.data_dir):
            log_file = os.path.join(self.data_dir,log_file)
            if ".txt" in log_file:
                # get the right cam log file
                if "Right" in log_file:
                    # get the ratio and csa using log file
                    
                    self.logger.info("======== Estimating and Updating rightSideCamearaOffset and rightSteeringOffset ========")
                    
                    right_estimated_ratio_mean , right_csa_mean = self.get_ratio_csa_from_log_file(log_file)
                    
                    self.RightCamRow[2] = round(right_estimated_ratio_mean,2)
                    self.RightCamRow[4] = round(right_csa_mean,2)
                    
                    self.logger.info(f"right_ratio_mean : {right_estimated_ratio_mean} | right_csa_mean : {right_csa_mean}")
                
                    self.check_and_update_estimated_offset(cam_name = "right", estimated_ratio = right_estimated_ratio_mean , estimated_csa = right_csa_mean)
                    
                    self.logger.info("======== Estimating and Updating rightSideCamearaOffset and rightSteeringOffset [Done] ========")
                        
                # get the left cam log file
                if "Left" in log_file:
                    
                    # get the ratio and csa using the log file
                    
                    self.logger.info("======== Estimating and Updating leftSideCamearaOffset and leftSteeringOffset ========")
                    
                    left_estimated_ratio_mean , left_csa_mean = self.get_ratio_csa_from_log_file(log_file)
                    
                    self.LeftCamRow[2] = round(left_estimated_ratio_mean,2)
                    self.LeftCamRow[4] = round(left_csa_mean,2)
                    
                    self.logger.info(f"left_ratio_mean : {left_estimated_ratio_mean} | left_csa_mean : {left_csa_mean}")
                    
                    self.check_and_update_estimated_offset(cam_name = "left",estimated_ratio = left_estimated_ratio_mean , estimated_csa = left_csa_mean)
                    
                    self.logger.info("======== Estimating and Updating leftSideCamearaOffset and leftSteeringOffset [Done] ========")
                    
                # get the front cam log file
                if "Front" in log_file:
                    
                    self.logger.info("============ Estimating Front ratio and csa ================")
                    
                    front_estimated_ratio_mean , front_csa_mean = self.get_ratio_csa_from_log_file(log_file)
                    
                    self.FrontCamRow[2] = round(front_estimated_ratio_mean,2)
                    self.FrontCamRow[4] = round(front_csa_mean,2)
                    
                    self.logger.info(f"front_ratio_mean : {front_estimated_ratio_mean} | front_csa_mean : {front_csa_mean}")
                    
        self.print_pretty_table()
                

if __name__ == "__main__":
       
    auto_calib = AutoCalibrate()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")
    