from enum import Enum
from prettytable import PrettyTable

    
class CamCalibResultTable:
    
    def __init__(self):
        
        # table to print cam calib data in formatted way
        self.table = PrettyTable()
        
        # first row of table indicating camera params
        self.table_field_names = ["CamName",                # 0
                                  "CamId",                  # 1
                                  "RatioWithoutOffset",     # 2
                                  "RatioWithOffset",        # 3
                                  "CsaWithoutOffset",       # 4
                                  "CsawithOffset",          # 5
                                  "RatioOffset",            # 6
                                  "SteeringAngleOffset",    # 7
                                  "ResultCamTilt",          # 8
                                  "ResultCamRotate",        # 9
                                  "RaitoAcceptableWithOffset",# 10
                                  "CsaAcceptableWithOffset"]  # 11      
        self.table.field_names = self.table_field_names
        ########### index to write data for respective camera ###############
        self.CAM_NAME_IDX               = 0
        self.CAM_ID_IDX                 = 1
        self.RATIO_WITHOUT_OFFSET_IDX   = 2
        self.RATIO_WITH_OFFSET_IDX      = 3
        self.CSA_WITHOUT_OFFSET_IDX     = 4
        self.CSA_WITH_OFFSET_IDX        = 5
        self.RATIO_OFFSET_IDX           = 6
        self.STEERING_ANGLE_OFFSET_IDX  = 7
        self.RESULT_CAM_TILT_IDX        = 8
        self.RESULT_CAM_ROTATE_IDX      = 9
        self.RATIO_WITH_OFFSET_ACCEPTABLE_IDX       = 10
        self.CSA_WITH_OFFSET_ACCEPTABLE_IDX         = 11
        #####################################################################
        
        ######## generate cam row to add data #############
        self.FrontCamRow = ["FrontCam" if i == 0  else None for i in range(len(self.table_field_names))]
        self.RightCamRow = ["RightCam" if i == 0  else None for i in range(len(self.table_field_names))]
        self.LeftCamRow  = ["LeftCam"  if i == 0  else None for i in range(len(self.table_field_names))]
        
    def update_table(self):
        self.table.add_row(self.FrontCamRow)
        self.table.add_row(self.RightCamRow)
        self.table.add_row(self.LeftCamRow)
        
        print(self.table)
        
if __name__ == "__main__":
    
    obj = CamCalibResultTable()
    obj.print_cam_result()