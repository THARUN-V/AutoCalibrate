import argparse
import logging

class ParseParams:
    
    def __init__(self):
        
        logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s", level=logging.INFO, datefmt="%d/%m/%y %H:%M:%S")
        self.logger = logging.getLogger()
        
        parser = argparse.ArgumentParser(description = "Script to automate the calibration.",formatter_class=argparse.RawTextHelpFormatter)
        
        parser.add_argument("--json_path",default = None,help = "json file for path to json file for read,modify and updating the params (default : None)")
        parser.add_argument("--n_cam",type = int ,default = 3,help = "number of cameras connected to bot (default : 3)")
        parser.add_argument("--resolution",type = int, default = 1 , help = "resoultion of image to get from camera. (default : 1) \n supported resolution \n 0 : (640,480) \n 1 : (960,540) \n 2 : (1280,720) \n 3 : (1280,960) \n 4 : (1920,1080)")

        self.args = parser.parse_args()
        
        
    def check_params(self):
        
        if self.args.json_path == None:
            self.logger.error("No Json File provided")
            return False
        
        return True