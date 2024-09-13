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
        parser.add_argument("--cam_switch",type = int, default = 0 , help = "wheteher to use one cam at a time or all cam at a time for detecting marker. (default : 0) \nsupported options\n0 : use one cam at a time\n1 : use all cameras")
        
        #### params related to marker detection #####
        parser.add_argument("--aruco_dict",type = str , default = "DICT_4X4_50",help = "Aruco Dictionary family used for detection. (default : DICT_4X4_50)")
        parser.add_argument("--front_cam_marker_id",type = int , default = 0 , help = "marker id for front camera. (default : 0)")
        parser.add_argument("--right_cam_marker_id",type = int , default = 1 , help = "marker id for right camra. (default : 1)")
        parser.add_argument("--left_cam_marker_id",type = int , default = 2, help = "marker id for left camera. (default : 2)")
        
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
        
        if self.args.json_path == None:
            self.logger.error("No Json File provided")
            return False
        
        return True