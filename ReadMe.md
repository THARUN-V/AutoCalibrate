# AutoCalibrate script to get camera id , side camera offsets and side camera steering angle

## Command to execute auto calibration
1. default mode (detect camera ids and estimate camera offsets)
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name>

2. skip camera id mapping
    ### if camera id's are already present in CameraStartUpJson.
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name> --skip_camera_id_mapping