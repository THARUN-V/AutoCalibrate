from CamContext import CamContext
from MarkerDetector import ArucoMarkerDetector
from CamWriter import CameraWriter
from ParseParams import *
from CameraStartUpJsonTemplate import *

import json 
import cv2
from datetime import datetime
import os 
import numpy
import sys
import threading
import time
from prettytable import PrettyTable
import socket


class AutoCalibrateV2(ParseParams,CamContext,ArucoMarkerDetector):
    
    def __init__(self):
        
        ParseParams.__init__(self)
        CamContext.__init__(self)
        ArucoMarkerDetector.__init__(self,self.args.aruco_dict)
        
        
        ### configure seecam ###
        self.configure_seecams()
        ########################
        
        self.current_json = None
        
        # check if all the required params are provided from cli
        # else print the appropriate log and exit.
        if not self.check_params():
            sys.exit()
            
        # name for backed up CameraStartUpJson
        self.bkp_camera_startup_json_name = f"CameraStartUpJson_bkp_{datetime.now().strftime('%d-%m-%y_%H-%M-%S')}.json"
        
        ###### create a directory to store data ######
        # get the bot name
        self.bot_name = socket.gethostname()
        # remove the C from bot name
        self.bot_name = self.bot_name.split("C")[0].strip("-")
        self.data_dir = os.path.join(os.getcwd(),self.bot_name+"_"+"AutoCalibData"+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        # create directory to writer log and video 
        os.mkdir(self.data_dir)
        ##############################################
        
        ########## param for video recording ##########
        # count to skip frames that is of green color
        self.skip_frame_count = 3
        # count to keep track of frames being written
        self.current_frame_count = 1
        ###############################################
            
    def get_formatted_timestamp(self):
        """
        Utility function to add formatted string with time stamp and log level, while taking user input.
        """
        
        log_level = "INFO"
        timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        
        return f"[{timestamp}, {log_level}]"
    
    def update_param_in_camera_startup_json(self,ParamType,**kwargs):
        
        # read the current version of CameraStartUpJson
        with open(self.args.json_path,"r") as existing_json_path:
            existing_json_file = json.load(existing_json_path)
            
        # update the required params
        for key,val in kwargs.items():
            existing_json_file[ParamType][0][key] = val
                
        # write the update verison of CameraStartUpJson
        with open(self.args.json_path,"w") as updated_json_path:
            json.dump(existing_json_file,updated_json_path,indent=4)
            
        # after updating json file, update current json file
        with open(self.args.json_path,"r") as updated_curr_json:
            self.current_json = json.load(updated_curr_json)
        
    def configure_camera_startup_json(self):
        """
        This function checks for CameraStartUpJon.
        if CameraStartUpJson is present take the current CameraStartUpJson
        else create one with template CameraStartUpJson
        """
        try:
            
            with open(self.args.json_path,"r") as camera_startup_json:
                self.current_json = json.load(camera_startup_json)
                
            # if CameraStartUpJson is already present ask the user, if it has to backed up
            self.logger.info("**** This Script overwrites the current json file for updating params , Take backup of current json file before proceeding if needed ****")
            
            bkp_choice = input(f"{self.get_formatted_timestamp()} Enter y to take backup , n to skip : ")
            
            # while taking input, check for proper input 
            while bkp_choice not in ["y","n"]:
                self.logger.info("######## Please provide y or n , to take backup of current CameraStartUpJson ########")
                bkp_choice = input(f"{self.get_formatted_timestamp()} Enter y to take backup , n to skip : ")
            
            # if yes take backup of current CameraStartUpJson by copying it with different name
            # the backed up CameraStartUpJson will be saved as CameraStartUpJson_bkp_<current_date_and_time>
            if bkp_choice == "y":
                with open(self.bkp_camera_startup_json_name,"w") as bkp_camera_startup_json:
                    json.dump(self.current_json,bkp_camera_startup_json,indent=4)
                # log the msg regarding successful backup of current CameraStartUpJson
                self.logger.info(f"Successfully backed up current CameraStartUpjson at {self.bkp_camera_startup_json_name}")
            if bkp_choice == "n":
                pass
                
                
        except FileNotFoundError:
            
            # create a template CameraStartUpJson
            with open(self.args.json_path,"w") as template_camera_startup_json:
                json.dump(CameraStartUpJsonTemplate,template_camera_startup_json,indent=4)
                
            # get the created json file 
            
            with open(self.args.json_path,"r") as new_camera_startup_json:
                self.current_json = json.load(new_camera_startup_json)
                
            self.logger.info("############# CameraStartUpJson Not Found , Created One ##################")
            
    def configure_bot_type(self):
        """
        gets input from user and updates BotType in CameraStartUpJson
        """
        
        ##### print user with available bot type and choose from #####
        self.logger.info("+---------------------------------- Available BotType ----------------------------------+")
        bot_type_info_table = PrettyTable()
        bot_type_info_table.field_names = ["BotType","Info"]
        bot_type_info_table.add_row(["1","APPU/JUMBO Bot with Camera mounted on FRP"])
        bot_type_info_table.add_row(["2","JUMBO Bot with raised FRP and camera mounted on metal plate"])
        print(bot_type_info_table)
        ###############################################################
        
        ##### get input from user for BotType #####
        bot_type = int(input(f"{self.get_formatted_timestamp()} Enter BotType : "))
        
        ## failsafe to make user choose bot_type out of available list ##
        while bot_type not in [1,2]:
            self.logger.info("#### please enter BotType from above Available BotType ####")
            bot_type = int(input(f"{self.get_formatted_timestamp()} Enter BotType : "))
        
        # update the BotType in CameraStartUpJson
        self.update_param_in_camera_startup_json(ParamType="CamParams",BotType=bot_type)
        
    def configure_lane_colour(self):
        """
        get LaneColourToScan from user and update it in CameraStartUpJson
        """
        lane_colour_input = int(input(f"{self.get_formatted_timestamp()} Enter LaneColor : "))
        
        # update the lane colour in CameraStartUpJson
        self.update_param_in_camera_startup_json(ParamType="CamParams",LaneColourToScan=lane_colour_input)
        
    def configue_bot_placement(self):
        """
        get conformation from user regarding, whether the bot is placed and it's good to continue auto calibration.
        """
        bot_placement_input = input(f"{self.get_formatted_timestamp()} Enter y when BOT is positioned properly [predefined calibration position] , n to exit : ")
        
        while bot_placement_input not in ["y","n"]:
            self.logger.info("########### Please provide y or n to proceed for AutoCalibration ###########")
            bot_placement_input = input(f"{self.get_formatted_timestamp()} Enter y when BOT is positioned properly [predefined calibration position] , n to exit : ")
            
        if bot_placement_input == "y" : pass
        if bot_placement_input == "n" : sys.exit()
        
        
    def configure_seecams(self):
        """
        1. scans and gets the serial number of seecam connected.
        2. if no cam is connected, exists the code by displaying log
        3. if number of connected cam and configured number of cam doesn't match , program exists with error msg.
        4. maintains a dict to store camera name and its serial number
        """
        
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
        
    def detect_and_map_cam_ids(self):
        """
        Function to detect markers in image and map the camera ids.
        """
        self.logger.info("========= Performing Camera Id Mapping =========")
        
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
                                self.update_param_in_camera_startup_json(ParamType="CamParams",frontCameraId=cam.serial_number)
                                self.cam_name_and_index["FrontCam"] = cam.camera_index
                                id_detected = True
                            if current_marker_id == self.args.right_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.update_param_in_camera_startup_json(ParamType="CamParams",rightCameraId=cam.serial_number)
                                self.cam_name_and_index["RightCam"] = cam.camera_index
                                id_detected = True
                            if current_marker_id == self.args.left_cam_marker_id:
                                self.logger.info(f"Detected Marker Id {current_marker_id} in {cam.serial_number}")
                                self.update_param_in_camera_startup_json(ParamType="CamParams",leftCameraId=cam.serial_number)
                                self.cam_name_and_index["LeftCam"] = cam.camera_index
                                id_detected = True
                            
            if id_detected:
                cap.release()
                
                
        self.logger.info(f"Mapped Camera Id's FrontCameraId : {self.current_json['CamParams'][0]['frontCameraId']} | RightCameraId : {self.current_json['CamParams'][0]['rightCameraId']} | LeftCameraId : {self.current_json['CamParams'][0]['leftCameraId']}")
        self.logger.info(f"Mapped Camera Idx FrontCameraIdx : {self.cam_name_and_index['FrontCam']} | RightCameraIdx : {self.cam_name_and_index['RightCam']} | LeftCameraIdx : {self.cam_name_and_index['LeftCam']}")
        
        self.logger.info("=========    Done Camera Id Mapping    =========")
        
        
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
        
    def run_calibration(self):
        """
        Main function where all the functions related to auto calibration are called in sequence.
        """
        
        ########### Configure CameraStartUpJson #################
        self.configure_camera_startup_json()
        #########################################################
        
        ########### Configure BotType ###########################
        self.configure_bot_type()
        #########################################################
        
        ############# Configure LaneColourToScan ################
        self.configure_lane_colour()
        #########################################################
        
        ############# configure bot placement in predefined calibration position ###########
        self.configue_bot_placement()
        ####################################################################################
        
        ############# Perform Camera Id Mapping ###############
        if self.args.skip_camera_id_mapping:
            # display to user about skipping camera device id mapping
            self.logger.info("################# Skipping Camera Device Id Mapping #################")
        if not self.args.skip_camera_id_mapping:
            self.detect_and_map_cam_ids()
        #######################################################
        
        ############ Record Video ####################
        self.record_video()
        ##############################################
        
        
        
    
if __name__ == "__main__":
       
    auto_calib = AutoCalibrateV2()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")