# AutoCalibrate script to get camera id , side camera offsets and side camera steering angle

## Command to execute auto calibration
1. default mode (detect camera ids and estimate camera offsets)
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name>

2. skip camera id mapping
    ### if camera id's are already present in CameraStartUpJson.
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name> --skip_camera_id_mapping

3. skip front camera
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name> --skip_front_cam

4. skip camera id mapping and front camera
    * sudo ./AutoCalibrate --videoplayback_build ./<videoplay_back_build_name> --skip_camera_id_mapping --skip_front_cam