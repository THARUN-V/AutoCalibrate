from prettytable import PrettyTable

class CamResult:
    
    def __init__(self):
        
        self.RATIO_WITHOUT_OFFSET = None 
        self.STEERING_ANGLE_WITHOUT_OFFSET = None 
        self.RATIO_WITH_OFFSET = None 
        self.STEERING_ANGLE_WITH_OFFSET = None
        
        self.RATIO_OFFSET = None 
        self.STEERING_OFFSET = None
        
class AutoCalibResult:
    
    def __init__(self):
        
        self.Front = CamResult()
        self.Right = CamResult()
        self.Left = CamResult()
        
    def update_param(self,curr_val,updated_val):
        
        if curr_val == None:
            return updated_val
        return curr_val
        
    def update_result(self,
                      cam,
                      ratio_without_offset = None,
                      csa_without_offset = None,
                      ratio_with_offset = None,
                      csa_with_offset = None ,
                      ratio_offset = None,
                      csa_offset = None):
        """
        This method updates ratio , csa and offset for respective cam.
        """
        if cam == "front":
            self.Front.RATIO_WITHOUT_OFFSET = self.update_param(self.Front.RATIO_WITHOUT_OFFSET,ratio_without_offset)
            self.Front.STEERING_ANGLE_WITHOUT_OFFSET = self.update_param(self.Front.STEERING_ANGLE_WITHOUT_OFFSET,csa_without_offset)
            self.Front.RATIO_WITH_OFFSET = self.update_param(self.Front.RATIO_WITH_OFFSET,ratio_with_offset)
            self.Front.STEERING_ANGLE_WITH_OFFSET = self.update_param(self.Front.STEERING_ANGLE_WITH_OFFSET,csa_with_offset)
            self.Front.RATIO_OFFSET = self.update_param(self.Front.RATIO_OFFSET,ratio_offset)
            self.Front.STEERING_OFFSET = self.update_param(self.Front.STEERING_OFFSET,csa_offset)
        if cam == "right":
            self.Right.RATIO_WITHOUT_OFFSET = self.update_param(self.Right.RATIO_WITHOUT_OFFSET,ratio_without_offset)
            self.Right.STEERING_ANGLE_WITHOUT_OFFSET = self.update_param(self.Right.STEERING_ANGLE_WITHOUT_OFFSET,csa_without_offset)
            self.Right.RATIO_WITH_OFFSET = self.update_param(self.Right.RATIO_WITH_OFFSET,ratio_with_offset)
            self.Right.STEERING_ANGLE_WITH_OFFSET = self.update_param(self.Right.STEERING_ANGLE_WITH_OFFSET,csa_with_offset)
            self.Right.RATIO_OFFSET = self.update_param(self.Right.RATIO_OFFSET,ratio_offset)
            self.Right.STEERING_OFFSET = self.update_param(self.Right.STEERING_OFFSET,csa_offset)
        if cam == "left":
            self.Left.RATIO_WITHOUT_OFFSET = self.update_param(self.Left.RATIO_WITHOUT_OFFSET,ratio_without_offset)
            self.Left.STEERING_ANGLE_WITHOUT_OFFSET = self.update_param(self.Left.STEERING_ANGLE_WITHOUT_OFFSET,csa_without_offset)
            self.Left.RATIO_WITH_OFFSET = self.update_param(self.Left.RATIO_WITH_OFFSET,ratio_with_offset)
            self.Left.STEERING_ANGLE_WITH_OFFSET = self.update_param(self.Left.STEERING_ANGLE_WITH_OFFSET,csa_with_offset)
            self.Left.RATIO_OFFSET = self.update_param(self.Left.RATIO_OFFSET,ratio_offset)
            self.Left.STEERING_OFFSET = self.update_param(self.Left.STEERING_OFFSET,csa_offset)
        
    def print_result(self):
        if self.args.debug_print:
            result_table = PrettyTable()
            
            result_table.field_names = ["CamName","RatioWithoutOffset","CsaWithoutOffset","RatioOffset","CsaOffset","RatioWithOffset","CsaWithOffset"]
            
            result_table.add_row(["Front",self.Front.RATIO_WITHOUT_OFFSET,self.Front.STEERING_ANGLE_WITHOUT_OFFSET,self.Front.RATIO_OFFSET,self.Front.STEERING_OFFSET,self.Front.RATIO_WITH_OFFSET,self.Front.STEERING_ANGLE_WITH_OFFSET])
            result_table.add_row(["Right",self.Right.RATIO_WITHOUT_OFFSET,self.Right.STEERING_ANGLE_WITHOUT_OFFSET,self.Right.RATIO_OFFSET,self.Right.STEERING_OFFSET,self.Right.RATIO_WITH_OFFSET,self.Right.STEERING_ANGLE_WITH_OFFSET])
            result_table.add_row(["Left",self.Left.RATIO_WITHOUT_OFFSET,self.Left.STEERING_ANGLE_WITHOUT_OFFSET,self.Left.RATIO_OFFSET,self.Left.STEERING_OFFSET,self.Left.RATIO_WITH_OFFSET,self.Left.STEERING_ANGLE_WITH_OFFSET])
            
            print(result_table)
        
if __name__ == "__main__":
    
    res = AutoCalibResult()
    res.print_result()