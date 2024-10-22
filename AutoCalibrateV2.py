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
        
        self.current_json = None
        
        # check if all the required params are provided from cli
        # else print the appropriate log and exit.
        if not self.check_params():
            sys.exit()
            
        # name for backed up CameraStartUpJson
        self.bkp_camera_startup_json_name = f"CameraStartUpJson_bkp_{datetime.now().strftime('%d-%m-%y_%H-%M-%S')}.json"
            
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
        
        
        
    
if __name__ == "__main__":
       
    auto_calib = AutoCalibrateV2()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")