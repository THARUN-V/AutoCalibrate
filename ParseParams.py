import argparse

class ParseParams:
    
    def __init__(self):
        
        parser = argparse.ArgumentParser(description = "Script to automate the calibration.")
        
        parser.add_argument("--json_path",default = None,help = "json file for path to json file for read,modify and updating the params")
        
        self.args = parser.parse_args()