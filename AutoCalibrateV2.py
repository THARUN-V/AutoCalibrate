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
        
    def check_and_create_json(self):
        """
        This function checks for CameraStartUpJon.
        if CameraStartUpJson is present take the current CameraStartUpJson
        else create one with template CameraStartUpJson
        """
        try:
            
            with open(self.args.json_path,"r") as camera_startup_json:
                self.current_json = json.load(camera_startup_json)
                
        except FileNotFoundError:
            
            # create a template CameraStartUpJson
            with open(self.args.json_path,"w") as template_camera_startup_json:
                json.dump(CameraStartUpJsonTemplate,template_camera_startup_json,indent=4)
                
            self.logger.info("############# CameraStartUpJson Not Found , Created One ##################")
        
    def run_calibration(self):
        """
        Main function where all the functions related to auto calibration are called in sequence.
        """
        
        ########### check for CameraStartUpJson #################
        self.check_and_create_json()
        #########################################################
    
if __name__ == "__main__":
       
    auto_calib = AutoCalibrateV2()
    try:
        auto_calib.run_calibration()
    except KeyboardInterrupt:
        print("------ exiting ----------")