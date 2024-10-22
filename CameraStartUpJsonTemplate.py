CameraStartUpJsonTemplate = {
            "Header": [
                {
                "BOT_ID": "Bot1",
                "Config_TimeStamp": 1671189765.5046573
                }
            ],
            "CamParams": [
                {
                "serial_port": "/dev/ttyAMA0",
                "BotType": 0,
                "rightSideCameraOffset": 0,
                "leftSideCameraOffset": 0,
                "EnableHostRatioBasedRejection": 0,
                "EnableBlankFactorBasedMasking": 0,
                "FrontCameraOffsetDistance": 54,
                "SideCameraOffsetDistance": 0,
                "LaneColourToScan": 0,
                "frontCameraId": "",
                "rightCameraId": "",
                "leftCameraId": "",
                "connectedCameraFlag":[1,1,1],
                "leftSideSteeringOffset":0,
                "rightSideSteeringOffset":0,
                "frontSideSteeringOffset":0
                }
            ],
            "DebugParams": [
                {
                "HostCommnFlag": 0,
                "HybridSwitch": False,
                "SelectCameraForOfflineMode" : 1,
                "PathWidth": 0,
                "ShowImageDebug": 0,
                "ShowImageRelease": 0,
                "LogImageDebug": 0,
                "LogImageFrameRatioDiffMin": 0.08,
                "TARGET_FPS":10,

                "EnableGrouping":0,
                "GroupingThreshold": 20,
                "GroupingNumberOfLinesWeight":0.2,
                "GroupingDistanceWeight":-0.6,
                "GroupingSumOfLengths":0.2,
                "VisualizeBestGroup":0
                }
            ]
}
