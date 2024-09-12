from ParseParams import *
from CamContext import CamContext
from CamCapture import CameraCapture
import json
import logging


class AutoCalibrate(ParseParams,CamContext,CameraCapture):
    
    def __init__(self):
        
        ParseParams.__init__(self)
        CamContext.__init__(self)
        CameraCapture.__init__(self)
        
        # check if all the required params are provided from cli
        # else print the appropriate log and exit.
        if not self.check_params():
            exit()    
            
        # scan the camera and get camera serial numbers
        self.see_cams = self.get_seecam()
        # check if the scanned and provided number of cameras match
        if len(self.see_cams) != self.args.n_cam:
            self.logger.error(f"Found {len(self.see_cams)} cameras out of {self.args.n_cam}")
            exit()
        
        
    def run_calibration(self):
        # print(self.args.json_path)
        # print(self.args.n_cam)
        pass

if __name__ == "__main__":
    
    # params = ParseParams()
    
    # print(params.args.json_path)
    
    # with open(params.args.json_path,"r") as json_file:
    #     f = json.load(json_file)
        
    # # f["test_val"] = 15975345685
    # # del f["new_val"]
    
    # # with open(params.args.json_path,"w") as json_file:
    # #     json.dump(f,json_file)
    
    # # print(json.dumps(f,indent = 4))
    
    # context = CamContext()
    
    # for cam in context.get_seecam():
    #     print(cam.serial_number)
    #     print(cam.camera_index)
    #     print("=========================================")
    
    auto_calib = AutoCalibrate()
    auto_calib.run_calibration()