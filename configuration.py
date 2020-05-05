import json

class DetectionConfig:
    def __init__(self):
        self.diagnosticsPort = 5000
        self.contrast = 0
        self.brightness = 0
        self.minThreshold = 30
        self.maxThreshold = 60
        self.showEnhanced = "original"
        self.channel = 2
        self.blur = 5
        self.hue_L = -16
        self.saturation_L = -7
        self.value_L = 2
        self.hue_H = 185
        self.saturation_H = 165
        self.value_H = 245
        self.withContours = True
        self.boxThickness = 1
        self.fontScale = 1
        self.surf_red_percent = 7.0
        self.surf_hue_L = 5
        self.surf_saturation_L = 5
        self.surf_value_L = 69
        self.surf_hue_H = 80
        self.surf_saturation_H = 255
        self.surf_value_H = 255
        self.modelPath = None

        # List of the strings that is used to add correct label for each box.
        self.labelsPath = None

        # Number of classes to detect
        self.num_classes = 2
        self.min_score = 0.7
        self.real_width = 10.0
        self.real_height = 10.0
        self.videoFile = None
        self.cameraID = None
        self.capRate = 0.02
        self.plcPollTime = 0.01
        self.plcIp = "192.168.0.121"
        self.plcDestNode = 121
        self.plcSrcNode = 25
        self.plcEnabled = False
        self.windowWidth = 1600
        self.regionOfInterest = None
        self.regionOfMeasurement = None

def loadConfig(path):
    config = DetectionConfig()
    jsonFile = open(path,"r")
    jsonDict = json.load(jsonFile)
    config.diagnosticsPort = jsonDict["diagnosticsPort"]
    config.contrast = jsonDict["contrast"]
    config.brightness = jsonDict["brightness"]
    config.minThreshold = jsonDict["minThreshold"]
    config.maxThreshold = jsonDict["maxThreshold"]
    config.showEnhanced = jsonDict["showEnhanced"]
    config.channel = jsonDict["channel"]
    config.blur = jsonDict["blur"]
    config.hue_L = jsonDict["hue_L"]
    config.saturation_L = jsonDict["saturation_L"]
    config.value_L = jsonDict["value_L"]
    config.hue_H = jsonDict["hue_H"]
    config.saturation_H = jsonDict["saturation_H"]
    config.value_H = jsonDict["value_H"]
    config.surf_red_percent = jsonDict["surf_red_percent"]
    config.surf_hue_L = jsonDict["surf_hue_L"]
    config.surf_saturation_L = jsonDict["surf_saturation_L"]
    config.surf_value_L = jsonDict["surf_value_L"]
    config.surf_hue_H = jsonDict["surf_hue_H"]
    config.surf_saturation_H = jsonDict["surf_saturation_H"]
    config.surf_value_H = jsonDict["surf_value_H"]
    config.modelPath = jsonDict["modelPath"]
    config.labelsPath = jsonDict["labelsPath"]
    config.min_score = jsonDict["min_score"]
    config.num_classes = jsonDict["num_classes"]
    config.real_width = jsonDict["real_width"]
    config.real_height = jsonDict["real_height"]
    if "videoFile" in jsonDict:
        config.videoFile = jsonDict["videoFile"]
    if "cameraID" in jsonDict:
        config.cameraID = jsonDict["cameraID"]
    config.capRate = jsonDict["capRate"]
    config.plcPollTime = jsonDict["plcPollTime"]
    config.plcIp = jsonDict["plcIp"]
    config.plcDestNode = jsonDict["plcDestNode"]
    config.plcSrcNode = jsonDict["plcSrcNode"]
    config.plcEnabled = jsonDict["plcEnabled"]
    config.windowWidth = jsonDict["windowWidth"]
    config.regionOfInterest = jsonDict["regionOfInterest"]
    config.regionOfMeasurement = jsonDict["regionOfMeasurement"]
    return config
