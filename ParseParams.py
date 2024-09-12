import argparse
import logging

class ParseParams:
    
    def __init__(self):
        
        logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s", level=logging.INFO, datefmt="%d/%m/%y %H:%M:%S")
        self.logger = logging.getLogger()
        
        parser = argparse.ArgumentParser(description = "Script to automate the calibration.")
        
        parser.add_argument("--json_path",default = None,help = "json file for path to json file for read,modify and updating the params (default : None)")
        parser.add_argument("--n_cam",type = int ,default = 3,help = "number of cameras connected to bot (default : 3)")
        
        self.args = parser.parse_args()
        
        
    def check_params(self):
        
        if self.args.json_path == None:
            self.logger.error("No Json File provided")
            return False
        
        return True