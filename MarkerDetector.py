import cv2 
import numpy 

class ArucoMarkerDetector:
    
    def __init__(self,aruco_dict):
        self.aruco_dict_map = {"DICT_4X4_100"  : cv2.aruco.DICT_4X4_100,
                            "DICT_4X4_1000" : cv2.aruco.DICT_4X4_1000,
                            "DICT_4X4_250"  : cv2.aruco.DICT_4X4_250,
                            "DICT_4X4_50"   : cv2.aruco.DICT_4X4_50,
                            "DICT_5X5_100"  : cv2.aruco.DICT_5X5_100,
                            "DICT_5X5_1000" : cv2.aruco.DICT_5X5_1000,
                            "DICT_5X5_250"  : cv2.aruco.DICT_5X5_250, 
                            "DICT_5X5_50"   : cv2.aruco.DICT_5X5_50,  
                            "DICT_6X6_100"  : cv2.aruco.DICT_6X6_100, 
                            "DICT_6X6_1000" : cv2.aruco.DICT_6X6_1000,
                            "DICT_6X6_250"  : cv2.aruco.DICT_6X6_250,   
                            "DICT_6X6_50"   : cv2.aruco.DICT_6X6_50,  
                            "DICT_7X7_100"  : cv2.aruco.DICT_7X7_100, 
                            "DICT_7X7_1000" : cv2.aruco.DICT_7X7_1000,
                            "DICT_7X7_250"  : cv2.aruco.DICT_7X7_250, 
                            "DICT_7X7_50"   : cv2.aruco.DICT_7X7_50, 
                            "DICT_APRILTAG_16H5" :  cv2.aruco.DICT_APRILTAG_16H5,
                            "DICT_APRILTAG_16h5" :  cv2.aruco.DICT_APRILTAG_16h5,
                            "DICT_APRILTAG_25H9" :  cv2.aruco.DICT_APRILTAG_25H9,
                            "DICT_APRILTAG_25h9" :  cv2.aruco.DICT_APRILTAG_25h9,
                            "DICT_APRILTAG_36H10":  cv2.aruco.DICT_APRILTAG_36H10, 
                            "DICT_APRILTAG_36H11":  cv2.aruco.DICT_APRILTAG_36H11,
                            "DICT_APRILTAG_36h10":  cv2.aruco.DICT_APRILTAG_36h10,
                            "DICT_APRILTAG_36h11":  cv2.aruco.DICT_APRILTAG_36h11,
                            "DICT_ARUCO_ORIGINAL":  cv2.aruco.DICT_ARUCO_ORIGINAL }
        
        # Define the dictionary used for ArUco markers
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dict_map[aruco_dict])
        self.aruco_params = cv2.aruco.DetectorParameters()
        
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict,self.aruco_params)
    
    def get_marker_id(self,img):
        
        img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        corners,ids,rejected_img_points = self.aruco_detector.detectMarkers(img_gray)
        
        # Draw detected markers
        annotated_image = cv2.aruco.drawDetectedMarkers(img.copy(),corners,ids)
        
        return corners , ids , rejected_img_points , annotated_image