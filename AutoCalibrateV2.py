from CamContext import CamContext
from MarkerDetector import ArucoMarkerDetector
from CamWriter import CameraWriter
from ParseParams import *
from CameraStartUpJsonTemplate import *
from AutoCalibResult import *

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


class AutoCalibrateV2(ParseParams,CamContext,ArucoMarkerDetector,AutoCalibResult):
    
    def __init__(self):
        
        ParseParams.__init__(self)
        CamContext.__init__(self)
        ArucoMarkerDetector.__init__(self,self.args.aruco_dict)
        AutoCalibResult.__init__(self)
        
        
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
        
        # flag to indicate the progress of executing video playback with recorded video
        self.progress_done = threading.Event()
        self.progress_msg = None
        
        ############ log file names ###############
        self.log_file_name = {
            0 : {
                "front" : "FrontWithoutRatioOffsetAndWithoutSteeringOffset.txt",
                "right" : "RightWithoutRatioOffsetAndWithoutSteeringOffset.txt",
                "left"  : "LeftWithoutRatioOffsetAndWithoutSteeringOffset.txt"
            },
            1 : {
                "front" : "FrontWithRatioOffsetAndWithoutSteeringOffset.txt",
                "right" : "RightWithRatioOffsetAndWithoutSteeringOffset.txt",
                "left"  : "LeftWithRatioOffsetAndWithoutSteeringOffset.txt",
            },
            2 : {
                "front" : "FrontWithRatioOffsetAndWithSteeringOffset.txt",
                "right" : "RightWithRatioOffsetAndWithSteeringOffset.txt",
                "left"  : "LeftWithRatioOffsetAndWithSteeringOffset.txt"
            }
        }
        ###########################################
        
        # videoplayback build name to pring in cli
        self.build_name = self.args.videoplayback_build if len(self.args.videoplayback_build.split("/")) == 1 else self.args.videoplayback_build.split("/")[-1]
            
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
        
    def configure_path_width(self):
        """
        get PathWidth in cm from user and update in CameraStartUpJson
        """
        path_width_input = int(input(f"{self.get_formatted_timestamp()} Enter PathWidth [in cm]: "))
        
        # Update the PathWidth in CameraStartUpJson
        self.update_param_in_camera_startup_json(ParamType = "DebugParams",PathWidth = path_width_input)
        
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
        
        #### in debug mode ####
        ## if testing in debug mode where lane is not available in bench testing, copy the existing video from another dir and continue with rest of the logic.
        if self.args.debug:
            src_dir = "/home/pi/auto_calib_debug_data/"
            dest_dir = self.data_dir
            # shutil.copy(src_dir,dest_dir)
            if os.path.exists(dest_dir):
                os.system(f"sudo rm -rf {dest_dir}")
            os.system(f"sudo cp -r {src_dir} {dest_dir}")
        #######################
        
    def overwrite_existing_offset(self):
        """
        before executing video playback build, overwrite existing offsets to zero
        """        
        self.update_param_in_camera_startup_json(ParamType = "CamParams",
                                                 leftSideCameraOffset = 0,
                                                 rightSideCameraOffset = 0,
                                                 leftSideSteeringOffset = 0,
                                                 rightSideSteeringOffset = 0,
                                                 frontSideSteeringOffset = 0)
        
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
        
    def execute_videoplayback_build(self,video_file,mode):
        """
        execute and generate log for given video file
        param:
        video_file : Path to video file
        mode : 0->without ratio and steering offset, 1->with ratio and without steering offset , 2->with ratio and with steering offset
        """

        # get log file name for resptective camera and update SelectCameraForOfflineMode in CameraStartUpJson
        if video_file == self.args.front_cam_video_name:
            log_file = os.path.join(self.data_dir,self.log_file_name[mode]["front"])    
            self.update_param_in_camera_startup_json(ParamType = "DebugParams",SelectCameraForOfflineMode = 0)
            
        if video_file == self.args.right_cam_video_name:
            log_file = os.path.join(self.data_dir,self.log_file_name[mode]["right"])
            self.update_param_in_camera_startup_json(ParamType = "DebugParams",SelectCameraForOfflineMode = 1)
            
        if video_file == self.args.left_cam_video_name:
            log_file = os.path.join(self.data_dir,self.log_file_name[mode]["left"])
            self.update_param_in_camera_startup_json(ParamType = "DebugParams",SelectCameraForOfflineMode = 2)
            
        # get absolute path to video file
        video_file = os.path.join(self.data_dir,video_file)
        
        # check if the video file exists #
        if len(os.listdir(self.data_dir)) < self.args.n_cam:
            self.logger.error(f"Only {len(os.listdir(self.data_dir))} exists out of {self.args.n_cam}")
            
        ########### execute videoplayback build ########################
        # Start the progress indicator thread
        self.progress_msg = f"{self.get_formatted_timestamp()} Executing VideoPlayback build [{self.build_name}] with {video_file}"
        progress_thread = threading.Thread(target = self.print_progress)
        progress_thread.start()
        
        cmd = f"{self.args.videoplayback_build} --offline -i {video_file} -v > {log_file} 2>&1"
        
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
        
            
    def generate_log_using_existing_build(self,mode):
        """
        generate log of ratio and steering angle using videoplayback build
        Param:
        mode : 0->without ratio and steering offset, 1->with ratio and without steering offset , 2->with ratio and with steering offset
        """
        # update HostCommnflag :0 and HybridSwitch : false in CameraStartUpJson before running VideoPlayback with offline videos
        self.update_param_in_camera_startup_json(ParamType = "DebugParams",HostCommnFlag = 0,HybridSwitch = False)
        
        # iterate over front,left and right video files in directory and execute videoplayback build and generate log files
        for video_file in os.listdir(self.data_dir):
            if ".mp4" in video_file:
                self.execute_videoplayback_build(video_file,mode)
                
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
        
        return round(ratio_mean,3) , round(csa_mean,2)
    
    def get_ratio_and_csa_offset(self,measured_ratio,measured_csa,cam):
        """
        get the ratio offset and csa offset for left,right and front cam based on provided mean ratio and mean csa
        """
        if cam == "right":
            return round(self.current_json["DebugParams"][0]["PathWidth"] * (self.args.target_ratio - measured_ratio),2) , round((self.args.target_steering_angle - measured_csa),2)
        if cam == "left":
            return round(self.current_json["DebugParams"][0]["PathWidth"]*(measured_ratio - self.args.target_ratio),2) , round((self.args.target_steering_angle - measured_csa),2)
        if cam == "front":
            return None , round((self.args.target_steering_angle - measured_csa),2)
                    
    
    def estimate_and_update_offset_in_json(self,mode):
        """
        function to estimate offset from log file and update in json
        """
        # iterate for three cameras and estimate ratio and steering offset using generated log file
        for cam in ["front","right","left"]:
            log_file = os.path.join(self.data_dir,self.log_file_name[mode][cam])
                
            # get the mean ratio and mean csa from log file
            ratio_mean , csa_mean = self.get_ratio_csa_from_log_file(log_file)
            
            # using this mean of ratio and csa , estimate the offset
            ratio_offset , csa_offset = self.get_ratio_and_csa_offset(ratio_mean,csa_mean,cam)
                
                        
            ### update estimated offset based on mode ###
            if mode == 0:
                # ratio and csa without offset
                # ratio offset update in json
                self.update_result(cam = cam,ratio_without_offset = ratio_mean,ratio_offset = ratio_offset)
                
                # update estimated ratio offset in json
                if cam == "right": self.update_param_in_camera_startup_json(ParamType = "CamParams",rightSideCameraOffset = ratio_offset)
                if cam == "left" : self.update_param_in_camera_startup_json(ParamType = "CamParams",leftSideCameraOffset = ratio_offset)
                
            if mode == 1:
                # ratio with offset and csa without offset
                # csa offset update in json
                self.update_result(cam = cam,csa_without_offset = csa_mean,csa_offset = csa_offset)
                
                # update estimated steering offset in json
                if cam == "right": self.update_param_in_camera_startup_json(ParamType = "CamParams",rightSideSteeringOffset = csa_offset)
                if cam == "left" : self.update_param_in_camera_startup_json(ParamType = "CamParams",leftSideSteeringOffset = csa_offset)
                if cam == "front": self.update_param_in_camera_startup_json(ParamType = "CamParams",frontSideSteeringOffset = csa_offset)
                
            if mode == 2:
                # ratio with offset and csa with offset
                self.update_result(cam = cam,ratio_with_offset = ratio_mean,csa_with_offset = csa_mean)
                
            
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
        
        ############# Configure PathWidth #######################
        self.configure_path_width()
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
        
        ######## Before Executing Videoplayback build overwrite existing offsets with zero #######
        self.overwrite_existing_offset()
        ##########################################################################################
        
        
        ############### Generate Log files using VideoPlayback build #############################
        
        ####### Without Ratio Offset and Without Steering Offset #######
        self.logger.info(f"########## Executing {self.build_name} without Ratio & Without Steering Offset ##########")
        self.generate_log_using_existing_build(mode = 0)
        ################################################################
        
        ###### Estimate ratio offset and update in json #######
        self.estimate_and_update_offset_in_json(mode = 0)
        self.print_result()
        #######################################################
        
        ##### With Ratio offset and without Steering Offset ######
        self.logger.info(f"########## Executing {self.build_name} with Ratio & Without Steering Offset ##########")
        self.generate_log_using_existing_build(mode = 1)
        ##########################################################
        
        ##### Estimate steering offset and update in json ####
        self.estimate_and_update_offset_in_json(mode = 1)
        self.print_result()
        ######################################################
        
        ##### With Ratio Offset and With Steering Offset #####
        self.logger.info(f"########## Executing {self.build_name} with Ratio & With Steering Offset ##########")
        self.generate_log_using_existing_build(mode = 2)
        ######################################################
        
        ##### Estimate steering offset and update in json ####
        self.estimate_and_update_offset_in_json(mode = 2)
        self.print_result()
        ######################################################
        
        ##########################################################################################
        
    
if __name__ == "__main__":
       
    auto_calib = AutoCalibrateV2()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")